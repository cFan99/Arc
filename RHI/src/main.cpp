#include <iostream>

// macOS OpenGL
#ifdef __APPLE__
    #define GL_SILENCE_DEPRECATION // 忽略OpenGL的弃用警告
    #include <OpenGL/gl3.h>
#endif

#include <GLFW/glfw3.h>

int main() 
{
    // 1. 初始化 GLFW
    if (!glfwInit()) 
    {
        std::cerr << "Failed to init GLFW" << std::endl;
        return -1;
    }

    // 2. 配置 OpenGL 版本 (macOS 最高 4.1)
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 4);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 1);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
    glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE);  // macOS 必须

    // 3. 创建窗口
    GLFWwindow* window = glfwCreateWindow(800, 600, "Arc Engine", nullptr, nullptr);
    if (!window) {
        std::cerr << "Failed to create window" << std::endl;
        glfwTerminate();
        return -1;
    }

    // 4. 设置当前上下文
    glfwMakeContextCurrent(window);

    // 5. 打印 OpenGL 信息
    std::cout << "OpenGL Version: " << glGetString(GL_VERSION) << std::endl;
    std::cout << "OpenGL Renderer: " << glGetString(GL_RENDERER) << std::endl;

    // 6. 主循环
    while (!glfwWindowShouldClose(window)) {
        // 清屏 - 深蓝色背景
        glClearColor(0.1f, 0.1f, 0.2f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT);

        // 交换缓冲区
        glfwSwapBuffers(window);

        // 处理事件
        glfwPollEvents();
    }

    // 7. 清理
    glfwDestroyWindow(window);
    glfwTerminate();

    std::cout << "Window closed." << std::endl;
    return 0;
}