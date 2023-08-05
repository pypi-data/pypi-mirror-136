# augtools 工具说明

# 1 工具简介

augtools   
图片增强工具，包含在 cspdataset 库中，可通过 pip 安装，命令行的形式调用  
可以对 VOC 格式目标检测数据集进行数据增强  
增强包括生成新的图片及对应 xml 文件  
生成的文件位于源文件夹相同位置，并以 imgaug_ 为前缀   


# 2 安装 cspdataset 包


```python
! pip install cspdataset
```

# 3 下载示例 VOC 数据集


```python
! wget 
```

## 3.1 数据集示例

VOC  
|------JPEGImages  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|----------1.jpg  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|----------1.jpg  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|----------xxx.jpg  
|------Annotations  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|----------1.xml  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|----------1.xml  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|----------xxx.xml  
       
JPEGImages：图片文件夹  
Annotations：标注文件夹  

# 4 命令调用

## 4.1 命令行帮助说明


```python
! augtools -h
```

## 4.2 调用示例


```python
! augtools -f aug.yml -i your/datasets/
```

# 4.3参数说明

-h 查看命令说明  
-f 数据增强配置文件（.yml文件）  
-i 数据集地址  

# 5 数据增强配置文件说明

- 数据增强操作内部调用的是 imgaug
- 配置文件中增强方法参数即对应 imgaug 中的相应 API
- 除 imgaug 中的增强方法外，还支持背景图片切换
- 示例文件见 ./aug.yml  
- 提供两种增强方式
> 方式一. 对每张图片轮流使用配置的增强方法，分别生成新的图片和 xml 文件  
> 方式二. 对每张图片顺序执行配置的增强方法，生成新的图片及 xml 文件  
- basci 为通用配置项，两种方式都需要配置
- 方式一支持在配置的方法中随机选择一种增强（random：true），或执行所有增强方法
- 使用方式一，直接在配置文件中输入 key: value 式参数对进行方法配置
- 使用方式二，在标志符参数 Sequential 下层配置增强方法，下层的配置方式同方式一
- 两种方式支持的增强方法相同，实际使用时，只能选择其中的一种方式增强，配置方法也只能选择一种  
- 是否启用某种增强方法，可通过注释和取消对应注释的方式实现    
- 各参数详细说明  

***aug.yml***    

***基础配置项***   
basic:                
&nbsp;&nbsp;  aug_times: 2       # 增强方法作用次数  
&nbsp;&nbsp;  random: false      # 对于方式一，是否随机采取一种方式增强    
&nbsp;&nbsp;  thread_num: false    # 是否采用多线程  


***增强方式一配置***  
bg_changed:                                  # 背景替换，每次从文件夹中随机抽取一张作为替换背景  
&nbsp;&nbsp;  bg_path: "D:/document/pycharmpro/data_aug/data/bg_imgs"   # 待替换用背景图片文件夹  

Fliplr: 0.5                          # 水平翻转方法配置，0.5的概率  

Flipud: 0.5                          # 垂直翻转方法配置，0.5的概率，空值默认为1  

Resize: [604, 604]                     # resize 操作，宽、高  

CropAndPad:                          # 裁剪/填充增强器  
&nbsp;&nbsp;  #px: (0, 16)                        # 与 percent 不得共存  
&nbsp;&nbsp;  percent: (0, 0.2)
&nbsp;&nbsp;  pad_mode: ["constant", "edge"]  
&nbsp;&nbsp;  pad_cval: (0, 128)  
  
Rotate: [-90, 90]                      # 旋转  
Multiply:  [0.5, 1.5]                  # 颜色亮暗调整  
Affine:                            # 仿射变换增强器  
scale: [0.5, 1.5]                     # 缩放  
Sharpen:                           # 锐化增强器  
&nbsp;&nbsp;  alpha: [0.0, 1.0]  
&nbsp;&nbsp;  lightness: [0.75, 2.0]     
Add: [-100, 100]                      # 加法增强器，像素值增加列表中所列范围的随机值  

WithColorspace:                      # 颜色空间转换增强  
&nbsp;&nbsp;  to_colorspace: "HSV"  
&nbsp;&nbsp;  from_colorspace: "RGB"  
&nbsp;&nbsp;  children:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    WithChannels:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    channels: 0  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    children:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;      Add: [10, 50]  

