# 基础作业一记录

在最终代码流程、细节之前，先记录一下迭代过程：
第一次搭建的网络大致如下：

```python
nn.Flatten(),
nn.Linear(64 * 8 * 8, 128),
nn.ReLU(),
nn.Dropout(0.3),
nn.Linear(128, 3)
```

训练效果来看，记得是第一组达到了90%，然后没看到保存模型的条件，直接运行test报错了。。
首先考虑是不是因为训练轮数还不够，但实测下来`epoch=300`以后准确率就基本维持在一个很小的区间（1组在92-93，2组在85左右），这条路明显走不通；
然后开始考虑是不是自己的网络过于简单了（确实是，旁支、激活函数等等都还没有启用。。。）
接着开始堆料，这里的完整代码相对有点参考价值

```python
    def __init__(self):
        super(mixed_net,self).__init__()

        #初始化输入层
        self.conv1 = nn.Conv2d(in_channels=3, out_channels=16, kernel_size=3, stride=1, padding=1)
        self.conv2 = nn.Conv2d(in_channels=16, out_channels=32, kernel_size=3, stride=1, padding=1)
        self.conv3 = nn.Conv2d(in_channels=32, out_channels=64, kernel_size=3, stride=1, padding=1)

        #池化处理,预计特征的大小是 64*8*8
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)

        #初始化旁支
        #旁支1:卷积核大小3x3，用于聚焦锥桶边缘特征和纹理信息；
        self.branch1 = nn.Sequential(
            nn.Conv2d(in_channels=16, out_channels=32, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2)
        )
        #旁支2:卷积核大小5x5，用于观察较大范围的色块，这与锥桶的颜色分布特点是一致的；
        self.branch2 = nn.Sequential(
            nn.Conv2d(in_channels=32, out_channels=64, kernel_size=5, stride=1, padding=2),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2)
        )

        #初始化全连接层
        self.fc1 = nn.Linear(160*8*8, 512)
        self.fc2 = nn.Linear(512, 256)
        self.fc3 = nn.Linear(256, 3)
    
    def forward(self, x):
        '''
        公式： W = (W + 2padding - kernel_w) / stride + 1
        这个公式是用来给手算参考的，实际这些工作已经被封装在了上面的方法中，不用自己再手动实现了。      
        '''

        x = self.pool(F.relu(self.conv1(x)))    # [B, 16, 32, 32]
        b1 = self.branch1(x)            # [B, 32, 16, 16]
        x = self.pool(F.relu(self.conv2(x)))    # [B, 32, 16, 16]
        b2 = self.branch2(x)            # [B, 64, 8, 8]

         # 将主干和旁支的特征图进行融合
        x = self.pool(F.relu(self.conv3(x)))    # [B, 64, 8, 8]

        b1 = self.pool(b1)           # [B, 32, 8, 8]

        x = torch.cat([x, b1], dim=1)  # 通道拼接

        x = torch.flatten(x, start_dim=1)  # [B, 160*8*8]
        
        # 全连接层
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
```

方法参数设置部分，有一部分是由IDE的代码联想功能完成的，参考网上的资料简并了一些层的写法，但数层数的时候发现超过要求了，于是开始设法减少层数
另外，这一轮准确率最高来到了95%附近，第二组的准确率提升更加明显，最高来到93%。
跟AI交流询问还有什么能提升模型性能的方法，提到了BatchNorm:
在深层神经网络中，随着每一层权重的更新，下一层接收到的数据分布会不断变化（内部协变量偏移）。这会让网络变得非常难调教，收敛极慢。BatchNorm 的出现就是为了解决这个问题。
BatchNorm 在每一层的激活函数之前，对一个小批量（Batch）的数据进行以下操作：

- 标准化：计算该 Batch 的均值和方差，把数据转换成均值为 0、方差为 1 的标准分布。
- 缩放与平移：为了不让标准化破坏模型原有的表达能力，BatchNorm 引入了两个可学习的参数：$\gamma$（缩放）和 $\beta$（平移）。$$y = \gamma \cdot \frac{x - \mu}{\sqrt{\sigma^2 + \epsilon}} + \beta$$这样，网络可以自己决定是保持标准化，还是为了更好的效果稍微偏离一点。

