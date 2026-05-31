# SCUT Racing Tasks

这个仓库用于记录 SCUT Racing 学习任务中的代码、笔记、实验数据和作业实现。内容按周组织，覆盖 Linux/CMake、机器学习、深度学习、ROS 2 等方向。

## 仓库结构

```text
.
├── Week1/
│   ├── CMake 1/                 # CMake 与 C++ 模块化编译练习
│   ├── CMake_Study_Notes.md     # CMake 学习笔记
│   ├── linux_practice/          # Linux 命令练习文件
│   └── linux_practice.sh        # Linux 练习脚本
├── Week2/
│   └── homework/                # 机器学习基础作业
├── Week3/
│   ├── dataset/                 # 锥桶图像分类数据集
│   ├── pth/                     # 训练得到的 PyTorch 模型权重
│   ├── 锥桶图像分类.ipynb       # 深度学习分类实验
│   ├── 深度学习笔记.md
│   └── 深度学习论文阅读记录.md
├── Week4/
│   └── ros2_learning-main/      # ROS 2 示例、基础作业和进阶作业
├── .gitignore                   # 构建产物和本地环境忽略规则
└── README.md
```

## 内容说明

### Week1：Linux 与 CMake

- 练习常用 Linux 命令、脚本执行和文件操作。
- 使用 CMake 组织 C++ 项目，包含多级目录、库目标和模块化编译。
- 主要入口：`Week1/CMake 1/README.md`、`Week1/CMake_Study_Notes.md`

### Week2：机器学习基础

`Week2/homework/` 中包含四个基础机器学习实验：

- 作业1：遗传算法与可视化。
- 作业2：多元线性回归与岭回归。
- 作业3：Iris 数据集上的 SVM 分类。
- 作业4：K-means 聚类。

说明文档见 `Week2/homework/README.md`。

### Week3：深度学习与图像分类

这一部分主要围绕锥桶图像分类任务展开：

- 使用 PyTorch 搭建分类网络。
- 记录网络结构、训练过程、优化思路和实验结果。
- 保存训练数据、测试数据和若干模型权重。
- 包含论文阅读记录与深度学习学习笔记。

主要文件：

- `Week3/锥桶图像分类.ipynb`
- `Week3/test.py`
- `Week3/net copy.py`
- `Week3/深度学习笔记.md`
- `Week3/深度学习论文阅读记录.md`

### Week4：ROS 2 学习

`Week4/ros2_learning-main/` 中包含 ROS 2 示例代码和作业：

- `ros2_case/`：课堂示例，包括参数读取、launch 文件、topic 发布与订阅。
- `ros2_homework_basic_ws/`：基础作业工作空间，使用 turtlesim 实现 8 字形轨迹。
- `ros2_homework_advanced/`：进阶作业说明，涉及地图话题、坐标系和 RViz 可视化。

基础作业入口：

```bash
cd Week4/ros2_learning-main/ros2_homework_basic_ws
colcon build
source install/setup.bash
ros2 launch ros2_homework_basic_package figure_eight.launch.py
```

## 常用命令

### 编译 Week1 CMake 项目

```bash
cd "Week1/CMake 1"
mkdir -p build
cd build
cmake ..
make -j6
```

### 运行 Week2/Week3 Notebook

建议在 Python 虚拟环境中安装依赖后启动 Jupyter：

```bash
jupyter notebook
```

然后在浏览器中打开对应的 `.ipynb` 文件。

### 编译 ROS 2 工作空间

在 ROS 2 环境已经配置好的终端中执行：

```bash
cd Week4/ros2_learning-main/ros2_homework_basic_ws
colcon build
source install/setup.bash
```

如果使用的是 Windows 主机，ROS 2 部分建议在 Ubuntu/WSL 或原生 Linux 环境中运行。

## Git 说明

仓库已配置 `.gitignore`，用于忽略常见本地文件和编译产物，包括：

- ROS 2/colcon 产物：`build/`、`install/`、`log/`
- CMake/C++ 产物：`CMakeFiles/`、`CMakeCache.txt`、目标文件、库文件、可执行文件等
- Python 缓存：`__pycache__/`、`*.pyc`
- 本地环境与编辑器配置：`.venv/`、`.vscode/`、`.idea/`

提交前可以用下面的命令检查状态：

```bash
git status --short
```

如果某些编译产物已经被 Git 跟踪，需要先从索引中移除，再依靠 `.gitignore` 阻止后续提交。

## 备注

本仓库偏向学习记录与阶段性作业归档，部分目录中包含实验过程文件、模型权重和数据集。后续如果需要减小仓库体积，可以考虑将大文件迁移到单独的数据存储或使用 Git LFS 管理。
