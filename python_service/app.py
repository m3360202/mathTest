from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from enhanced_parser import EnhancedDocxParser
except ImportError:
    # 如果增强解析器不可用，使用简化版本
    import docx
    import zipfile
    import xml.etree.ElementTree as ET
    import re
    
    class EnhancedDocxParser:
        def parse_document(self, docx_path: str):
            try:
                doc = docx.Document(docx_path)
                content_parts = []
                
                # 提取段落
                for paragraph in doc.paragraphs:
                    text = paragraph.text.strip()
                    if text:
                        content_parts.append(text)
                
                # 提取表格
                for table in doc.tables:
                    for row in table.rows:
                        row_text = []
                        for cell in row.cells:
                            cell_text = cell.text.strip()
                            if cell_text:
                                row_text.append(cell_text)
                        if row_text:
                            content_parts.append(" | ".join(row_text))
                
                content = "\n\n".join(content_parts)
                
                return {
                    'success': True,
                    'content': content,
                    'metadata': {
                        'ole_objects_count': 0,
                        'images_count': 0,
                        'math_formulas_count': 0,
                        'content_length': len(content)
                    }
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e),
                    'content': ''
                }

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="增强数学文档解析微服务",
    description="专门解析包含数学公式、OLE对象、图片的Word文档，转换为结构化内容",
    version="2.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局解析器实例
parser = EnhancedDocxParser()

@app.get("/")
async def root():
    """健康检查端点"""
    return {
        "message": "数学文档解析微服务正在运行",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.post("/parse-docx")
async def parse_docx(file: UploadFile = File(...)):
    """
    解析包含数学公式、OLE对象、图片的Word文档
    
    Args:
        file: 上传的.docx文件
    
    Returns:
        解析后的结构化内容，包含文本、公式、图片信息等
    """
    
    # 验证文件类型
    if not file.filename.endswith('.docx'):
        raise HTTPException(status_code=400, detail="只支持.docx格式的文件")
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        try:
            # 保存上传的文件
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
            
            logger.info(f"开始增强解析文件: {file.filename}")
            
            # 使用增强解析器解析文档
            result = parser.parse_document(tmp_path)
            
            if result['success']:
                logger.info(f"文件解析完成: {file.filename}")
                logger.info(f"提取到 {result['metadata']['ole_objects_count']} 个OLE对象")
                logger.info(f"提取到 {result['metadata']['images_count']} 个图片")
                logger.info(f"提取到 {result['metadata']['math_formulas_count']} 个数学公式")
                
                return {
                    "success": True,
                    "filename": file.filename,
                    "content": result['content'],
                    "content_length": len(result['content']),
                    "parsing_metadata": result['metadata']
                }
            else:
                raise HTTPException(status_code=500, detail=result['error'])
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"解析文件时发生未知错误: {str(e)}")
            raise HTTPException(status_code=500, detail=f"文件解析失败: {str(e)}")
        finally:
            # 清理临时文件
            try:
                os.unlink(tmp_path)
            except:
                pass

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "docx-parser"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True) 