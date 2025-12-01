cmake_minimum_required(VERSION 3.20)

project(Arc_RHI)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 查找 GLFW
find_package(glfw3 3.3 REQUIRED)

# 先做个简单的可执行程序测试
add_executable(arc_test src/main.cpp)

# 链接库
if(APPLE)
    target_link_libraries(arc_test PRIVATE
        glfw
        "-framework OpenGL"
        "-framework Cocoa"
        "-framework IOKit"
        "-framework CoreVideo"
    )
endif()