#!/usr/bin/env python3
"""
数学文档处理系统测试客户端

使用方法:
python test_client.py --file test.docx --search "数学公式"
"""

import argparse
import requests
import json
import os
from pathlib import Path

class MathDocumentClient:
    def __init__(self, base_url="http://localhost:3000"):
        self.base_url = base_url.rstrip('/')
        
    def check_health(self):
        """检查系统健康状态"""
        try:
            response = requests.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"❌ 健康检查失败: {e}")
            return None
    
    def check_status(self):
        """检查系统各组件状态"""
        try:
            response = requests.get(f"{self.base_url}/status")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"❌ 状态检查失败: {e}")
            return None
    
    def upload_document(self, file_path):
        """上传并处理文档"""
        if not os.path.exists(file_path):
            print(f"❌ 文件不存在: {file_path}")
            return None
            
        try:
            with open(file_path, 'rb') as f:
                files = {'docxFile': (os.path.basename(file_path), f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
                response = requests.post(f"{self.base_url}/upload", files=files, timeout=60)
                response.raise_for_status()
                return response.json()
        except requests.RequestException as e:
            print(f"❌ 文档上传失败: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    print(f"详细错误: {json.dumps(error_detail, indent=2, ensure_ascii=False)}")
                except:
                    print(f"响应内容: {e.response.text}")
            return None
    
    def search_documents(self, query, limit=5):
        """搜索文档"""
        try:
            payload = {"query": query, "limit": limit}
            response = requests.post(f"{self.base_url}/search", json=payload)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"❌ 搜索失败: {e}")
            return None
    
    def get_documents(self):
        """获取文档列表"""
        try:
            response = requests.get(f"{self.base_url}/documents")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"❌ 获取文档列表失败: {e}")
            return None

def main():
    parser = argparse.ArgumentParser(description="数学文档处理系统测试客户端")
    parser.add_argument("--url", default="http://localhost:3000", help="API服务地址")
    parser.add_argument("--file", help="要上传的docx文件路径")
    parser.add_argument("--search", help="搜索查询")
    parser.add_argument("--limit", type=int, default=5, help="搜索结果限制数量")
    parser.add_argument("--health", action="store_true", help="检查健康状态")
    parser.add_argument("--status", action="store_true", help="检查系统状态")
    parser.add_argument("--list", action="store_true", help="列出所有文档")
    
    args = parser.parse_args()
    
    client = MathDocumentClient(args.url)
    
    print(f"🔗 连接到服务: {args.url}")
    
    # 健康检查
    if args.health or not any([args.file, args.search, args.status, args.list]):
        print("\n📋 执行健康检查...")
        health = client.check_health()
        if health:
            print(f"✅ 服务健康: {json.dumps(health, indent=2, ensure_ascii=False)}")
        else:
            print("❌ 服务不健康")
            return
    
    # 系统状态检查
    if args.status:
        print("\n📊 检查系统状态...")
        status = client.check_status()
        if status:
            print(f"📈 系统状态: {json.dumps(status, indent=2, ensure_ascii=False)}")
        else:
            print("❌ 无法获取系统状态")
    
    # 文档上传
    if args.file:
        print(f"\n📄 上传文档: {args.file}")
        result = client.upload_document(args.file)
        if result:
            print(f"✅ 上传成功: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print("❌ 上传失败")
    
    # 文档搜索
    if args.search:
        print(f"\n🔍 搜索文档: '{args.search}'")
        results = client.search_documents(args.search, args.limit)
        if results:
            print(f"🎯 搜索结果: {json.dumps(results, indent=2, ensure_ascii=False)}")
        else:
            print("❌ 搜索失败")
    
    # 列出文档
    if args.list:
        print("\n📚 获取文档列表...")
        docs = client.get_documents()
        if docs:
            print(f"📋 文档列表: {json.dumps(docs, indent=2, ensure_ascii=False)}")
        else:
            print("❌ 获取文档列表失败")

if __name__ == "__main__":
    main() 