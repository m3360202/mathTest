#!/usr/bin/env python3
"""
简单检查两个服务是否正常运行
"""

import requests

def main():
    print("🔍 检查服务状态...")
    
    # 检查Python服务
    try:
        response = requests.get("http://localhost:8001/health", timeout=3)
        if response.status_code == 200:
            print("✅ Python解析服务 (端口8001): 正常运行")
        else:
            print(f"❌ Python解析服务: 状态码 {response.status_code}")
    except:
        print("❌ Python解析服务 (端口8001): 无法连接")
        print("   请运行: .\\start_python.bat")
    
    # 检查Node.js服务
    try:
        response = requests.get("http://localhost:3000/health", timeout=3)
        if response.status_code == 200:
            print("✅ Node.js主服务 (端口3000): 正常运行")
        else:
            print(f"❌ Node.js主服务: 状态码 {response.status_code}")
    except:
        print("❌ Node.js主服务 (端口3000): 无法连接")
        print("   请运行: .\\start_nodejs.bat")
    
    print("\n🎯 如果两个服务都正常，你就可以:")
    print("   • 上传文档: py upload_demo.py")
    print("   • 搜索内容: py test_client.py --search '你的搜索词'")

if __name__ == "__main__":
    main() 