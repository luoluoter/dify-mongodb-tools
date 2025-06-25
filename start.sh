#!/bin/bash

# Dify MongoDB Tools 启动脚本
# 支持开发和生产环境

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Python版本
check_python_version() {
    log_info "检查Python版本..."
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装"
        exit 1
    fi
    
    python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    required_version="3.8"
    
    if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
        log_error "Python版本过低，需要 $required_version 或更高版本，当前版本: $python_version"
        exit 1
    fi
    
    log_success "Python版本检查通过: $python_version"
}

# 检查依赖
check_dependencies() {
    log_info "检查依赖..."
    
    if [ ! -f "requirements.txt" ]; then
        log_error "requirements.txt 文件不存在"
        exit 1
    fi
    
    log_success "依赖文件检查通过"
}

# 安装依赖
install_dependencies() {
    log_info "安装Python依赖..."
    
    if [ ! -d "venv" ]; then
        log_info "创建虚拟环境..."
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    
    log_info "升级pip..."
    pip install --upgrade pip
    
    log_info "安装依赖包..."
    pip install -r requirements.txt
    
    log_success "依赖安装完成"
}

# 检查环境变量
check_environment() {
    log_info "检查环境变量..."
    
    if [ ! -f ".env" ]; then
        log_warning ".env 文件不存在，使用默认配置"
        return 0
    fi
    
    # 检查必要的环境变量
    if grep -q "MONGO_URI" .env; then
        log_success "MongoDB URI 已配置"
    else
        log_warning "MongoDB URI 未配置，将使用默认值"
    fi
    
    if grep -q "DB_NAME" .env; then
        log_success "数据库名称已配置"
    else
        log_warning "数据库名称未配置，将使用默认值"
    fi
}

# 检查MongoDB连接
check_mongodb_connection() {
    log_info "检查MongoDB连接..."
    
    # 从.env文件读取MongoDB URI
    if [ -f ".env" ]; then
        source .env
    fi
    
    MONGO_URI=${MONGO_URI:-"mongodb://localhost:27017/"}
    
    # 尝试连接MongoDB
    if command -v mongosh &> /dev/null; then
        if mongosh --quiet --eval "db.runCommand('ping')" "$MONGO_URI" &> /dev/null; then
            log_success "MongoDB连接成功"
        else
            log_warning "MongoDB连接失败，请检查MongoDB服务是否运行"
        fi
    else
        log_warning "mongosh 未安装，跳过MongoDB连接检查"
    fi
}

# 启动应用
start_application() {
    log_info "启动应用..."
    
    # 设置环境变量
    export FLASK_ENV=${FLASK_ENV:-"development"}
    export PYTHONPATH="${PYTHONPATH}:$(pwd)"
    
    # 激活虚拟环境
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    # 启动应用
    log_success "应用启动中..."
    python app.py
}

# 显示帮助信息
show_help() {
    echo "Dify MongoDB Tools 启动脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help     显示此帮助信息"
    echo "  -c, --check    仅检查环境和依赖"
    echo "  -i, --install  安装依赖"
    echo "  -d, --dev      开发模式启动"
    echo "  -p, --prod     生产模式启动"
    echo "  --docker       一键部署Docker容器"
    echo ""
    echo "示例:"
    echo "  $0              # 默认启动"
    echo "  $0 --check      # 检查环境"
    echo "  $0 --install    # 安装依赖"
    echo "  $0 --dev        # 开发模式"
}

# 新增：Docker一键部署
run_docker() {
    IMAGE_NAME="dify-mongodb-tools"
    CONTAINER_NAME="dify-mongodb-tools"
    PORT=${PORT:-3333}
    echo "[INFO] 检查是否存在同名容器 $CONTAINER_NAME..."
    if docker ps -a --format '{{.Names}}' | grep -wq "$CONTAINER_NAME"; then
        echo "[INFO] 存在同名容器，正在删除..."
        docker stop "$CONTAINER_NAME" >/dev/null 2>&1
        docker rm "$CONTAINER_NAME" >/dev/null 2>&1
        echo "[INFO] 已删除旧容器 $CONTAINER_NAME"
    fi
    echo "[INFO] 构建镜像 $IMAGE_NAME..."
    docker build -t "$IMAGE_NAME" . || { echo "[ERROR] 镜像构建失败"; exit 1; }
    echo "[INFO] 启动新容器 $CONTAINER_NAME..."
    docker run -d --restart=always -p $PORT:3333 \
        --name "$CONTAINER_NAME" \
        -v "$PWD/.env:/app/.env" \
        "$IMAGE_NAME"
    if [ $? -eq 0 ]; then
        echo "[SUCCESS] 容器 $CONTAINER_NAME 已启动，端口映射 $PORT:3333"
    else
        echo "[ERROR] 容器启动失败"
        exit 1
    fi
}

# 主函数
main() {
    case "${1:-}" in
        -h|--help)
            show_help
            exit 0
            ;;
        -c|--check)
            check_python_version
            check_dependencies
            check_environment
            check_mongodb_connection
            log_success "环境检查完成"
            exit 0
            ;;
        -i|--install)
            check_python_version
            check_dependencies
            install_dependencies
            exit 0
            ;;
        -d|--dev)
            export FLASK_ENV=development
            ;;
        -p|--prod)
            export FLASK_ENV=production
            ;;
        --docker)
            run_docker
            exit 0
            ;;
        "")
            # 默认行为
            ;;
        *)
            log_error "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
    
    # 执行启动流程
    check_python_version
    check_dependencies
    check_environment
    check_mongodb_connection
    
    # 如果没有虚拟环境，提示安装依赖
    if [ ! -d "venv" ]; then
        log_warning "虚拟环境不存在，请先运行: $0 --install"
        exit 1
    fi
    
    start_application
}

# 捕获中断信号
trap 'log_info "应用被中断"; exit 0' INT TERM

# 执行主函数
main "$@"
