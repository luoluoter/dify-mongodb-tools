# Dify MongoDB Tools

一个用于与MongoDB交互的Flask应用，提供数据写入和查询功能，支持Dify工具集集成。

## ✨ 功能特性

- 🔄 **数据保存**: 支持任意结构数据的写入和更新
- 📊 **灵活查询**: 支持复杂查询条件、排序和分页
- 🗄️ **多数据库支持**: 完全动态的数据库和集合操作
- 🔍 **健康检查**: 提供应用和数据库连接状态监控
- 🛡️ **错误处理**: 完善的错误处理和日志记录

## 🚀 快速开始

### 环境要求

- Docker 20.0+
- MongoDB 4.0+

### 推荐部署方式 (Docker)

```bash
# 克隆项目
git clone https://github.com/luoluoter/dify-mongodb-tools.git
cd dify-mongodb-tools

# 使用Docker一键部署
bash start.sh --docker

# 指定端口部署（避免端口冲突）
PORT=3388 bash start.sh --docker  # 使用8080端口
```

### 其他部署方式

- [📖 手动安装指南](docs/installation.md) - Python环境安装和配置
- [🐳 Docker详细部署](docs/docker.md) - Docker部署详细说明
- [🔧 开发环境设置](docs/development.md) - 开发环境配置

## 📖 使用示例

> **注意**：下面示例中需要用实际部署的IP和端口

### 保存数据

```bash
curl -X POST http://localhost:3333/api/save \
  -H "Content-Type: application/json" \
  -d '{
    "db_name": "my_db",
    "collection_name": "my_collection",
    "title": "测试数据",
    "content": "{\"name\": \"张三\", \"age\": 25}"
  }'
```

### 查询数据

```bash
curl "http://localhost:3333/api/search?db_name=my_db&collection_name=my_collection&conditions=%7B%7D&limit=10"
```

### 健康检查

```bash
curl http://localhost:3333/api/health
```

## 📚 文档

- [📖 安装指南](docs/installation.md) - 详细的安装和配置说明
- [🔧 API文档](docs/api.md) - 完整的API接口文档
- [💻 开发指南](docs/development.md) - 开发环境设置和贡献指南

## 🛠️ 开发工具

```bash
# 使用启动脚本
bash start.sh --docker   # Docker一键部署 (推荐)
bash start.sh --install  # 安装依赖
bash start.sh --dev      # 开发模式运行
bash start.sh --prod     # 生产模式运行
```

## 🔧 Dify集成

### schema.json 文件

项目根目录下的 `schema.json` 文件是用于 **Dify 创建自定义工具时导入的 OpenAPI 规范文件**。

#### 使用方法

1. **在Dify中创建自定义工具**：
   - 登录Dify管理后台
   - 进入"工具" → "自定义工具"
   - 点击"创建工具"

2. **导入API规范**：
   - 选择"导入OpenAPI规范"
   - 上传或粘贴 `schema.json` 文件内容
   - Dify会自动解析API接口并生成工具配置

3. **配置工具参数**：
   - 根据实际需求调整数据库连接信息
   - 配置必要的认证信息
   - 测试工具连接

#### 支持的API接口

- **POST /api/save** - 保存数据到指定数据库和集合
- **GET /api/search** - 搜索数据，支持复杂查询条件
- **GET /api/health** - 健康检查

#### 注意事项

- 确保Dify能够访问到MongoDB Tools服务
- 根据实际部署环境修改schema.json中的服务器URL
- **端口配置**：如果使用了自定义端口（如8080、9000等），需要在schema.json中更新对应的URL
- 建议在生产环境中配置适当的认证机制

## 📋 API端点

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/api/save` | 保存数据到指定数据库和集合 |
| GET | `/api/search` | 搜索数据，支持复杂查询 |
| GET | `/api/health` | 健康检查 |

## 🤝 贡献

欢迎贡献代码！请查看 [开发指南](docs/development.md) 了解详情。

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🆘 支持

- 📖 [文档](docs/)
- 🐛 [Issues](https://github.com/luoluoter/dify-mongodb-tools/issues)
- 💬 联系维护者
