#!/usr/bin/env python3
"""
向量数据库查看器
用于查看、管理存储在系统中的文档
"""

import requests
import json
from datetime import datetime
import os

class DatabaseViewer:
    def __init__(self, base_url="http://localhost:3000"):
        self.base_url = base_url.rstrip('/')
    
    def get_system_status(self):
        """获取系统状态"""
        try:
            response = requests.get(f"{self.base_url}/status")
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None
    
    def search_all_documents(self, query="", limit=20):
        """搜索所有文档（使用空查询或通用查询）"""
        try:
            # 使用常见词汇进行搜索，获取更多结果
            search_queries = [query] if query else [
                "数学", "公式", "方程", "函数", "计算", "题目", 
                "解", "求", "已知", "设", "证明", "a", "x", "1"
            ]
            
            all_results = {}
            for search_query in search_queries:
                payload = {"query": search_query, "limit": limit}
                response = requests.post(f"{self.base_url}/search", json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('results', {}).get('documents'):
                        all_results[search_query] = result['results']
            
            return all_results
        except Exception as e:
            print(f"❌ 搜索失败: {str(e)}")
            return {}
    
    def get_document_by_id(self, doc_id):
        """通过ID获取特定文档（模拟功能）"""
        # 由于我们使用的是简化的内存存储，这里通过搜索来查找
        all_docs = self.search_all_documents(limit=100)
        
        for query, results in all_docs.items():
            if results.get('metadatas'):
                for i, metadata in enumerate(results['metadatas']):
                    if str(metadata.get('timestamp', '')).find(doc_id[:8]) != -1:
                        return {
                            'id': doc_id,
                            'document': results['documents'][i],
                            'metadata': metadata,
                            'found_via_query': query
                        }
        return None
    
    def display_all_documents(self):
        """显示所有存储的文档"""
        print("📚 查看向量数据库中的所有文档")
        print("=" * 60)
        
        # 获取系统状态
        status = self.get_system_status()
        if status:
            print(f"🟢 系统状态: {status}")
            print()
        
        # 搜索所有文档
        print("🔍 正在搜索数据库中的所有文档...")
        all_results = self.search_all_documents()
        
        if not all_results:
            print("📭 数据库中没有找到任何文档")
            print("💡 请先使用 upload_demo.py 上传一些文档")
            return
        
        # 去重并整理文档
        unique_docs = {}
        for query, results in all_results.items():
            if results.get('documents'):
                for i, doc in enumerate(results['documents']):
                    metadata = results['metadatas'][i] if i < len(results['metadatas']) else {}
                    doc_key = f"{metadata.get('filename', 'unknown')}_{len(doc)}"
                    
                    if doc_key not in unique_docs:
                        unique_docs[doc_key] = {
                            'document': doc,
                            'metadata': metadata,
                            'found_queries': [query]
                        }
                    else:
                        unique_docs[doc_key]['found_queries'].append(query)
        
        print(f"📊 找到 {len(unique_docs)} 个唯一文档:")
        print()
        
        for i, (doc_key, doc_info) in enumerate(unique_docs.items(), 1):
            metadata = doc_info['metadata']
            document = doc_info['document']
            
            print(f"📄 文档 {i}:")
            print(f"   📝 文件名: {metadata.get('filename', '未知')}")
            print(f"   📅 上传时间: {metadata.get('uploadedAt', metadata.get('timestamp', '未知'))}")
            print(f"   📊 文件大小: {metadata.get('filesize', '未知')} bytes")
            print(f"   📏 内容长度: {metadata.get('contentLength', len(document))} 字符")
            print(f"   🔍 匹配查询: {', '.join(doc_info['found_queries'][:3])}{'...' if len(doc_info['found_queries']) > 3 else ''}")
            
            # 显示内容预览
            preview = document[:200] + "..." if len(document) > 200 else document
            print(f"   📖 内容预览:")
            print(f"      {preview}")
            print()
    
    def search_documents_interactive(self):
        """交互式搜索文档"""
        print("🔍 交互式文档搜索")
        print("=" * 40)
        
        while True:
            query = input("\n请输入搜索关键词 (输入 'quit' 退出): ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                break
            
            if not query:
                print("请输入有效的搜索关键词")
                continue
            
            print(f"\n🔍 搜索: '{query}'")
            
            try:
                payload = {"query": query, "limit": 5}
                response = requests.post(f"{self.base_url}/search", json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result['results']['documents']:
                        print(f"✅ 找到 {len(result['results']['documents'])} 个相关文档:")
                        
                        for i, (doc, metadata, distance) in enumerate(zip(
                            result['results']['documents'],
                            result['results']['metadatas'],
                            result['results']['distances']
                        )):
                            print(f"\n📄 结果 {i+1}:")
                            print(f"   📝 文件: {metadata.get('filename', '未知')}")
                            print(f"   🎯 相似度: {1-distance:.2%}")
                            print(f"   📖 内容: {doc[:150]}{'...' if len(doc) > 150 else ''}")
                    else:
                        print("📭 没有找到相关文档")
                        print("💡 尝试使用其他关键词，如：数学、公式、方程、函数等")
                else:
                    print(f"❌ 搜索失败: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ 搜索出错: {str(e)}")
    
    def export_database_info(self):
        """导出数据库信息到文件"""
        print("💾 导出数据库信息...")
        
        all_results = self.search_all_documents()
        
        if not all_results:
            print("📭 没有数据可导出")
            return
        
        # 准备导出数据
        export_data = {
            'export_time': datetime.now().isoformat(),
            'total_queries': len(all_results),
            'documents': []
        }
        
        # 去重并整理文档
        unique_docs = {}
        for query, results in all_results.items():
            if results.get('documents'):
                for i, doc in enumerate(results['documents']):
                    metadata = results['metadatas'][i] if i < len(results['metadatas']) else {}
                    doc_key = f"{metadata.get('filename', 'unknown')}_{len(doc)}"
                    
                    if doc_key not in unique_docs:
                        unique_docs[doc_key] = {
                            'document': doc,
                            'metadata': metadata,
                            'found_queries': [query]
                        }
        
        export_data['documents'] = list(unique_docs.values())
        
        # 保存到文件
        filename = f"database_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 数据库信息已导出到: {filename}")
            print(f"📊 导出了 {len(unique_docs)} 个文档的信息")
        except Exception as e:
            print(f"❌ 导出失败: {str(e)}")

def main():
    viewer = DatabaseViewer()
    
    while True:
        print("\n" + "="*50)
        print("📚 向量数据库查看器")
        print("="*50)
        print("1. 查看所有文档")
        print("2. 交互式搜索")
        print("3. 导出数据库信息")
        print("4. 系统状态")
        print("0. 退出")
        print()
        
        choice = input("请选择操作 (0-4): ").strip()
        
        if choice == '1':
            viewer.display_all_documents()
        elif choice == '2':
            viewer.search_documents_interactive()
        elif choice == '3':
            viewer.export_database_info()
        elif choice == '4':
            status = viewer.get_system_status()
            if status:
                print("🟢 系统状态:")
                print(json.dumps(status, indent=2, ensure_ascii=False))
            else:
                print("❌ 无法获取系统状态")
        elif choice == '0':
            print("👋 再见！")
            break
        else:
            print("❌ 无效选择，请重试")
        
        input("\n按回车键继续...")

if __name__ == "__main__":
    main() 