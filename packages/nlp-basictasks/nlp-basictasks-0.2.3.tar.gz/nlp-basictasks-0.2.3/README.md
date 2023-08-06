# nlp-basictasks

nlp-basictasks是利用[PyTorch](https://pytorch.org/get-started/locally/)深度学习框架所构建一个简单的库，旨在快速搭建模型完成一些基础的NLP任务，如分类、匹配、序列标注、语义相似度计算等。



## 整体架构

![image](https://user-images.githubusercontent.com/89245998/130556405-b8cd394c-434a-415e-b048-3e352fa413a1.png)

如上图，整体架构分为三个大模块：

1. readers负责读取数据，不同的任务在readers中有不同的数据处理形式。不同任务的数据后处理代码也放在readers中。
2. modules代表编码器，用来提取文本特征，主要包括BERT、LSTM、MLP。
3. tasks根据任务的不同有相应的处理方式。（**和readers中相应的数据处理方式对应**）

## 安装

```bash
pip install --index-url https://pypi.org/project/ nlp-basictasks==0.2.2
```

or

```bash
git clone https://github.com/xianghuisun/nlp-basictasks.git
cd nlp-basictasks & python setup.py install
```



## 使用

[notebooks](https://github.com/xianghuisun/nlp-basictasks/tree/main/docs/notebooks)中展示了用nlp-basictasks框架快速实现五个NLP常见任务，具体见：

- [实体识别](https://github.com/xianghuisun/nlp-basictasks/blob/main/docs/notebooks/ner.ipynb)
- [语义相似度计算](https://github.com/xianghuisun/nlp-basictasks/blob/main/docs/notebooks/sts.ipynb)
- [文本分类](https://github.com/xianghuisun/nlp-basictasks/blob/main/docs/notebooks/text_classification.ipynb)
- [文本匹配](https://github.com/xianghuisun/nlp-basictasks/blob/main/docs/notebooks/text_match.ipynb)
- [问答检索](https://github.com/xianghuisun/nlp-basictasks/blob/main/docs/notebooks/qa_system.ipynb)


## 参考
- [PALM](https://github.com/PaddlePaddle/PALM)
- [pytorch-crf](https://github.com/kmkurn/pytorch-crf)
- [Faiss](https://github.com/facebookresearch/faiss)
- [sentence-transformers](https://github.com/UKPLab/sentence-transformers)
- [transformers](https://github.com/huggingface/transformers)




