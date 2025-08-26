#!/usr/bin/env python3
"""
测试增强解析器的功能
"""

import requests
import json
import os
from pathlib import Path

def test_enhanced_parsing():
    """测试增强解析功能"""
    print("🧪 测试增强文档解析功能")
    print("=" * 50)
    
    # 查找docx文件
    docx_files = list(Path('.').glob('*.docx'))
    
    if not docx_files:
        print("❌ 没有找到.docx文件进行测试")
        print("请将包含数学公式、图片、OLE对象的.docx文件放到当前目录")
        return
    
    test_file = docx_files[0]
    print(f"📄 测试文件: {test_file.name}")
    
    try:
        # 检查Python服务状态
        print("\n🔍 检查Python解析服务状态...")
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code != 200:
            print("❌ Python服务未运行，请先启动 start_python.bat")
            return
        print("✅ Python服务正常运行")
        
        # 上传文件进行解析
        print(f"\n📤 上传并解析文件: {test_file.name}")
        
        with open(test_file, 'rb') as f:
            files = {'file': (test_file.name, f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
            response = requests.post("http://localhost:8001/parse-docx", files=files, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 解析成功!")
            
            # 显示解析结果
            print(f"\n📊 解析统计:")
            if 'parsing_metadata' in result:
                metadata = result['parsing_metadata']
                print(f"   📄 内容长度: {metadata['content_length']} 字符")
                print(f"   🔗 OLE对象数量: {metadata['ole_objects_count']}")
                print(f"   🖼️  图片数量: {metadata['images_count']}")
                print(f"   🧮 数学公式数量: {metadata['math_formulas_count']}")
            
            # 显示内容预览
            content = result['content']
            print(f"\n📖 内容预览 (前500字符):")
            print("-" * 50)
            print(content[:500])
            if len(content) > 500:
                print("...")
            print("-" * 50)
            
            # 检查是否包含OLE和图片信息
            if "OLE对象" in content:
                print("✅ 成功检测到OLE对象")
            else:
                print("⚠️  未检测到OLE对象")
            
            if "图片" in content:
                print("✅ 成功检测到图片信息")
            else:
                print("⚠️  未检测到图片")
            
            if "数学" in content or "$" in content:
                print("✅ 成功检测到数学内容")
            else:
                print("⚠️  未检测到数学内容")
            
            # 测试搜索功能
            print(f"\n🔍 测试搜索功能...")
            test_search_queries = ["数学", "公式", "等差数列", "图片", "OLE"]
            
            for query in test_search_queries:
                if query in content:
                    print(f"   ✅ '{query}' - 可以搜索到")
                else:
                    print(f"   ❌ '{query}' - 搜索不到")
            
            return True
            
        else:
            print(f"❌ 解析失败: {response.status_code}")
            try:
                error_info = response.json()
                print(f"错误详情: {json.dumps(error_info, indent=2, ensure_ascii=False)}")
            except:
                print(f"错误响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程出错: {str(e)}")
        return False

def main():
    success = test_enhanced_parsing()
    
    print(f"\n{'='*50}")
    if success:
        print("🎉 增强解析器测试成功!")
        print("\n💡 接下来你可以:")
        print("   1. 重新上传文档到主服务: python upload_demo.py")
        print("   2. 测试搜索功能: python test_client.py --search '你的搜索词'")
        print("   3. 查看数据库内容: python quick_view.py")
    else:
        print("❌ 增强解析器测试失败")
        print("\n🔧 请检查:")
        print("   1. Python服务是否正常运行")
        print("   2. 文档文件是否存在且格式正确")
        print("   3. 查看Python服务的错误日志")

if __name__ == "__main__":
    main() 