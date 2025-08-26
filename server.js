const express = require('express');
const axios = require('axios');
const multer = require('multer');
const cors = require('cors');
const fs = require('fs-extra');
const path = require('path');
const FormData = require('form-data');
const { v4: uuidv4 } = require('uuid');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;
const PYTHON_SERVICE_URL = process.env.PYTHON_SERVICE_URL || 'http://localhost:8001';
const CHROMA_URL = process.env.CHROMA_URL || 'http://localhost:8000';

// 中间件配置
app.use(cors());
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ extended: true, limit: '50mb' }));

// 配置文件上传
const upload = multer({ 
    dest: 'uploads/',
    limits: {
        fileSize: 50 * 1024 * 1024, // 50MB
    },
    fileFilter: (req, file, cb) => {
        if (file.mimetype === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document') {
            cb(null, true);
        } else {
            cb(new Error('只支持.docx格式的文件'), false);
        }
    }
});

// 简化的文档存储客户端
class DocumentStore {
    constructor() {
        this.documents = new Map(); // 临时内存存储，用于演示
        this.collectionName = 'math_documents';
    }

    async createCollection() {
        try {
            console.log('✅ 文档存储初始化成功');
            return { success: true };
        } catch (error) {
            console.error('❌ 文档存储初始化失败:', error.message);
            throw error;
        }
    }

    async addDocument(content, metadata = {}) {
        try {
            const documentId = uuidv4();
            
            // 生成简单的文档指纹用于搜索
            const fingerprint = this.generateFingerprint(content);
            
            const document = {
                id: documentId,
                content: content,
                metadata: { 
                    ...metadata, 
                    timestamp: new Date().toISOString(),
                    fingerprint: fingerprint
                }
            };
            
            this.documents.set(documentId, document);
            console.log(`📄 文档已存储: ${documentId}`);
            
            return { id: documentId, success: true };
        } catch (error) {
            console.error('❌ 存储文档失败:', error.message);
            throw error;
        }
    }

