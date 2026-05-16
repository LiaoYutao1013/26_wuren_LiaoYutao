# CMake 学习笔记——第一周

目前是先自己手写一版CMake，然后试运行，如果报错了再和AI反馈，寻找错误原因和解决方案。

## 1. CMake 的作用

个人理解CMake 不是编译器，而是一套调用编译器（编译工具）的规范，指示各文件的依赖关系并调用编译器完成编译任务。

它读取项目中的 `CMakeLists.txt`，生成适合当前平台的构建文件：

- Linux 常见生成 `Makefile`，然后用 `make` 编译。
- Windows 可能生成 Visual Studio 工程、Ninja 构建文件或 Makefile。
- 项目源码、头文件、第三方库、编译选项都可以在 CMake 中统一管理。

编译过程中会产生大量文件，为了避免项目被污染，源代码目录和编译输出目录一般需要分离，让输出目录独立于工程本体。此外，Git中要添加过滤选项，以免把上百MB的编译产物一并上传到仓库（太痛了，回滚版本搞了老半天，Git还会卡上传文件体积）

## 2. 当前工程结构

```text
CMake 1/
├── CMakeLists.txt
├── main.cpp
├── common/
│   ├── CMakeLists.txt
│   ├── kalman/
│   │   ├── CMakeLists.txt
│   │   └── include/KalmanFilterX.hpp
│   └── math/
│       ├── CMakeLists.txt
│       ├── include/Math.h
│       └── src/Math.cpp
└── modules/
    ├── CMakeLists.txt
    ├── A1/
    ├── A2/
    ├── M1/
    └── M2/
```

这个工程采用分层组织：

- 顶层 `CMakeLists.txt`：设置工程、C++ 标准、添加子目录、生成最终可执行文件。
- `common/`：公共库，例如 `math` 和 `kalman`。
- `modules/`：功能模块库，例如 `A1`、`A2`、`M1`、`M2`。
- `main.cpp`：最终程序入口，链接各个库后生成 `test` 可执行文件。

## 3. 任务分析（夹杂CMake相关的笔记，先展示完成的代码吧）

最顶层的CMake长这样

```cmake
cmake_minimum_required(VERSION 3.19)

project(Test)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_subdirectory(common)
add_subdirectory(modules)

add_executable(test main.cpp)

target_link_libraries(test
    PRIVATE
        M1
        M2
        math
)
```

### cmake_minimum_required

指定当前项目要求的最低 CMake 版本。版本太低时，CMake 会直接报错。
（原来是3.10，我看题目要求就直接加到3.19了）

### project

定义工程名，但工程名不必须是最终可执行文件名。
（项目名和目标名的区别）

### 设置 C++ 标准

```cmake
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
```

各行含义：

- `CMAKE_CXX_STANDARD 14`：使用 C++14。
- `CMAKE_CXX_STANDARD_REQUIRED ON`：强制使用指定标准。
- `CMAKE_CXX_EXTENSIONS OFF`：关闭编译器扩展，尽量使用标准 C++规范。

### add_subdirectory

```cmake
add_subdirectory(common)
add_subdirectory(modules)
```

add_subdirectory 让 CMake 继续寻找子目录中的 `CMakeLists.txt`，并把其中的源代码链接起来（有点像include找头文件的感觉）。

在本工程中，

- `common/CMakeLists.txt` 会继续添加 `kalman` 和 `math`。
- `modules/CMakeLists.txt` 会继续添加 `A1`、`A2`、`M1`、`M2`。

### add_executable

```cmake
add_executable(test main.cpp)
```

生成一个名为 `test` 的可执行文件，源文件是 `main.cpp`。
test是目标名，与前文的工程项目名Test不同。

### target_link_libraries

```cmake
target_link_libraries(test
    PRIVATE
        M1
        M2
        math
)
```

表示 `test` 需要链接 `M1`、`M2`、`math` 三个库。

这里的 `PRIVATE` 表示这些依赖只对 `test` 自己有效，不需要继续传递给其他目标。

## 4. 库目标 add_library

例如 `modules/A1/CMakeLists.txt`：

```cmake
aux_source_directory(src A1_DIR)

add_library(A1 STATIC ${A1_DIR})

target_include_directories(A1
    PUBLIC
        ${CMAKE_CURRENT_LIST_DIR}/include
)
```

### aux_source_directory

```cmake
aux_source_directory(src A1_DIR)
```

把 `src` 目录下的源文件收集到变量 `A1_DIR` 中。

优点是写起来简单。

缺点是新增 `.cpp` 文件时，CMake 不一定会自动重新配置。实际项目中更推荐显式列出源文件，例如：

```cmake
add_library(A1 STATIC
    src/A11.cpp
    src/A12.cpp
    src/A13.cpp
)
```

### add_library STATIC

```cmake
add_library(A1 STATIC ${A1_DIR})
```

生成一个静态库目标 `A1`。

常见库类型：

- `STATIC`：静态库，Linux 下通常是 `.a`，Windows 下通常是 `.lib`。
- `SHARED`：动态库，Linux 下通常是 `.so`，Windows 下通常是 `.dll`。
- `INTERFACE`：接口库，不编译源码，只传播头文件目录、链接库和编译选项。

## 5. 头文件目录 target_include_directories

```cmake
target_include_directories(A1
    PUBLIC
        ${CMAKE_CURRENT_LIST_DIR}/include
)
```

作用是告诉 CMake：编译 `A1` 时，需要把 `A1/include` 加入头文件搜索路径。

`${CMAKE_CURRENT_LIST_DIR}` 表示当前这个 `CMakeLists.txt` 所在目录。

所以在 `modules/A1/CMakeLists.txt` 中：

