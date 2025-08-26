#!/usr/bin/env python3
"""
诊断文档解析和存储问题
"""

import requests
import json
from pathlib import Path

def check_services():
    """检查所有服务状态"""
    print("🔍 检查服务状态...")
    
    # 检查Node.js主服务
    try:
        response = requests.get("http://localhost:3000/health", timeout=3)
        print(f"✅ Node.js主服务: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Node.js主服务: {str(e)}")
        return False
    
    # 检查Python解析服务
    try:
        response = requests.get("http://localhost:8001/health", timeout=3)
        print(f"✅ Python解析服务: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Python解析服务: {str(e)}")
        return False
    
    return True

def check_database_content():
    """检查数据库中的实际内容"""
    print("\n📊 检查数据库内容...")
    
    try:
        # 获取数据库统计
        response = requests.get("http://localhost:3000/database/stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()['statistics']
            print(f"   📄 总文档数: {stats['totalDocuments']}")
            print(f"   💾 总存储量: {stats['totalStorage']} 字符")
            
            if stats['totalDocuments'] == 0:
                print("   ⚠️  数据库为空！")
                return False
        else:
            print(f"   ❌ 无法获取数据库统计: {response.status_code}")
            return False
        
        # 获取文档列表
        response = requests.get("http://localhost:3000/documents", timeout=5)
        if response.status_code == 200:
            data = response.json()
            documents = data['documents']
            
            if documents:
                print(f"\n📋 文档详情:")
                for i, doc in enumerate(documents, 1):
                    print(f"   📄 文档 {i}:")
                    print(f"      🆔 ID: {doc['id']}")
                    print(f"      📝 文件名: {doc['filename']}")
                    print(f"      📏 内容长度: {doc['contentLength']} 字符")
                    print(f"      📖 内容预览: {doc['contentPreview']}")
                    
                    # 检查是否包含目标文本
                    if "q为常数" in doc['contentPreview'] or "pn+q" in doc['contentPreview']:
                        print(f"      ✅ 包含目标文本")
                    else:
                        print(f"      ❌ 未包含目标文本")
                    print()
                    
                return True
            else:
                print("   📭 没有找到任何文档")
                return False
        else:
            print(f"   ❌ 无法获取文档列表: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 检查数据库内容时出错: {str(e)}")
        return False

def test_search_functionality():
    """测试搜索功能"""
    print("\n🔍 测试搜索功能...")
    
    test_queries = [
        "数列",
        "通项公式", 
        "等差数列",
        "q为常数",
        "pn+q",
        "公差"
    ]
    
    found_any = False
    
    for query in test_queries:
        try:
            payload = {"query": query, "limit": 3}
            response = requests.post("http://localhost:3000/search", json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result['results']['documents']:
                    print(f"   ✅ '{query}': 找到 {len(result['results']['documents'])} 个结果")
                    found_any = True
                    
                    # 显示第一个结果的内容片段
                    first_doc = result['results']['documents'][0]
                    print(f"      内容片段: {first_doc[:100]}...")
                else:
                    print(f"   ❌ '{query}': 无结果")
            else:
                print(f"   ❌ '{query}': 搜索失败 ({response.status_code})")
                
        except Exception as e:
            print(f"   ❌ '{query}': 搜索出错 - {str(e)}")
    
    return found_any

def test_direct_python_service():
    """直接测试Python解析服务"""
    print("\n🐍 直接测试Python解析服务...")
    
    # 查找docx文件
    docx_files = list(Path('.').glob('*.docx'))
    
    if not docx_files:
        print("   ❌ 没有找到.docx文件")
        return False
    
    test_file = docx_files[0]
    print(f"   📄 测试文件: {test_file.name}")
    
    try:
        with open(test_file, 'rb') as f:
            files = {'file': (test_file.name, f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
            response = requests.post("http://localhost:8001/parse-docx", files=files, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            content = result['content']
            
            print(f"   ✅ 解析成功，内容长度: {len(content)} 字符")
            
            # 检查是否包含目标文本
            target_texts = ["q为常数", "pn+q", "通项公式", "等差数列"]
            found_targets = []
            
            for target in target_texts:
                if target in content:
                    found_targets.append(target)
            
            if found_targets:
                print(f"   ✅ 找到目标文本: {', '.join(found_targets)}")
                print(f"   📖 内容预览:")
                print(f"      {content[:300]}...")
                return True
            else:
                print(f"   ❌ 未找到目标文本")
                print(f"   📖 实际内容预览:")
                print(f"      {content[:300]}...")
                return False
        else:
            print(f"   ❌ 解析失败: {response.status_code}")
            try:
                error = response.json()
                print(f"   错误: {error}")
            except:
                print(f"   错误响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ 测试出错: {str(e)}")
        return False

def main():
    print("🔧 诊断文档解析和存储问题")
    print("=" * 50)
    
    # 1. 检查服务状态
    if not check_services():
        print("\n❌ 服务未正常运行，请检查启动状态")
        return
    
    # 2. 直接测试Python解析服务
    python_ok = test_direct_python_service()
    
    # 3. 检查数据库内容
    db_ok = check_database_content()
    
    # 4. 测试搜索功能
    search_ok = test_search_functionality()
    
    print("\n" + "=" * 50)
    print("📋 诊断结果:")
    print(f"   🐍 Python解析服务: {'✅ 正常' if python_ok else '❌ 异常'}")
    print(f"   💾 数据库存储: {'✅ 正常' if db_ok else '❌ 异常'}")
    print(f"   🔍 搜索功能: {'✅ 正常' if search_ok else '❌ 异常'}")
    
    if not python_ok:
        print("\n🔧 建议解决方案:")
        print("   1. 检查Python服务的错误日志")
        print("   2. 确保enhanced_parser.py文件存在且正确")
        print("   3. 重启Python服务")
    elif not db_ok:
        print("\n🔧 建议解决方案:")
        print("   1. 重新上传文档: py upload_demo.py")
        print("   2. 检查Node.js服务日志")
    elif not search_ok:
        print("\n🔧 建议解决方案:")
        print("   1. 检查搜索算法的实现")
        print("   2. 尝试不同的搜索关键词")
    else:
        print("\n🎉 所有功能正常！")

if __name__ == "__main__":
    main() 