现在考虑用它实验是否能提升模型性能。
同时增强训练集。

关于优化方案，了解到SGD和Adam（AI建议考虑当前的优化方案是否合适，于是详细查询了这两个概念）：

1. SGD (随机梯度下降)
   - 核心逻辑：它不仅考虑当前的梯度，还考虑之前的惯性。
   - 数学原理：$$v_t = \gamma v_{t-1} + \eta \nabla \theta$$$$\theta = \theta - v_t$$（其中 $\gamma$ 是动量因子，$\eta$ 是学习率）
   - 优点：
     - 泛化能力强：虽然收敛慢，但最终往往能找到更优的解，模型在测试集上的表现通常更好。
     - 简单稳定：没有复杂的计算，内存占用极低。
   - 缺点：
     - 慢：需要更长的训练时间。
     - 调参难：对学习率（Learning Rate）非常敏感，通常需要配合复杂的学习率衰减策略。
2. Adam (自适应矩估计)
   - 核心逻辑：它为每一个参数动态地计算学习率。如果某个参数的梯度波动很大，它就慢一点；如果梯度很稳，它就走快点。
   - 数学原理：它同时记录梯度的一阶矩（均值）和二阶矩（方差），并进行偏差修正。
   - 优点：
     - 收敛极快：在训练初期能迅速降低损失函数。
     - 省心：对初始学习率不那么敏感，默认值（通常是 0.001）往往就能跑出不错的结果。处理稀疏梯度：非常适合处理 NLP 或包含大量嵌入层（Embedding）的任务。
   - 缺点：
     - 可能陷入局部最优：因为它走得太快，有时会冲过头，或者停在一些泛化性不好的“坑”里。
     - 计算开销：由于要维护多个状态，内存占用比 SGD 高。

回到正题，这一次的模型运行相当成功，最终预测集上准确率第一组来到100%,第二组也有95%，生成的模型文件已保存在`./pth`中。

网络最终的结构如下：
```Input
[B, 3, 64, 64]
   |
   v
Conv2d(3 -> 32, kernel=3, padding=1)
[B, 32, 64, 64]
   |
BatchNorm2d(32)
   |
ReLU
   |
MaxPool2d(2, 2)
[B, 32, 32, 32]
   |
   v
Conv2d(32 -> 64, kernel=3, padding=1)
[B, 64, 32, 32]
   |
BatchNorm2d(64)
   |
ReLU
   |
MaxPool2d(2, 2)
[B, 64, 16, 16]
   |
   v
Conv2d(64 -> 128, kernel=3, padding=1)
[B, 128, 16, 16]
   |
BatchNorm2d(128)
   |
ReLU
   |
MaxPool2d(2, 2)
[B, 128, 8, 8]
   |
   v
Conv2d(128 -> 128, kernel=3, padding=1)
[B, 128, 8, 8]
   |
BatchNorm2d(128)
   |
ReLU
[B, 128, 8, 8]
   |
   v
AdaptiveAvgPool2d((1, 1))
[B, 128, 1, 1]
   |
   v
Flatten
[B, 128]
   |
   v
Dropout(0.3)
[B, 128]
   |
   v
Linear(128 -> 3)
[B, 3]
```

除开激活函数和旁支，共有4层Conv2d，4层BatchNorm2d，1层AdaptiveAvgPool2d，1层Linear，恰好10层，全连接层也不超过3层。

创新点（？）：增强训练集，因为原先的训练集和测试集共用一套，可能泛化能力不足（或者应该称之为样本量不足？），具体做了以下优化（代码里从上到下）：

- 1. 翻转图像，构建扩大的训练集；
- 2. 旋转图像，目的同上；
- 3. 随机调亮度、饱和度、对比度，增加模型容错；
