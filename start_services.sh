#!/bin/bash

# 数学文档处理系统启动脚本

set -e

echo "🚀 启动数学文档处理系统..."

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 创建必要的目录
echo "📁 创建必要目录..."
mkdir -p uploads logs chroma_config

# 复制环境变量文件
if [ ! -f .env ]; then
    echo "📋 创建环境变量文件..."
    cp .env.example .env
    echo "⚠️  请根据需要修改 .env 文件中的配置"
fi

# 启动服务的函数
start_with_docker() {
    echo "🐳 使用Docker Compose启动服务..."
    docker-compose up -d
    
    echo "⏳ 等待服务启动..."
    sleep 10
    
    # 检查服务状态
    echo "🔍 检查服务状态..."
    docker-compose ps
    
    echo "✅ 服务启动完成！"
    echo "🌐 主服务地址: http://localhost:3000"
    echo "🐍 Python服务地址: http://localhost:8001"
    echo "🗄️  ChromaDB地址: http://localhost:8000"
}

# 本地启动的函数
start_locally() {
    echo "💻 本地启动服务..."
    
    # 检查Node.js
    if ! command -v node &> /dev/null; then
        echo "❌ Node.js未安装，请先安装Node.js"
        exit 1
    fi
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python3未安装，请先安装Python3"
        exit 1
    fi
    
    # 启动ChromaDB
    echo "🗄️  启动ChromaDB..."
    if ! docker ps | grep -q chromadb; then
        docker run -d --name chromadb -p 8000:8000 chromadb/chroma:latest
    fi
    
    # 安装Node.js依赖
    if [ ! -d node_modules ]; then
        echo "📦 安装Node.js依赖..."
        npm install
    fi
    
    # 安装Python依赖
    if [ ! -d python_service/venv ]; then
        echo "🐍 创建Python虚拟环境..."
        cd python_service
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
        cd ..
    fi
    
    # 启动Python服务
    echo "🐍 启动Python服务..."
    cd python_service
    source venv/bin/activate
    uvicorn app:app --host 0.0.0.0 --port 8001 --reload &
    PYTHON_PID=$!
    cd ..
    
    # 等待Python服务启动
    sleep 5
    
    # 启动Node.js服务
    echo "🟢 启动Node.js服务..."
    npm start &
    NODE_PID=$!
    
    echo "✅ 服务启动完成！"
    echo "🌐 主服务地址: http://localhost:3000"
    echo "🐍 Python服务地址: http://localhost:8001"
    echo "🗄️  ChromaDB地址: http://localhost:8000"
    
    # 创建停止脚本
    cat > stop_services.sh << EOF
#!/bin/bash
echo "🛑 停止服务..."
kill $PYTHON_PID $NODE_PID 2>/dev/null || true
docker stop chromadb 2>/dev/null || true
echo "✅ 服务已停止"
EOF
    chmod +x stop_services.sh
    
    echo "📝 要停止服务，请运行: ./stop_services.sh"
}

# 检查启动方式
if [ "$1" == "local" ]; then
    start_locally
else
    start_with_docker
fi

echo ""
echo "🧪 测试服务："
echo "  健康检查: curl http://localhost:3000/health"
echo "  系统状态: curl http://localhost:3000/status"
echo "  使用测试客户端: python test_client.py --health"
echo ""
echo "📚 API文档："
echo "  主服务: http://localhost:3000"
echo "  Python服务: http://localhost:8001/docs" 