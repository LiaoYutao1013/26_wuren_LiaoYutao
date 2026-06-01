## ROS2基础作业：

# 一些提示：

作业要求的是8字形，也就是说，乌龟先画一个圆，然后向反方向画另一个圆；
可以思考一下下面的问题：
乌龟的运动消息格式是什么？
什么参数能控制乌龟的转向？
另外，如何保证乌龟的画两个圆是相切的？

# 格式要求：
创建一个功能包就行，可以参考样例工作空间的格式要求
也没有必要创建发布端和接收端什么的，一个源文件全包含了就行
参考格式：
ros2_homework_basic_ws
    build
    install
    log
    src
        ros2_homework_basic_package
            config
            include(比较简单，不必须)
            launch
                xxx.launch.py
            src
                xxx.cpp
            result
                可视化截图和运行视频等
            CMakeLists.txt
            package.xml
    README.md（代码启动命令流程、ROS学习笔记、作业完成思路、完成作业遇到的困难以及解决 办法、AI使用情况等）