# 一、工具说明
- 处理 COCO, VOC 格式的数据集
- 包含数据集互转、切分、检查



# 二、数据集格式说明
## voc格式
VOC  
|  
|---------Annotations  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|-------xxx.xml  
|  
|---------ImageSets  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|-------Main  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|-------trainval.txt   
|---------JPEGImages  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|-------xxx.jpg  
|  
|---------labels.txt  
注：图片文件名与对应标注数据xml文件文件名相同  
​

## coco格式
COCO  
|  
|---------Annotations  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|-------train.json  
|  
|-------train  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|-------xxx.jpg
​

# 三、使用说明
## 1. pip 安装
> pip install cspdataset

## 2. 命令行式使用
> datatools COMMAND
> 使用帮助
> datatools --help

> 脚本调用
> import datatools

## 3. 参数说明
> usage: datatools.py [-h]   
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--form {coco,COCO,VOC,voc}  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--data_dir DATA_DIR  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[--split]  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[--division_ratio DIVISION_RATIO [DIVISION_RATIO ...]]  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[--transform]  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[--output_transform OUTPUT_TRANSFORM]  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[--check]  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[--output_check OUTPUT_CHECK]  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[--labelfile LABELFILE] [--eva EVA]  



> tools for voc/coco dataset  
optional arguments:  
-h, --help                                           show this help message and exit  
--form {coco,COCO,VOC,voc}             the form of the dataset  
--data_dir DATA_DIR                           the dir of the dataset  
--split                                                  Set a switch to split  
--division_ratio DIVISION_RATIO [DIVISION_RATIO ...] data segmentation ratio  
--transform                                          Set a switch to transform  
--output_transform OUTPUT_TRANSFORM    dir for output  
--check                                                 Set a switch to check  
--output_check OUTPUT_CHECK           dir for output  
--labelfile LABELFILE                              the labels.txt from the platform  

## 4. 示例

- 数据集转化
> datatools --transform --form voc --data_dir /your/voc/folder --output_transform /the/folder/tosave/coco

- 数据集切分
> datatools --split --form voc --data_dir /your/voc/folder --division_ratio 0.9 0.8  
> 0.9 训练集占总数据集比例，0.1用作训练后的模型评估  
> 0.8 训练集中用于训练的比例，0.2用于训练过程中的评估  

- 数据集检查
> datatools --check --form voc --data_dir /your/voc/folder --labelfile /the/label.txt --output_check /the/folder/tosave/check/result  

## 5. 补充说明
> 数据集检查  
> 包括对原始图片、标注数据（xml或json文件）的检查  
> 图片：图像是否损坏，无法加载  
> 标注文件：没有图片尺寸；图片尺寸为0；类别错误；坐标越界；没有标注坐标；坐标信息为负数；标注文件无坐标信息（缺bbox）  
> 输出：包含错误文件文件名的 .txt 文件  

> 数据集切分    
> voc格式：在VOC/ImageSets/Main 生成 trainval.txt、train.txt、val.txt、test.txt，分别为训练数据集、训练数据集中用作训练部分、训练数据集中用作评估部分、测试数据集。内容为图片文件名    
> cooc格式：在coco/Annotations/生成 trainval.json、train.json、val.json、test.json，在coco/Images目录下生成存放应图片文件的trainval、train、val、test文件夹      
> 对待切分 coco 数据集，需保证该数据集中只存在 Annotation、train 两个文件夹，暂不支持存在多个图片文件夹（如同时存在test、train 图片文件夹，则只会基于 train 作切分）    

