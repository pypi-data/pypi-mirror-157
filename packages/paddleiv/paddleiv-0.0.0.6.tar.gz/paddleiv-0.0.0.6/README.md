# Install
pip install paddleiv
# Author
Xuheng Cao (caoxuhengcn@gmail.com)
# Example
## paddleiv.get_mat_train()
用于多模态图像融合训练集制作：  
1) 适用于Mat格式的数据集制作，将mat格式样本放入'train' 文件夹中
2) 每一个样本Mat文件中的key
3) 用于生成多光谱图像的光谱响应函数srf
4) 图像块的采样间隔inc
5) 图像块的大小
6) 超分辨率因数sf

>In[1]: &ensp;import numpy as np  
&emsp;&emsp;&emsp;import paddleiv as piv  
&emsp;&emsp;&emsp;train_data = piv.get_mat_train('train/','key',srf,inc,patch_size,sf)

## paddleiv.init_weights()
用于对网络卷积网络进行参数初始化：  
1) init_type初始化方法有 'normal'，'mean_space'，'mean_channel'，'xavier'，'kaiming'，'orthogonal'
2) 待初始化网络Net
>In[2]:  &ensp;Net=ConvolutionNN()  
&emsp;&emsp;&emsp;piv.init_weights(Net,init_type='normal')  


## paddleiv.SAM_Loss()
提供SAM损失指标
>In[3]: &ensp; S_loss=SAM_Loss()  
 &emsp; &emsp; &emsp;l = S_loss(predict,label)  
 &emsp; &emsp; &emsp;l.backward()

## paddleiv.PSNR_Loss()
提供PSNR损失指标
>In[4]: &ensp; P_loss=PSNR_Loss()  
 &emsp; &emsp; &emsp;l = P_loss(predict,label)  
 &emsp; &emsp; &emsp;l.backward()