    async searchSimilar(query, limit = 5) {
        try {
            const queryFingerprint = this.generateFingerprint(query);
            const results = [];
            
            console.log(`🔍 搜索查询: "${query}"`);
            console.log(`📊 数据库中有 ${this.documents.size} 个文档`);
            
            // 1. 基于指纹的相似度搜索
            for (const [id, doc] of this.documents) {
                const similarity = this.calculateSimilarity(queryFingerprint, doc.metadata.fingerprint);
                if (similarity > 0.05) { // 降低阈值
                    results.push({
                        id: id,
                        document: doc.content,
                        metadata: doc.metadata,
                        similarity: similarity,
                        matchType: 'fingerprint'
                    });
                }
            }
            
            // 2. 如果指纹搜索结果不够，使用直接文本搜索
            if (results.length < limit) {
                const queryLower = query.toLowerCase();
                
                for (const [id, doc] of this.documents) {
                    // 避免重复添加
                    if (results.some(r => r.id === id)) continue;
                    
                    const contentLower = doc.content.toLowerCase();
                    if (contentLower.includes(queryLower)) {
                        // 计算匹配程度
                        const matches = (contentLower.match(new RegExp(queryLower.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g')) || []).length;
                        const similarity = Math.min(matches * 0.1, 0.8); // 最高0.8分
                        
                        results.push({
                            id: id,
                            document: doc.content,
                            metadata: doc.metadata,
                            similarity: similarity,
                            matchType: 'direct'
                        });
                    }
                }
            }
            
            // 3. 如果还是没有结果，尝试部分匹配
            if (results.length === 0) {
                const queryWords = query.toLowerCase().split(/\s+/).filter(w => w.length > 1);
                
                for (const [id, doc] of this.documents) {
                    const contentLower = doc.content.toLowerCase();
                    let matchCount = 0;
                    
                    for (const word of queryWords) {
                        if (contentLower.includes(word)) {
                            matchCount++;
                        }
                    }
                    
                    if (matchCount > 0) {
                        const similarity = (matchCount / queryWords.length) * 0.5; // 部分匹配降权
                        results.push({
                            id: id,
                            document: doc.content,
                            metadata: doc.metadata,
                            similarity: similarity,
                            matchType: 'partial'
                        });
                    }
                }
            }
            
            // 按相似度排序并限制结果数量
            results.sort((a, b) => b.similarity - a.similarity);
            const limitedResults = results.slice(0, limit);
            
            console.log(`✅ 找到 ${limitedResults.length} 个相关文档`);
            if (limitedResults.length > 0) {
                console.log(`📈 匹配类型分布: ${limitedResults.map(r => r.matchType).join(', ')}`);
            }
            
            return {
                documents: limitedResults.map(r => r.document),
                metadatas: limitedResults.map(r => r.metadata),
                distances: limitedResults.map(r => 1 - r.similarity),
                ids: limitedResults.map(r => r.id)
            };
        } catch (error) {
            console.error('❌ 搜索失败:', error.message);
            throw error;
        }
    }

    generateFingerprint(text) {
        // 生成文本指纹用于相似度计算
        const words = text.toLowerCase()
            .replace(/[^\u4e00-\u9fa5\w\s]/g, '') // 保留中文、英文、数字
            .split(/\s+/)
            .filter(word => word.length > 1);
        
        const fingerprint = new Map();
        words.forEach(word => {
            fingerprint.set(word, (fingerprint.get(word) || 0) + 1);
        });
        
        return fingerprint;
    }

    calculateSimilarity(fp1, fp2) {
        // 改进的相似度计算，包含简单的文本包含检查
        const keys1 = new Set(fp1.keys());
        const keys2 = new Set(fp2.keys());
        const intersection = new Set([...keys1].filter(k => keys2.has(k)));
        
        // 如果有交集，计算余弦相似度
        if (intersection.size > 0) {
            let dotProduct = 0;
            let norm1 = 0;
            let norm2 = 0;
            
            for (const key of intersection) {
                const val1 = fp1.get(key) || 0;
                const val2 = fp2.get(key) || 0;
                dotProduct += val1 * val2;
            }
            
            for (const val of fp1.values()) {
                norm1 += val * val;
            }
            for (const val of fp2.values()) {
                norm2 += val * val;
            }
            
            if (norm1 > 0 && norm2 > 0) {
                return dotProduct / (Math.sqrt(norm1) * Math.sqrt(norm2));
            }
        }
        
        // 如果余弦相似度为0，尝试简单的包含匹配
        const query_words = Array.from(keys1);
        const doc_words = Array.from(keys2);
        
        let matches = 0;
        for (const query_word of query_words) {
            for (const doc_word of doc_words) {
                if (doc_word.includes(query_word) || query_word.includes(doc_word)) {
                    matches++;
                    break;
                }
            }
        }
        
        return matches > 0 ? matches / query_words.length * 0.3 : 0; // 降权的包含匹配
    }
}

// 初始化文档存储客户端
const documentStore = new DocumentStore();

// API路由

/**
 * 健康检查
 */
app.get('/health', (req, res) => {
    res.json({ 
        status: 'healthy', 
        service: 'math-document-processor-main',
        timestamp: new Date().toISOString()
    });
});

/**
 * 获取系统状态
 */
app.get('/status', async (req, res) => {
    try {
        // 检查Python服务状态
        const pythonServiceStatus = await axios.get(`${PYTHON_SERVICE_URL}/health`)
            .then(() => 'healthy')
            .catch(() => 'unhealthy');

        // 检查文档存储状态
        const storeStatus = 'healthy'; // 内存存储始终可用

        res.json({
            mainService: 'healthy',
            pythonService: pythonServiceStatus,
            documentStore: storeStatus,
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        res.status(500).json({
            error: 'Error checking system status',
            details: error.message
        });
    }
});

/**
 * 文档上传和处理
 */
app.post('/upload', upload.single('docxFile'), async (req, res) => {
    if (!req.file) {
        return res.status(400).json({ error: 'No file uploaded' });
    }

    let tempFilePath = req.file.path;

    try {
        console.log(`Processing file: ${req.file.originalname}`);

        // 1. 调用Python解析微服务
        const formData = new FormData();
        const fileStream = fs.createReadStream(tempFilePath);
        formData.append('file', fileStream, {
            filename: req.file.originalname,
            contentType: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        });

        const parseResponse = await axios.post(`${PYTHON_SERVICE_URL}/parse-docx`, formData, {
            headers: {
                ...formData.getHeaders(),
                'Content-Type': 'multipart/form-data'
            },
            maxContentLength: Infinity,
            maxBodyLength: Infinity,
            timeout: 30000 // 30秒超时
        });

        if (!parseResponse.data.success) {
            throw new Error(parseResponse.data.error || 'Python service parsing failed');
        }

        const parsedContent = parseResponse.data.content;
        console.log(`Parsed content length: ${parsedContent.length}`);

        // 2. 确保文档存储初始化
        await documentStore.createCollection();

        // 3. 添加到文档存储
        const metadata = {
            filename: req.file.originalname,
            filesize: req.file.size,
            mimetype: req.file.mimetype,
            uploadedAt: new Date().toISOString(),
            contentLength: parsedContent.length
        };

        const dbResult = await documentStore.addDocument(parsedContent, metadata);

        // 4. 返回成功响应
        res.json({
            success: true,
            message: 'File processed and stored successfully',
            data: {
                documentId: dbResult.id,
                filename: req.file.originalname,
                contentPreview: parsedContent.substring(0, 200) + (parsedContent.length > 200 ? '...' : ''),
                contentLength: parsedContent.length,
                metadata: metadata
            }
        });

    } catch (error) {
        console.error('Processing error:', error);
        
        let errorMessage = 'Error processing file';
        let statusCode = 500;

        if (error.response) {
            errorMessage = error.response.data?.detail || error.response.data?.error || errorMessage;
            statusCode = error.response.status || 500;
        } else if (error.message) {
            errorMessage = error.message;
        }

        res.status(statusCode).json({
            success: false,
            error: errorMessage,
            filename: req.file?.originalname
        });

    } finally {
        // 清理临时文件
        try {
            await fs.remove(tempFilePath);
        } catch (cleanupError) {
            console.error('Error cleaning up temp file:', cleanupError);
        }
    }
});

/**
 * 语义搜索
 */
app.post('/search', async (req, res) => {
    try {
        const { query, limit = 5 } = req.body;

        if (!query || typeof query !== 'string') {
            return res.status(400).json({ error: 'Query is required and must be a string' });
        }

        console.log(`Searching for: ${query}`);

        const searchResults = await documentStore.searchSimilar(query, parseInt(limit));

        res.json({
            success: true,
            query: query,
            results: searchResults,
            timestamp: new Date().toISOString()
        });

    } catch (error) {
        console.error('Search error:', error);
        res.status(500).json({
            success: false,
            error: 'Error performing search',
            details: error.message
        });
    }
});

/**
 * 获取所有文档列表
 */
app.get('/documents', async (req, res) => {
    try {
        const documents = [];
        
        // 从内存存储中获取所有文档
        for (const [id, doc] of documentStore.documents) {
            documents.push({
                id: id,
                filename: doc.metadata.filename,
                uploadedAt: doc.metadata.timestamp,
                contentLength: doc.content.length,
                contentPreview: doc.content.substring(0, 100) + (doc.content.length > 100 ? '...' : ''),
                metadata: doc.metadata
            });
        }

        res.json({
            success: true,
            totalDocuments: documents.length,
            documents: documents,
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        console.error('Error fetching documents:', error);
        res.status(500).json({
            success: false,
            error: 'Error fetching documents',
            details: error.message
        });
    }
});

/**
 * 根据ID获取特定文档
 */
app.get('/documents/:id', async (req, res) => {
    try {
        const documentId = req.params.id;
        
        if (documentStore.documents.has(documentId)) {
            const doc = documentStore.documents.get(documentId);
            res.json({
                success: true,
                document: {
                    id: documentId,
                    content: doc.content,
                    metadata: doc.metadata
                }
            });
        } else {
            res.status(404).json({
                success: false,
                error: 'Document not found',
                id: documentId
            });
        }
    } catch (error) {
        console.error('Error fetching document:', error);
        res.status(500).json({
            success: false,
            error: 'Error fetching document',
            details: error.message
        });
    }
});

/**
 * 获取数据库统计信息
 */
app.get('/database/stats', async (req, res) => {
    try {
        const stats = {
            totalDocuments: documentStore.documents.size,
            totalStorage: 0,
            averageContentLength: 0,
            fileTypes: {},
            uploadDates: []
        };

        let totalContentLength = 0;
        
        for (const [id, doc] of documentStore.documents) {
            totalContentLength += doc.content.length;
            
            // 统计文件类型
            const filename = doc.metadata.filename || 'unknown';
            const ext = filename.split('.').pop() || 'unknown';
            stats.fileTypes[ext] = (stats.fileTypes[ext] || 0) + 1;
            
            // 收集上传日期
            if (doc.metadata.timestamp) {
                stats.uploadDates.push(doc.metadata.timestamp);
            }
        }

        stats.averageContentLength = stats.totalDocuments > 0 ? 
            Math.round(totalContentLength / stats.totalDocuments) : 0;
        stats.totalStorage = totalContentLength;

        res.json({
            success: true,
            statistics: stats,
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        console.error('Error fetching database stats:', error);
        res.status(500).json({
            success: false,
            error: 'Error fetching database statistics',
            details: error.message
        });
    }
});

// 错误处理中间件
app.use((error, req, res, next) => {
    if (error instanceof multer.MulterError) {
        if (error.code === 'LIMIT_FILE_SIZE') {
            return res.status(400).json({ error: 'File size too large (max 50MB)' });
        }
    }
    
    console.error('Unhandled error:', error);
    res.status(500).json({ 
        error: 'Internal server error',
        details: error.message 
    });
});

// 404处理
app.use('*', (req, res) => {
    res.status(404).json({ error: 'Endpoint not found' });
});

// 启动服务器
app.listen(PORT, async () => {
    console.log(`🚀 Math Document Processor Main Service running on port ${PORT}`);
    console.log(`📄 Python Service URL: ${PYTHON_SERVICE_URL}`);
    console.log(`🗄️  ChromaDB URL: ${CHROMA_URL}`);
    
    // 初始化文档存储
    try {
        await documentStore.createCollection();
        console.log('✅ 文档存储已初始化');
    } catch (error) {
        console.error('❌ 文档存储初始化失败:', error.message);
    }
});

// 优雅关闭
process.on('SIGTERM', () => {
    console.log('SIGTERM received, shutting down gracefully');
    process.exit(0);
});

process.on('SIGINT', () => {
    console.log('SIGINT received, shutting down gracefully');
    process.exit(0);
}); 