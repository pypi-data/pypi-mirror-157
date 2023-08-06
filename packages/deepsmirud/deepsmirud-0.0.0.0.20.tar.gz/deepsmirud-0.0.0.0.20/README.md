# DeepsmirUD
![](https://img.shields.io/badge/deepsmirud-executable-519dd9.svg)
![](https://img.shields.io/badge/last_released-June._2022-green.svg)
![](https://img.shields.io/github/stars/2003100127/deepsmirud?logo=GitHub&color=blue)
![](https://img.shields.io/pypi/v/deepsmirud?logo=PyPI)
[![Downloads](https://pepy.tech/badge/deepsmirud)](https://pepy.tech/project/deepsmirud)
[![Downloads](https://pepy.tech/badge/deepsmirud/month)](https://pepy.tech/project/deepsmirud)
[![Downloads](https://pepy.tech/badge/deepsmirud/week)](https://pepy.tech/project/deepsmirud)

###### tags: `DeepsmirUD` `miRNA` `drugs` `gene regulation`


## Overview
```angular2html
 ____                                _      _   _ ____
|  _ \  ___  ___ _ __  ___ _ __ ___ (_)_ __| | | |  _ \
| | | |/ _ \/ _ \ '_ \/ __| '_ ` _ \| | '__| | | | | | |
| |_| |  __/  __/ |_) \__ \ | | | | | | |  | |_| | |_| |
|____/ \___|\___| .__/|___/_| |_| |_|_|_|   \___/|____/
                |_|
```
This repository is a standalone package of the DeepsmirUD method. DeepsmirUD is used to predict small molecule-mediated regulatory effects on miRNA expression. This method is powered by 12 cutting-edged deep learning models.

## Installation
```angular2html
pip install deepsmirud
```

## Overview
```angular2html
deepsmirud [-h]
           --method m
           --smile_fpn sm
           --fasta_fpn mir
           --model_fp mf
           --output_path o

argument details:
    -h, --help            show this help message and exit
    -m, --method,
            A deep learning method. It can be any below.
            AlexNet | BiRNN | RNN | Seq2Seq |
            CNN | ConvMixer64 | DSConv | LSTMCNN |
            MobileNet | ResNet18 | ResNet50 | SEResNet |


    -sm, --smile_fpn, a small molecule file that contains only smile strings


    -mir, --fasta_fpn, a miRNA fasta file


    -mf, --model_fp, a model path


    -o, --output_path, outputting deepsmirud predictions
```

## Usage
### Download models
```shell
deepsmirud_download -o /the/path/you/prefer/model.zip
```

```
# output messages
downloading...
downloaded!
```
Please use `-mf` of `deepsmirud` then to access to where the models are located.

### Input format
Two example files in DeepsmirUD are 5757.txt and MIMAT0000066.fasta for a small molecule and a miRNA molecule.

* #### Estradiol (small molecule)

![estradiol](https://github.com/2003100127/deepsmirud/blob/main/img/Estradiol.png?raw=true)
```shell
# 5757.txt
C[C@]12CC[C@H]3[C@H]([C@@H]1CC[C@@H]2O)CCC4=C3C=CC(=C4)O
```

* #### hsa-let-7e-5p (miRNA)
```
# MIMAT0000066.fasta
>hsa-let-7e-5p MIMAT0000066
UGAGGUAGGAGGUUGUAUAGUU
```

### Inference
Use two example files in DeepsmirUD. The LSTMCNN model is recommanded to use in your studies.
```shell
deepsmirud -m LSTMCNN -sm deepsmirud/data/example/5757.txt -mir deepsmirud/data/example/MIMAT0000066.fasta -mf /the/path/you/prefer/model/lstmcnn -o ./out.deepsmirud
```

## Citation
Please cite our work if you use DeepsmirUD in your research.

## Contact
If you have any question, please contact [Jianfeng Sun](jianfeng.sunmt@gmail.com). We highly recommend creating issue pages when you have problems. Your issues will be responded then.