```cmake
${CMAKE_CURRENT_LIST_DIR}/include
```

就等于：

```text
Week1/CMake 1/modules/A1/include
```

这样源码中就可以直接写：

```cpp
#include "A1.h"
```

而不需要写很长的相对路径。

## 6. PUBLIC、PRIVATE、INTERFACE

CMake 的现代写法是围绕 target 组织依赖。`PUBLIC`、`PRIVATE`、`INTERFACE` 决定依赖是否向后传播。

| 关键字 | 当前目标自己使用 | 链接当前目标的其他目标使用 | 常见场景 |
| --- | --- | --- | --- |
| `PRIVATE` | 是 | 否 | 只在 `.cpp` 内部使用的依赖 |
| `PUBLIC` | 是 | 是 | 头文件中暴露出去的依赖 |
| `INTERFACE` | 否 | 是 | header-only 库或只传播配置 |

```cmake
target_link_libraries(M2
    PUBLIC
        A1
        A2
        kalman
)
```

`M2.h` 中include的头文件如下：

```cpp
#include "KalmanFilterX.hpp"
#include "A1.h"
#include "A2.h"
```

因为这些类型出现在 `M2` 的头文件中，所以链接 `M2` 的目标也需要知道 `A1`、`A2`、`kalman` 的头文件目录。因此使用 `PUBLIC` 。（像是在交叉引用）

顶层：

```cmake
target_link_libraries(test
    PRIVATE
        M1
        M2
        math
)
```

`test` 是最终可执行文件，不会再被别的目标链接，所以这里用 `PRIVATE` 即可。
（印象里Makefile中有以自己为目标（空目标）来生成最终可执行文件的操作，CMake在此处做了封装？）

## 7. INTERFACE 库：kalman

`common/kalman/CMakeLists.txt`：

```cmake
find_package(OpenCV REQUIRED)

add_library(kalman INTERFACE)

target_include_directories(kalman
    INTERFACE
        ${CMAKE_CURRENT_LIST_DIR}/include
        ${OpenCV_INCLUDE_DIRS}
)

target_link_libraries(kalman
    INTERFACE
        ${OpenCV_LIBS}
)
```

`kalman` 目录中主要是 `KalmanFilterX.hpp`，属于头文件模板库，没有对应的 `.cpp` 需要编译，所以使用：

```cmake
add_library(kalman INTERFACE)
```

接口库不会生成真实的 `.a` 或 `.so` 文件，它只负责向使用者传播头文件目录，第三方链接库和编译选项。

因为 `KalmanFilterX.hpp` 中使用了 OpenCV：

```cpp
#include <opencv2/core.hpp>
```

所以 `kalman` 需要通过 `find_package(OpenCV REQUIRED)` 找到 OpenCV，并把 OpenCV 的 include 目录和库传递出去。

## 8. find_package

```cmake
find_package(OpenCV REQUIRED)
```

作用是查找系统中安装的 OpenCV（找第三方库）。

`REQUIRED` 表示如果找不到 OpenCV，CMake 配置阶段直接失败。

找到后，常见变量包括：

```cmake
${OpenCV_INCLUDE_DIRS}
${OpenCV_LIBS}
```

本工程中：

- `kalman` 需要 OpenCV。
- `math` 也间接需要 OpenCV，因为 `Math.h` 使用了 `cv::Point2f`、`cv::Matx33f` 等类型。
- `test` 最终通过链接 `M2` 和 `math` 间接获得 OpenCV 依赖。

## 9. 当前工程依赖关系

依赖关系树大致如下。

```text
test
├── M1
│   └── A1
├── M2
│   ├── A1
│   ├── A2
│   └── kalman
│       └── OpenCV
└── math
    └── kalman
        └── OpenCV
```

## 10. 子目录中 CMakeLists.txt 的作用

主要作用：继续向下搜寻编译使用的源文件（或者更深层的CMakeLists?），与其他CMake文件联动形成关系树。
`common/CMakeLists.txt`：

```cmake
add_subdirectory(kalman)
add_subdirectory(math)
```

`modules/CMakeLists.txt`：

```cmake
add_subdirectory(A1)
add_subdirectory(A2)
add_subdirectory(M1)
add_subdirectory(M2)
```

这种写法的好处在于结构清晰，便于管理工程，各层专注于本层的模块、依赖，增改功能模块时不会大规模重构。新增模块时，只需要新增对应目录和 `CMakeLists.txt`，再到上一级加一次`add_subdirectory`。

## 11. 编译常见问题

### 找不到头文件

现象：

```text
fatal error: xxx.h: No such file or directory
```

检查：

- 对应库是否写了 `target_include_directories`。
- include 目录是否写到了正确路径。
- 如果头文件被其他库的头文件继续包含，依赖是否应该使用 `PUBLIC` 或 `INTERFACE`。

最后可能还要考虑是不是源码编译失败导致的，我第一次编译的时候报错，最后检查推断是手残误删了一行include，重新补上后报错消失。（应该把这个情况归类在此？）

以下两种异常是和AI聊天时它提到的，一并写进来提醒自己。

### 找不到 OpenCV（或者其他可能需要的第三方库）

现象：

```text
Could not find OpenCV
```

检查：

- OpenCV（第三方库） 是否安装。
- `OpenCVConfig.cmake` 是否能被 CMake 找到。
- 必要时通过 `OpenCV_DIR` 指定路径。

### 链接失败

现象：

```text
undefined reference to ...
```

常见原因：

- `.cpp` 文件没有加入对应 `add_library` 或 `add_executable`。
- 需要链接的库没有写进 `target_link_libraries`。
- 依赖传播关键字写错，例如应该 `PUBLIC` 却写成 `PRIVATE`。
  