Invert:                           # 反转增强器, 设置0-1的比例，默认为1，将原始像素值V变成255-V  
ContrastNormalization: [0.5, 1.5]          # 对比度增强器  
AdditiveGaussianNoise:                 # 高斯噪声, 0.2为比例  
scale: 0.1 * 255  
Dropout:                          # 随机丢弃像素点，将其置为0，p为概率值，下同  
&nbsp;&nbsp;&nbsp;&nbsp;  p: [0, 0.2]  
CoarseDropout:                      # 矩形丢弃增强器，将图片中矩形方块像素值置为0  
&nbsp;&nbsp;&nbsp;&nbsp;  p: 0.02  
size_percent: 0.5  
rayscale:                        # 灰度增强器  
&nbsp;&nbsp;&nbsp;&nbsp;  alpha: [0.0, 1.0]  
GaussianBlur:                     # 高斯模糊  
sigma: [0.0, 3.0]  
AverageBlur:                      # 均值模糊  
&nbsp;&nbsp;&nbsp;&nbsp;  k: [2, 11]  #((5, 11), (1, 3))  
MedianBlur:                      # 中值模糊  
&nbsp;&nbsp;&nbsp;&nbsp;  k: [3, 11]  
Emboss:                        # 浮雕增强器  
&nbsp;&nbsp;&nbsp;&nbsp;  alpha: [0.0, 1.0]  
&nbsp;&nbsp;&nbsp;&nbsp;  strength: [0.5, 1.5]  
EdgeDetect:                     # 边缘增强器  
&nbsp;&nbsp;&nbsp;&nbsp;  alpha: [0.0, 1.0]  

***增强方式二配置***  
Sequential:                    # 顺序增强器标识符  
&nbsp;&nbsp;&nbsp;&nbsp;  bg_changed:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    bg_path: "./data/bg_imgs"  
&nbsp;&nbsp;&nbsp;&nbsp;  Fliplr: 0.5                                
&nbsp;&nbsp;&nbsp;&nbsp;  Flipud:                            
&nbsp;&nbsp;&nbsp;&nbsp;  Resize: [608, 608]  
&nbsp;&nbsp;&nbsp;&nbsp;  CropAndPad:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    #px: (0, 16)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    percent: (0, 0.2)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    pad_mode: ["constant", "edge"]  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    pad_cval: (0, 128)  
&nbsp;&nbsp;&nbsp;&nbsp;  Rotate: [-90, 90]   
  
&nbsp;&nbsp;&nbsp;&nbsp;  WithColorspace: #颜色空间转换增强  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    to_colorspace: "HSV"  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    from_colorspace: "RGB"  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    children:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;      WithChannels:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;      channels: 0  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;      children:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;       Add: [10, 50]  

&nbsp;&nbsp;&nbsp;&nbsp;  Multiply:   
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    mul: [0.5, 1.5]  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    per_channel: 0.5  
&nbsp;&nbsp;&nbsp;&nbsp;  Affine:   
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  rotate: [-45, 45]   
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  scale: [0.5, 1.5]   
&nbsp;&nbsp;&nbsp;&nbsp;  PiecewiseAffine:                      # 扭曲增强器  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  scale: [0.01, 0.05]  
&nbsp;&nbsp;&nbsp;&nbsp;  Sharpen:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    alpha: [0.0, 1.0]  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    lightness: [0.75, 2.0]  
&nbsp;&nbsp;&nbsp;&nbsp;  Add: [-100, 100]  
&nbsp;&nbsp;&nbsp;&nbsp;  Invert:   
&nbsp;&nbsp;&nbsp;&nbsp;  ContrastNormalization: [0.5, 1.5]            # 对比度增强器  
&nbsp;&nbsp;&nbsp;&nbsp;  AdditiveGaussianNoise:   
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    scale: 0.2 * 255  
&nbsp;&nbsp;&nbsp;&nbsp;  Dropout:   
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    p: [0, 0.2]  
&nbsp;&nbsp;&nbsp;&nbsp;  CoarseDropout:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;   p: 0.02  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    size_percent: 0.5  
&nbsp;&nbsp;&nbsp;&nbsp;  Grayscale:                            # 灰度增强器  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    alpha: [0.0, 1.0]  
&nbsp;&nbsp;&nbsp;&nbsp;  GaussianBlur:   
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    sigma: [0.0, 3.0]  
&nbsp;&nbsp;&nbsp;&nbsp;  AverageBlur:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    k: [2, 11]  #((5, 11), (1, 3))  
&nbsp;&nbsp;&nbsp;&nbsp;  MedianBlur:   
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    k: [3, 11]  
&nbsp;&nbsp;&nbsp;&nbsp;  Emboss:   
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    alpha: [0.0, 1.0]  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    strength: [0.5, 1.5]  
&nbsp;&nbsp;&nbsp;&nbsp;  EdgeDetect:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    alpha: [0.0, 1.0]  
