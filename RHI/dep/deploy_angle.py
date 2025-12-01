#!/usr/bin/env python3
"""
Arc Engine - ANGLE Deploy Script
跨平台自动下载并编译 ANGLE
支持: macOS, Windows, Linux
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path

# ==================== 配置 ====================

# ANGLE 仓库地址
ANGLE_REPO = "https://chromium.googlesource.com/angle/angle"
DEPOT_TOOLS_REPO = "https://chromium.googlesource.com/chromium/tools/depot_tools.git"

# 脚本所在目录（dep/）
SCRIPT_DIR = Path(__file__).parent.resolve()

# 编译目录（dep/angle_build）
BUILD_DIR = SCRIPT_DIR / "angle_build"

# 输出目录（dep/angle）
OUTPUT_DIR = SCRIPT_DIR / "angle"

# ==================== 工具函数 ====================

def get_platform():
    """获取当前平台"""
    system = platform.system()
    if system == "Darwin":
        return "macos"
    elif system == "Windows":
        return "windows"
    elif system == "Linux":
        return "linux"
    else:
        print(f"不支持的平台: {system}")
        sys.exit(1)

def get_arch():
    """获取 CPU 架构"""
    machine = platform.machine().lower()
    if machine in ("arm64", "aarch64"):
        return "arm64"
    elif machine in ("x86_64", "amd64"):
        return "x64"
    else:
        return machine

def run_command(cmd, cwd=None, env=None):
    """运行命令并实时显示输出（进度条会原地更新）"""
    print(f">>> {cmd}")
    sys.stdout.flush()
    
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    
    # 直接运行，不捕获输出，让终端直接显示
    # 这样进度条的 \r 控制字符会正常工作
    result = subprocess.run(
        cmd,
        shell=True,
        cwd=cwd,
        env=merged_env
        # 不设置 stdout/stderr，让它们直接输出到终端
    )
    
    if result.returncode != 0:
        print(f"\n命令执行失败，返回码: {result.returncode}")
        sys.exit(1)
    
    return result

def ensure_directory(path):
    """确保目录存在"""
    Path(path).mkdir(parents=True, exist_ok=True)

# ==================== 主要步骤 ====================

def install_depot_tools():
    """安装 depot_tools"""
    depot_tools_dir = BUILD_DIR / "depot_tools"
    
    if depot_tools_dir.exists():
        print("depot_tools 已存在，跳过下载")
    else:
        print("=== 下载 depot_tools ===")
        ensure_directory(BUILD_DIR)
        run_command(f"git clone --progress {DEPOT_TOOLS_REPO}", cwd=BUILD_DIR)
    
    return depot_tools_dir

def get_env_with_depot_tools(depot_tools_dir):
    """获取包含 depot_tools 的环境变量"""
    env = os.environ.copy()
    
    current_platform = get_platform()
    
    if current_platform == "windows":
        env["PATH"] = f"{depot_tools_dir};{env.get('PATH', '')}"
        env["DEPOT_TOOLS_WIN_TOOLCHAIN"] = "0"
    else:
        env["PATH"] = f"{depot_tools_dir}:{env.get('PATH', '')}"
    
    return env

def clone_angle():
    """克隆 ANGLE 源码"""
    angle_dir = BUILD_DIR / "angle"
    
    if angle_dir.exists():
        print("ANGLE 已存在，更新中...")
        run_command("git pull --progress", cwd=angle_dir)
    else:
        print("=== 克隆 ANGLE ===")
        run_command(f"git clone --progress {ANGLE_REPO}", cwd=BUILD_DIR)
    
    return angle_dir

def sync_dependencies(angle_dir, env):
    """同步 ANGLE 依赖"""
    print("=== 同步依赖（这可能需要一些时间）===")
    run_command("python3 scripts/bootstrap.py", cwd=angle_dir, env=env)
    run_command("gclient sync", cwd=angle_dir, env=env)

def configure_build(angle_dir, env):
    """配置编译选项"""
    print("=== 配置编译 ===")
    
    current_platform = get_platform()
    
    # 根据平台设置编译参数
    if current_platform == "macos":
        gn_args = 'is_debug=false is_component_build=false angle_enable_metal=true angle_enable_vulkan=false angle_enable_gl=false angle_enable_null=false'
    elif current_platform == "windows":
        gn_args = 'is_debug=false is_component_build=false angle_enable_d3d11=true angle_enable_vulkan=true angle_enable_gl=false angle_enable_null=false'
    elif current_platform == "linux":
        gn_args = 'is_debug=false is_component_build=false angle_enable_vulkan=true angle_enable_gl=true angle_enable_null=false'
    
    if current_platform == "windows":
        run_command(f'gn gen out/Release --args="{gn_args}"', cwd=angle_dir, env=env)
    else:
        run_command(f"gn gen out/Release --args='{gn_args}'", cwd=angle_dir, env=env)

def build_angle(angle_dir, env):
    """编译 ANGLE"""
    print("=== 编译 ANGLE（这需要 10-30 分钟）===")
    run_command("autoninja -C out/Release libEGL libGLESv2", cwd=angle_dir, env=env)

def copy_to_project(angle_dir):
    """复制编译结果到项目"""
    print("=== 复制到项目 ===")
    
    current_platform = get_platform()
    
    # 创建输出目录
    lib_dir = OUTPUT_DIR / "lib"
    include_dir = OUTPUT_DIR / "include"
    ensure_directory(lib_dir)
    ensure_directory(include_dir)
    
    # 源目录
    release_dir = angle_dir / "out" / "Release"
    include_src = angle_dir / "include"
    
    # 库文件后缀
    if current_platform == "macos":
        lib_files = ["libEGL.dylib", "libGLESv2.dylib"]
    elif current_platform == "windows":
        lib_files = ["libEGL.dll", "libGLESv2.dll", "libEGL.dll.lib", "libGLESv2.dll.lib"]
    elif current_platform == "linux":
        lib_files = ["libEGL.so", "libGLESv2.so"]
    
    # 复制库文件
    for lib in lib_files:
        src = release_dir / lib
        if src.exists():
            dst = lib_dir / lib
            print(f"  复制: {lib}")
            shutil.copy2(src, dst)
        else:
            print(f"  警告: 未找到 {lib}")
    
    # 复制头文件
    header_dirs = ["EGL", "GLES2", "GLES3", "KHR"]
    for header_dir in header_dirs:
        src = include_src / header_dir
        dst = include_dir / header_dir
        if src.exists():
            print(f"  复制头文件: {header_dir}/")
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)

def verify_installation():
    """验证安装"""
    print("\n=== 验证安装 ===")
    
    lib_dir = OUTPUT_DIR / "lib"
    include_dir = OUTPUT_DIR / "include"
    
    print(f"\n库文件目录: {lib_dir}")
    if lib_dir.exists():
        for f in lib_dir.iterdir():
            print(f"  ✓ {f.name}")
    
    print(f"\n头文件目录: {include_dir}")
    if include_dir.exists():
        for f in include_dir.iterdir():
            if f.is_dir():
                print(f"  ✓ {f.name}/")

# ==================== 主函数 ====================

def deploy():
    """部署 ANGLE"""
    print("=" * 50)
    print("Arc Engine - ANGLE Deploy")
    print("=" * 50)
    
    current_platform = get_platform()
    arch = get_arch()
    print(f"平台: {current_platform}")
    print(f"架构: {arch}")
    print(f"输出目录: {OUTPUT_DIR}")
    print()
    
    # 步骤 1: 安装 depot_tools
    depot_tools_dir = install_depot_tools()
    env = get_env_with_depot_tools(depot_tools_dir)
    
    # 步骤 2: 克隆 ANGLE
    angle_dir = clone_angle()
    
    # 步骤 3: 同步依赖
    sync_dependencies(angle_dir, env)
    
    # 步骤 4: 配置编译
    configure_build(angle_dir, env)
    
    # 步骤 5: 编译
    build_angle(angle_dir, env)
    
    # 步骤 6: 复制到项目
    copy_to_project(angle_dir)
    
    # 步骤 7: 验证
    verify_installation()
    
    print("\n" + "=" * 50)
    print("✓ ANGLE 部署完成！")
    print("=" * 50)

if __name__ == "__main__":
    deploy()

