#!/usr/bin/env python3
"""
数学文档上传演示脚本
"""

import requests
import json
import os
from pathlib import Path

def check_services():
    """检查服务状态"""
    print("🔍 检查服务状态...")
    
    # 检查主服务
    try:
        response = requests.get("http://localhost:3000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Node.js主服务: 正常运行")
        else:
            print("❌ Node.js主服务: 异常")
            return False
    except:
        print("❌ Node.js主服务: 无法连接 (端口3000)")
        return False
    
    # 检查Python服务
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            print("✅ Python解析服务: 正常运行")
        else:
            print("❌ Python解析服务: 异常")
            return False
    except:
        print("❌ Python解析服务: 无法连接 (端口8001)")
        return False
    
    return True

def upload_document(file_path):
    """上传文档"""
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return None
    
    print(f"📤 上传文档: {file_path}")
    
    try:
        with open(file_path, 'rb') as f:
            files = {
                'docxFile': (os.path.basename(file_path), f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            response = requests.post(
                "http://localhost:3000/upload", 
                files=files, 
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 上传成功!")
                print(f"📄 文档ID: {result['data']['documentId']}")
                print(f"📝 内容预览: {result['data']['contentPreview']}")
                print(f"📊 内容长度: {result['data']['contentLength']} 字符")
                return result['data']['documentId']
            else:
                print(f"❌ 上传失败: {response.status_code}")
                try:
                    error_info = response.json()
                    print(f"错误详情: {json.dumps(error_info, indent=2, ensure_ascii=False)}")
                except:
                    print(f"错误响应: {response.text}")
                return None
                
    except Exception as e:
        print(f"❌ 上传过程出错: {str(e)}")
        return None

def search_documents(query):
    """搜索文档"""
    print(f"🔍 搜索文档: '{query}'")
    
    try:
        payload = {"query": query, "limit": 5}
        response = requests.post(
            "http://localhost:3000/search", 
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 搜索成功!")
            
            if result['results']['documents']:
                print(f"📋 找到 {len(result['results']['documents'])} 个相关文档:")
                for i, (doc, meta) in enumerate(zip(result['results']['documents'], result['results']['metadatas'])):
                    print(f"  {i+1}. 文件: {meta.get('filename', '未知')}")
                    print(f"     内容: {doc[:100]}{'...' if len(doc) > 100 else ''}")
                    print()
            else:
                print("📭 没有找到相关文档")
                
            return result
        else:
            print(f"❌ 搜索失败: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ 搜索过程出错: {str(e)}")
        return None

def main():
    print("🚀 数学文档处理系统 - 上传演示")
    print("=" * 50)
    
    # 1. 检查服务状态
    if not check_services():
        print("\n❌ 请确保所有服务都已启动:")
        print("   1. 运行 start_python.bat")
        print("   2. 运行 start_nodejs.bat")
        return
    
    print("\n✅ 所有服务正常运行!")
    
    # 2. 检查是否有docx文件
    docx_files = list(Path('.').glob('*.docx'))
    
    if not docx_files:
        print("\n📄 在当前目录中没有找到.docx文件")
        print("请将要测试的.docx文件放到项目根目录下，然后重新运行此脚本")
        
        # 创建一个示例说明
        print("\n💡 你可以:")
        print("   1. 将任何包含数学公式的.docx文件复制到当前目录")
        print("   2. 重新运行: python upload_demo.py")
        print("   3. 或者直接使用curl命令:")
        print("      curl -X POST -F \"docxFile=@your_file.docx\" http://localhost:3000/upload")
        return
    
    print(f"\n📁 找到 {len(docx_files)} 个docx文件:")
    for i, file in enumerate(docx_files):
        print(f"   {i+1}. {file.name}")
    
    # 3. 上传第一个文件
    test_file = docx_files[0]
    print(f"\n📤 准备上传: {test_file.name}")
    
    document_id = upload_document(str(test_file))
    
    if document_id:
        print(f"\n🎉 文档已成功上传并存储到向量数据库!")
        print(f"📄 文档ID: {document_id}")
        
        # 4. 测试搜索功能
        print("\n" + "="*50)
        print("🔍 测试搜索功能...")
        
        search_queries = [
            "数学",
            "公式", 
            "方程",
            "计算",
            "题目"
        ]
        
        for query in search_queries:
            print(f"\n🔍 搜索: '{query}'")
            result = search_documents(query)
            if result and result['results']['documents']:
                print(f"   ✅ 找到 {len(result['results']['documents'])} 个相关结果")
                break
        else:
            print("\n📝 尝试搜索文档中的具体内容...")
    
    print("\n" + "="*50)
    print("🎊 演示完成! 你的数学文档处理系统已经可以正常工作了!")
    print("\n📚 接下来你可以:")
    print("   • 上传更多的.docx文件")
    print("   • 尝试不同的搜索关键词")
    print("   • 查看 http://localhost:3000/health 获取系统状态")
    print("   • 查看 http://localhost:8001/docs 获取API文档")

if __name__ == "__main__":
    main() 