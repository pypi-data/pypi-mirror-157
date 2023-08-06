import numpy as np
import os,json,sys
from typing import Dict, Sequence, Type, Callable, List, Optional
import torch
from torch import nn
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from modules.transformers import BertModel,BertConfig,BertTokenizer
from modules.MLP import MLP
from log import logging
logger=logging.getLogger(__name__)

'''
BertModel inherite BertForPretrainedModel inherite PreTrainedModel

In PreTrainedModel
@classmethod
def from_pretrained(cls,pretrained_model_name_or_path,*model_args,**kwargs):
    config=kwargs.pop('config',None)
    state_dict=kwargs.pop('state_dict',None)

    #The config will be loaded from pretrained_model_name_or_path/config.json if config not provided
    #instantiate model
    model=cls(config)
    if state_dict is None:
        state_dict=torch.load(pretrained_model_name_or_path/pytorch_model.bin,map_location='cpu')#也就是说模型最开始是加载到cpu上的
    missing_keys,unexpected_keys,error_msgs=[],[],[]

    def load(module: nn.Module, prefix=''):
        module._load_from_state_dict(state_dict,prefix,missing_keys,unexpected_keys,error_msgs)
        for name,child in module._modules.items():
            if child:
                load(child,prefix+name+'.')
    
    load(model,prefix='' if hasattr(model,'bert') else 'bert.')
    #prefix用来解决加载不同模型保存的pytorch_model.bin出现的keys不匹配问题
    if len(missing_keys) > 0:
        logger.info("Weights of {} not initialized from pretrained model: {}".format(
            model.__class__.__name__, missing_keys))
    if len(unexpected_keys) > 0:
        logger.info("Weights from pretrained model not used in {}: {}".format(
            model.__class__.__name__, unexpected_keys))
    return model
'''

class ClsHead(nn.Module):
    '''
    ClsHead不区分是单句子还是双句子，因为处理逻辑是一样的
    '''
    def __init__(self, model_path,
                num_labels,
                state_dict=None,
                is_finetune=False,
                pooling_type='cls'):
        super().__init__()
        self.num_labels=num_labels
        self.pooling_type=pooling_type
        if is_finetune==False:
            logger.info("Loading model from {}, which is from huggingface model".format(model_path))
            self.load_huggingface_model(bert_model_path=model_path)
        else:
            self.load_finetuned_model(model_path=model_path)
            logger.info("Loading model from {}, which has been finetuned.".format(model_path))

        # bert_model_path=os.path.join(model_path,"BERT")#save的时候将BERT保存在model_path下的BERT文件夹中
        # self.config=BertConfig.from_pretrained(bert_model_path)
        # self.bert=BertModel.from_pretrained(bert_model_path)
        # self.tokenizer=BertTokenizer.from_pretrained(bert_model_path)

    def load_huggingface_model(self,bert_model_path):
        self.config=BertConfig.from_pretrained(bert_model_path)
        self.bert=BertModel.from_pretrained(bert_model_path)
        self.tokenizer=BertTokenizer.from_pretrained(bert_model_path)
        self.head_layer=MLP(in_features=self.config.hidden_size,out_features=self.num_labels)

    def load_finetuned_model(self,model_path):
        bert_save_path=os.path.join(model_path,"BERT")#save的时候将BERT保存在model_path下的BERT文件夹中
        self.config=BertConfig.from_pretrained(bert_save_path)
        self.bert=BertModel.from_pretrained(bert_save_path)
        self.tokenizer=BertTokenizer.from_pretrained(bert_save_path)

        head_save_path=os.path.join(model_path,'MLP')
        self.head_layer=MLP.load(input_path=head_save_path)

    def save(self,output_path):
        bert_save_path=os.path.join(output_path,"BERT")
        self.bert.save_pretrained(bert_save_path,save_config=False)#下面已经save，不用save两次，虽然没什么影响
        self.config.save_pretrained(bert_save_path)
        self.tokenizer.save_pretrained(bert_save_path)
        head_save_path=os.path.join(output_path,'MLP')
        self.head_layer.save(head_save_path)
    
    def forward(self,input_ids,attention_mask=None,token_type_ids=None,label_ids=None,output_all_encoded_layers=False,embedding_for_adv=None):
        '''
        input_ids.size()==attention_mask.size()==token_type_ids.size()==position_ids.size()==
        (batch_size,seq_length)
        label_ids.size()==(batch_size,)
        如果不输出所有中间层的hidden_states，那么sequence_outputs就是tensor而不是list
        否则sequence_outputs就是长度为层数的list
        '''
        (sequence_outputs,pooled_output)=self.bert(input_ids=input_ids,
                                                  token_type_ids=token_type_ids,
                                                   attention_mask=attention_mask,
                                                   output_all_encoded_layers=output_all_encoded_layers,
                                                   embedding_for_adv=embedding_for_adv)
        #要注意到sequence_output[0]与pooled_output的区别在于pooled_output是经过一层tanh的
        assert len(pooled_output.size())==2 and pooled_output.size(1)==self.config.hidden_size

        if self.pooling_type=='cls':
            before_logits=pooled_output
        elif self.pooling_type=='last_layer':
            #取最后一层的mean pooling
            if output_all_encoded_layers==True:
                assert type(sequence_outputs)==list
                sequence_outputs=sequence_outputs[-1]
            #sequence_outputs现在代表last layer的hidden_states
            attention_mask_expanded=attention_mask.unsqueeze(-1).expand(sequence_outputs.size())
            #sequence_outputs.size()==(bsz,pad_seq_len,dim)==attention_mask_expanded.size()

            sum_mask=attention_mask.sum(1).unsqueeze(1)#(batch_size,1)
            sum_mask=torch.clamp(sum_mask,min=1e-7)
            before_logits=torch.sum(sequence_outputs*attention_mask_expanded,1)/sum_mask#(bsz,seq_len,dim)-->(bsz,dim)
        elif self.pooling_type=='last_two_layer':
            #print(output_all_encoded_layers,type(sequence_outputs))
            assert output_all_encoded_layers==True and type(sequence_outputs)==list
            attention_mask_expanded=attention_mask.unsqueeze(-1).expand(sequence_outputs[-1].size())
            #sequence_outputs.size()==(bsz,pad_seq_len,dim)==attention_mask_expanded.size()
            sum_mask=attention_mask.sum(1).unsqueeze(1)#(batch_size,1)
            sum_mask=torch.clamp(sum_mask,min=1e-7)
            #print(sequence_outputs[-1].size(),attention_mask_expanded.size())
            last_1_pooling=torch.sum(sequence_outputs[-1]*attention_mask_expanded,1)/sum_mask
            last_2_pooling=torch.sum(sequence_outputs[-2]*attention_mask_expanded,1)/sum_mask

            before_logits=(last_1_pooling+last_2_pooling)/2
        
        else:
            raise Exception("Unknown pooling type %s error"%self.pooling_type)
        
        logits=self.head_layer(before_logits)#(batch_size,num_labels)
        return logits
        # predictions=torch.argmax(logits,dim=1)
        # if label_ids is not None:
        #     loss=nn.CrossEntropyLoss(reduction="mean")(input=logits,target=label_ids)
        #     accuracy=(predictions==label_ids).float().mean()
        #     return loss,accuracy
        # else:
        #     return logits,predictions