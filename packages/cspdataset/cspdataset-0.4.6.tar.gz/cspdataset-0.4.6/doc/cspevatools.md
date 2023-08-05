# 图像识别-目标检测评估工具

基于漏检率、错检率的目标检测评估工具

可生成badcase，badcase可以生成拼接的图像或voc格式的xml

### 一、目录说明

```
|--README.md----------------# 简介
|--eva------------------# 数据(过程数据、历史评估)    
	|--det-------------------# 评估方案、评估脚本  
		|--utils----------------# 模型(推理脚本、baseline)   
			|--options-----------------# 参数配置
			|--util-----------------# 操作工具包括 iou、漏检率、错检率计算、格式转换等
			|--voc_xml-----------------# 独立操作公司标准数据集向coco评估数据集转换
		|--eva----------------# 脚本主工程
```

### 二、文件格式说明（待评估json文件）

```
[
    {
        "image_id": 1,                         # 随机生成
        "category": "No_helmet",			   # 标签名称
        "filename": "SANY吊车_29_33.jpg",       # 图片文件名称
        "bndbox": {                            # 预测框
            "xmin": "519",
            "ymin": "291",
            "xmax": "536",
            "ymax": "307"
        },
        "score": 0.8106697797775269             # 预测后的分数
    },
    ...
 ]
```

### 三、参数说明

- -e：选择评估类型默认目标检测[det]
- -s：目标检测待评估的json文件

- -t：测试集标注数据的JSON文件，该文件为coco格式的文件，可以使用dataset的转换工具将voc转换为coco
- -o：测试集图片文件路径
- -i：输出badcase混合图片文件存储路径（允许不传，不传即不生成）
- -v：输出badcase的voc格式xml文件存储路径（允许不传，不传即不生成）

### 四、使用案例

- 指定待评估的json文件为test.json
- 指定测试集标注的json文件为 test_pred_simple.json
- 指定测试集图片文件路径为 /data/test/images

```
evatools -e det  -s test_pred_simple.json -t test.json -o /data/test/images  -i badcase_img  -v badcase_voc
```

### FAQ

- 评估工具接收标准的coco数据格式的标注数据，可以通过datatools将voc转换为coco格式的数据
- 评估工具可以指定输出的数据格式包括图像和voc格式的xml，不设置参数即不输出
- 评估日志在执行目录logs下，以日期分割
