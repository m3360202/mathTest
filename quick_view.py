#!/usr/bin/env python3
"""
快速查看向量数据库内容
"""

import requests
import json

def main():
    print("📚 快速查看向量数据库内容")
    print("=" * 40)
    
    try:
        # 1. 获取数据库统计信息
        print("📊 数据库统计信息:")
        response = requests.get("http://localhost:3000/database/stats")
        if response.status_code == 200:
            stats = response.json()['statistics']
            print(f"   📄 总文档数: {stats['totalDocuments']}")
            print(f"   💾 总存储量: {stats['totalStorage']} 字符")
            print(f"   📏 平均长度: {stats['averageContentLength']} 字符")
            print(f"   📁 文件类型: {stats['fileTypes']}")
        else:
            print("   ❌ 无法获取统计信息")
        
        print()
        
        # 2. 获取所有文档列表
        print("📋 所有文档列表:")
        response = requests.get("http://localhost:3000/documents")
        if response.status_code == 200:
            data = response.json()
            documents = data['documents']
            
            if not documents:
                print("   📭 数据库中没有文档")
                print("   💡 请先使用 upload_demo.py 上传文档")
                return
            
            for i, doc in enumerate(documents, 1):
                print(f"\n   📄 文档 {i}:")
                print(f"      🆔 ID: {doc['id']}")
                print(f"      📝 文件名: {doc['filename']}")
                print(f"      📅 上传时间: {doc['uploadedAt']}")
                print(f"      📏 内容长度: {doc['contentLength']} 字符")
                print(f"      📖 内容预览: {doc['contentPreview']}")
        else:
            print("   ❌ 无法获取文档列表")
        
        print()
        print("🔍 想要搜索特定内容？运行:")
        print("   python database_viewer.py")
        print("   或")
        print("   python test_client.py --search '你的搜索词'")
            
    except Exception as e:
        print(f"❌ 连接失败: {str(e)}")
        print("💡 请确保Node.js服务正在运行 (端口3000)")

if __name__ == "__main__":
    main() 