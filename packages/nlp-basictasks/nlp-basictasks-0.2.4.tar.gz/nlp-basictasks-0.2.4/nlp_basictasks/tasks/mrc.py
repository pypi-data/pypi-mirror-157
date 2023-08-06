import json
import numpy as np
import os,sys
from typing import Dict, Sequence, Type, Callable, List, Optional
from tqdm import tqdm

import torch
from torch import nn
from torch.utils.data import DataLoader
from tqdm.autonotebook import tqdm, trange
from tensorboardX import SummaryWriter
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
#print(sys.path)
from heads import MrcHead
from log import logging

from readers.mrc import convert_examples_to_features
from modules.utils import get_optimizer,get_scheduler
from .utils import batch_to_device

logger=logging.getLogger(__name__)

class mrc():
    '''
    '''
    def __init__(self,model_path,
                max_seq_length:int = 500,
                device:str = None,
                state_dict=None,
                is_finetune=False,
                tensorboard_logdir = None,
                do_FGV=False):

        self.do_FGV=do_FGV
        self.max_seq_lenth=max_seq_length
        logger.info("Doing attack traing : {}".format(do_FGV))
        self.model=MrcHead(model_path=model_path,
                            state_dict=state_dict,
                            is_finetune=is_finetune)
        if tensorboard_logdir!=None:
            os.makedirs(tensorboard_logdir,exist_ok=True)
            self.tensorboard_writer=SummaryWriter(tensorboard_logdir)
        else:
            self.tensorboard_writer=None

        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        logging.info("Use pytorch device: {}".format(device))
        self._target_device = torch.device(device)
        self.model.to(self._target_device)

    def smart_batching_collate(self,batch_examples,is_training=True):
        '''
        传进来的batch_examples每一个example.__dict__.keys()==['guid','question','context','context_tokens','answer','start_position','end_position']
        '''
        batch_features=convert_examples_to_features(examples=batch_examples,
                                                    tokenizer=self.model.tokenizer,
                                                    max_seq_length=self.max_seq_lenth,
                                                    is_training=is_training)
        batch_features_={"input_ids":[],'token_type_ids':[],"attention_mask":[],'start_positions':[],'end_positions':[]}
        for feature in batch_features:
            batch_features_['input_ids'].append(feature.input_ids)
            batch_features_['token_type_ids'].append(feature.token_type_ids)
            batch_features_['attention_mask'].append(feature.input_mask)
            batch_features_["start_positions"].append(feature.start_position)
            batch_features_["end_positions"].append(feature.end_position)
        
        batch_features_={key:torch.LongTensor(value) for key,value in batch_features_.items()}
        return batch_features_

    def getLoss(self,features,loss_fct,eps=1e-10,noise_coeff=0.01):
        '''
        '''
        input_ids=features['input_ids']
        token_type_ids=features['token_type_ids']
        attention_mask=features['attention_mask']
        start_positions=features['start_positions']
        end_positions=features['end_positions']
        start_end_logits=self.model(input_ids=input_ids,
                        attention_mask=attention_mask,
                        token_type_ids=token_type_ids,
                        output_all_encoded_layers=features['output_all_encoded_layers'])
        
        start_logits,end_logits=start_end_logits.split(1,dim=-1)#2 batch_size,seq_len,1
        start_logits=start_logits.squeeze(-1)
        end_logits=end_logits.squeeze(-1)
        # 2 (batch_size,seq_len)
        assert start_positions.dim()==end_positions.dim()<start_logits.dim()
        ignore_index=start_logits.size(1)#对于长度超出给定目标的长度，忽略
        start_positions.clamp_(0,ignore_index)
        end_positions.clamp_(0,ignore_index)
        start_loss=loss_fct(start_logits,start_positions)
        end_loss=loss_fct(end_logits,end_positions)
        loss=(start_loss+end_loss)/2
        return loss

    def fit(self,
            train_dataloader,
            evaluator = None,
            epochs: int = 1,
            loss_fct = nn.CrossEntropyLoss(),
            scheduler: str = 'WarmupLinear',
            warmup_proportion: float = 0.1,
            optimizer_type = 'AdamW',
            optimizer_params: Dict[str, object] = {'lr': 2e-5},
            weight_decay: float = 0.01,
            evaluation_steps = None,
            output_path: str = None,
            save_best_model: bool = True,
            max_grad_norm: float = 1,
            use_amp: bool = False,
            callback: Callable[[float, int, int], None] = None,
            show_progress_bar: bool = True,
            early_stop_patience = 10,
            print_loss_step: Optional[int] = None,
            output_all_encoded_layers: bool = False
            ):

        train_dataloader.collate_fn=self.smart_batching_collate

        if print_loss_step==None:
            print_loss_step=len(train_dataloader)//5
        if evaluator is not None and evaluation_steps==None:
            evaluation_steps=len(train_dataloader)//2
        #一个epoch下打印5次loss，评估2次
        logger.info("一个epoch 下，每隔{}个step会输出一次loss，每隔{}个step会评估一次模型".format(print_loss_step,evaluation_steps))
        if use_amp:
            from torch.cuda.amp import autocast
            scaler = torch.cuda.amp.GradScaler()

        self.model.to(self._target_device)#map_location='cpu'

        if output_path is not None:
            os.makedirs(output_path, exist_ok=True)

        self.best_score = -9999999
        num_train_steps = int(len(train_dataloader) * epochs)
        warmup_steps = num_train_steps*warmup_proportion

        optimizer = get_optimizer(model=self.model,optimizer_type=optimizer_type,weight_decay=weight_decay,optimizer_params=optimizer_params)
        scheduler = get_scheduler(optimizer, scheduler=scheduler, warmup_steps=warmup_steps, t_total=num_train_steps)

        global_step=0
        skip_scheduler = False
        patience = early_stop_patience        
        for epoch in trange(epochs, desc="Epoch", disable=not show_progress_bar):
            training_steps=0
            training_loss=0.0

            self.model.zero_grad()
            self.model.train()

            for train_step,features in tqdm(enumerate(train_dataloader)):
                features=batch_to_device(features,target_device=self._target_device)
                features['output_all_encoded_layers']=output_all_encoded_layers
                #print(features.keys(),features["input_ids"].size())
                if use_amp:
                    with autocast():
                        loss_value=self.getLoss(features=features,loss_fct=loss_fct)

                    scale_before_step = scaler.get_scale()
                    scaler.scale(loss_value).backward()
                    scaler.unscale_(optimizer)
                    torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_grad_norm)
                    scaler.step(optimizer)
                    scaler.update()

                    skip_scheduler = scaler.get_scale() != scale_before_step
                else:
                    loss_value=self.getLoss(features=features,loss_fct=loss_fct)
                    training_loss+=loss_value.item()
                    if print_loss_step!=None and train_step>0 and train_step%print_loss_step == 0:
                        training_loss/=print_loss_step
                        logging.info("Epoch : {}, train_step : {}/{}, loss_value : {} ".format(epoch,train_step*(epoch+1),num_train_steps,training_loss))
                        training_loss=0.0
                    if self.tensorboard_writer is not None:
                        self.tensorboard_writer.add_scalar(f"train_loss",loss_value.item(),global_step=global_step)
                    loss_value.backward()
                    torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_grad_norm)
                    optimizer.step()

                optimizer.zero_grad()
                if not skip_scheduler:
                    scheduler.step()

                training_steps += 1
                global_step += 1

                if evaluator is not None and evaluation_steps>0 and (train_step) % evaluation_steps == 0 :
                    eval_score=self._eval_during_training(evaluator, output_path, epoch, training_steps, callback)
                    if self.tensorboard_writer is not None:
                        self.tensorboard_writer.add_scalar(f"eval_score",float(eval_score),global_step=global_step)
                    if eval_score > self.best_score:
                        if save_best_model:
                            self.model.save(output_path=output_path)
                            logging.info(("In epoch {}, training_step {}, the eval score is {}, previous eval score is {}, model has been saved in {}".format(epoch,train_step*(epoch+1),eval_score,self.best_score,output_path)))
                            self.best_score=eval_score
                    else:
                        patience-=1
                        logging.info(f"No improvement over previous best eval score ({eval_score:.6f} vs {self.best_score:.6f}), patience = {patience}")
                        if patience==0:
                            logging.info("Run our of patience, early stop!")
                            return
                
                    self.model.zero_grad()
                    self.model.train()

    def _eval_during_training(self, evaluator, output_path,  epoch, steps, callback):
        if evaluator is not None:
            score_and_auc = evaluator(self, label2id=self.label2id, output_path=output_path, epoch=epoch, steps=steps)
            if callback is not None:
                callback(score_and_auc, epoch, steps)
            return score_and_auc
        return None

    def predict(self,
                is_pairs,
                dataloader,
                batch_size:int=32,
                num_workers: int = 0,
                convert_to_numpy: bool = True,
                convert_to_tensor: bool = False,
                output_all_encoded_layers = False,
                show_progress_bar=False):
        if self.pooling_type not in ['cls','last_layer']:
            output_all_encoded_layers=True

        if isinstance(dataloader,list):
            #传进来的dataloader是一个List
            dataloader=DataLoader(dataloader,batch_size=batch_size,num_workers=num_workers,shuffle=False)
        if is_pairs==False:
            logger.info('当前是单句子分类任务预测')
            dataloader.collate_fn=self.smart_batching_collate_of_single
        else:
            logger.info("当前是双句子分类任务预测")
            dataloader.collate_fn=self.smart_batching_collate_of_pair
        
        predictions=[]
        self.model.eval()#不仅仅是bert_model
        self.model.to(self._target_device)
        with torch.no_grad():
            for _ in trange(1, desc="Evaluating", disable=not show_progress_bar):
                for features,_ in tqdm(dataloader):
                    features['output_all_encoded_layers']=output_all_encoded_layers
                    features=batch_to_device(features,self._target_device)
                    logits=self.model(**features)
                    probs=torch.nn.functional.softmax(logits,dim=1)#(batch_size,num_labels)
                    predictions.extend(probs)
        if convert_to_tensor:
            predictions=torch.stack(predictions)#(num_eval_examples,num_classes)
        
        elif convert_to_numpy:
            predictions=np.asarray([predict.cpu().detach().numpy() for predict in predictions])

        return predictions#(num_eval_examples,num_classes)