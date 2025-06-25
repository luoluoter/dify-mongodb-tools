# 安装指南

## 环境要求

- Python 3.8+
- MongoDB 4.0+
- Docker (可选)

## 安装方式

### 方式一：直接安装

1. **克隆项目**

```bash
git clone <repository-url>
cd dify-mongodb-tools
```

2. **安装依赖**

```bash
pip install -r requirements.txt
```

3. **配置环境变量**

```bash
cp env.example .env
# 编辑 .env 文件，配置MongoDB连接信息
```

4. **运行应用**

```bash
python app.py
```

### 方式二：使用启动脚本

1. **克隆项目**

```bash
git clone <repository-url>
cd dify-mongodb-tools
```

2. **使用启动脚本**

```bash
# 检查环境
./start.sh --check

# 安装依赖
./start.sh --install

# 开发模式运行
./start.sh --dev

# 生产模式运行
./start.sh --prod
```

### 方式三：使用Makefile

```bash
# 安装依赖
make install

# 开发模式运行
make dev

# 生产模式运行
make prod

# 运行测试
make test
```

### 方式四：Docker部署

1. **构建镜像**

```bash
docker build -t dify-mongodb-tools .
```

2. **运行容器**

```bash
# 开发环境
docker run -d --restart=always -p 3333:3333 \
  --name dify-mongodb-tools \
  -v $PWD/.env:/app/.env \
  dify-mongodb-tools

# 生产环境
docker run -d \
  --restart=always \
  -p 3333:3333 \
  --name dify-mongodb-tools \
  -e FLASK_ENV=production \
  -e MONGO_URI=mongodb://your-mongo-host:27017/ \
  dify-mongodb-tools
```

## 环境变量配置

### 必需配置

```env
# MongoDB连接字符串
MONGO_URI=mongodb://localhost:27017/
```

### 可选配置

```env
# Flask应用配置
HOST=0.0.0.0
PORT=3333
DEBUG=false

# 日志配置
LOG_LEVEL=INFO

# 环境配置
FLASK_ENV=development
```

## 验证安装

安装完成后，可以通过以下方式验证：

1. **健康检查**

```bash
curl http://localhost:3333/api/health
```

2. **查看API信息**

```bash
curl http://localhost:3333/
```

## 常见问题

### Q: MongoDB连接失败

A: 检查MongoDB服务是否运行，以及连接字符串是否正确

### Q: 端口被占用

A: 修改.env文件中的PORT配置，或停止占用端口的服务

### Q: 权限问题

A: 确保对项目目录有读写权限，Docker用户需要适当的权限
