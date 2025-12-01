#!/usr/bin/env python3
"""
Arc Engine - RHI 依赖部署脚本
用于部署 RHI 所需的第三方库
"""

import sys
import argparse
from pathlib import Path

# 脚本目录
SCRIPT_DIR = Path(__file__).parent.resolve()
DEP_DIR = SCRIPT_DIR / "dep"

# 添加 dep 目录到 Python 路径
sys.path.insert(0, str(DEP_DIR))

def deploy_angle():
    """部署 ANGLE"""
    from deploy_angle import deploy
    deploy()

def deploy_all():
    """部署所有依赖"""
    print("=" * 50)
    print("Arc Engine - 部署所有依赖")
    print("=" * 50)
    print()
    
    # ANGLE
    print("[1/1] 部署 ANGLE...")
    deploy_angle()
    
    # 未来可以添加更多依赖
    # print("[2/x] 部署 xxx...")
    # deploy_xxx()
    
    print()
    print("=" * 50)
    print("✓ 所有依赖部署完成！")
    print("=" * 50)

def main():
    parser = argparse.ArgumentParser(
        description="Arc Engine RHI 依赖部署工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 deploy.py              # 部署所有依赖
  python3 deploy.py --all        # 部署所有依赖
  python3 deploy.py --angle      # 只部署 ANGLE
  python3 deploy.py --list       # 列出可用依赖
        """
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="部署所有依赖"
    )
    
    parser.add_argument(
        "--angle",
        action="store_true",
        help="只部署 ANGLE"
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="列出可用依赖"
    )
    
    args = parser.parse_args()
    
    # 列出依赖
    if args.list:
        print("可用依赖:")
        print("  - angle    OpenGL ES 实现 (via ANGLE)")
        # 未来添加更多
        # print("  - xxx      描述")
        return
    
    # 部署特定依赖
    if args.angle:
        deploy_angle()
        return
    
    # 默认部署所有
    deploy_all()

if __name__ == "__main__":
    main()

