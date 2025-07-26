#!/bin/bash

echo "🚀 设置Google Cloud CLI for VEO 3.0"
echo "=================================="

# 检查操作系统
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "📱 检测到macOS系统"
    
    # 检查是否安装了Homebrew
    if ! command -v brew &> /dev/null; then
        echo "❌ Homebrew未安装，请先安装Homebrew:"
        echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi
    
    echo "🍺 使用Homebrew安装Google Cloud CLI..."
    brew install --cask google-cloud-sdk
    
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🐧 检测到Linux系统"
    
    # 下载并安装gcloud
    curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-linux-x86_64.tar.gz
    tar -xf google-cloud-cli-linux-x86_64.tar.gz
    ./google-cloud-sdk/install.sh
    
else
    echo "❌ 不支持的操作系统: $OSTYPE"
    echo "请手动安装Google Cloud CLI: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

echo ""
echo "✅ Google Cloud CLI安装完成"
echo ""

# 初始化gcloud
echo "🔧 初始化gcloud配置..."
gcloud init

echo ""
echo "🔐 设置认证..."

# 登录
gcloud auth login

# 设置应用默认凭据
gcloud auth application-default login

# 设置项目
echo "📋 设置项目..."
gcloud config set project central-diode-467003-e0

# 启用必要的API
echo "🔌 启用必要的API..."
gcloud services enable aiplatform.googleapis.com
gcloud services enable compute.googleapis.com

echo ""
echo "✅ 设置完成！"
echo ""
echo "🧪 测试配置:"
echo "   python test_veo3_vertex_ai.py"
echo ""
echo "📖 更多信息:"
echo "   VEO 3.0模型: https://console.cloud.google.com/vertex-ai/publishers/google/model-garden/veo-3.0-generate-preview"