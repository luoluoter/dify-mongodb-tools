# 开发指南

## 项目结构

```
dify-mongodb-tools/
├── app.py              # 主应用文件
├── config.py           # 配置管理
├── database.py         # 数据库操作
├── api.py              # API路由
├── utils.py            # 工具函数
├── requirements.txt    # 依赖管理
├── Dockerfile          # Docker配置
├── .dockerignore       # Docker忽略文件
├── Makefile            # 构建工具
├── start.sh            # 启动脚本
├── env.example         # 环境变量示例
├── .gitignore          # Git忽略文件
├── schema.json         # API模式定义
├── tests/              # 测试目录
│   ├── __init__.py
│   ├── test_database.py
│   └── test_utils.py
├── docs/               # 文档目录
│   ├── __init__.py
│   ├── installation.md
│   ├── api.md
│   └── development.md
└── README.md           # 项目文档
```

## 开发环境设置

### 1. 克隆项目

```bash
git clone <repository-url>
cd dify-mongodb-tools
```

### 2. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

```bash
cp env.example .env
# 编辑 .env 文件
```

### 5. 启动开发服务器

```bash
python app.py
```

## 代码规范

### Python代码风格

- 遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 代码规范
- 使用类型提示 (Type Hints)
- 添加详细的文档字符串 (Docstrings)
- 保持函数职责单一

### 命名规范

- **文件名**: 小写字母，下划线分隔 (snake_case)
- **类名**: 大驼峰命名 (PascalCase)
- **函数名**: 小写字母，下划线分隔 (snake_case)
- **变量名**: 小写字母，下划线分隔 (snake_case)
- **常量名**: 大写字母，下划线分隔 (UPPER_SNAKE_CASE)

### 文档字符串格式

```python
def function_name(param1: str, param2: int) -> Dict[str, Any]:
    """
    函数功能描述
    
    Args:
        param1: 参数1的描述
        param2: 参数2的描述
        
    Returns:
        返回值的描述
        
    Raises:
        ValueError: 异常描述
    """
    pass
```

## 测试

### 运行测试

```bash
# 运行所有测试
python -m unittest discover tests

# 运行特定测试文件
python -m unittest tests.test_database

# 运行特定测试方法
python -m unittest tests.test_database.TestMongoDBManager.test_save_data
```

### 测试覆盖率

```bash
# 安装覆盖率工具
pip install coverage

# 运行测试并生成覆盖率报告
coverage run -m unittest discover tests
coverage report
coverage html  # 生成HTML报告
```

### 编写测试

1. **测试文件命名**: `test_*.py`
2. **测试类命名**: `Test*`
3. **测试方法命名**: `test_*`
4. **使用Mock**: 模拟外部依赖

```python
import unittest
from unittest.mock import Mock, patch

class TestExample(unittest.TestCase):
    def setUp(self):
        """测试前准备"""
        pass
    
    def test_example(self):
        """测试示例"""
        # 测试代码
        self.assertEqual(1 + 1, 2)
    
    def tearDown(self):
        """测试后清理"""
        pass
```

## 代码质量工具

### 代码检查

```bash
# 安装flake8
pip install flake8

# 运行代码检查
flake8 . --exclude=venv,__pycache__,.git
```

### 代码格式化

```bash
# 安装black
pip install black

# 格式化代码
black . --exclude=venv
```

### 类型检查

```bash
# 安装mypy
pip install mypy

# 运行类型检查
mypy . --ignore-missing-imports
```

## 调试

### 日志配置

```python
import logging

# 设置日志级别
logging.basicConfig(level=logging.DEBUG)

# 在代码中使用日志
logger = logging.getLogger(__name__)
logger.debug("调试信息")
logger.info("一般信息")
logger.warning("警告信息")
logger.error("错误信息")
```

### 调试模式

```bash
# 设置环境变量
export FLASK_ENV=development
export DEBUG=true

# 启动应用
python app.py
```

## 部署

### 生产环境配置

1. **环境变量**

```env
FLASK_ENV=production
DEBUG=false
LOG_LEVEL=WARNING
```

2. **使用Gunicorn**

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:3333 app:app
```

3. **使用Nginx反向代理**

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:3333;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Docker部署

```bash
# 构建生产镜像
docker build -t dify-mongodb-tools:prod .

# 运行生产容器
docker run -d \
  --restart=always \
  -p 3333:3333 \
  --name dify-mongodb-tools \
  -e FLASK_ENV=production \
  -e MONGO_URI=mongodb://your-mongo-host:27017/ \
  dify-mongodb-tools:prod
```

## 贡献指南

### 开发流程

1. **Fork项目**
2. **创建功能分支**

   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **开发功能**
4. **编写测试**
5. **运行测试**

   ```bash
   make test
   ```

6. **代码检查**

   ```bash
   make lint
   make format
   ```

7. **提交代码**

   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

8. **推送分支**

   ```bash
   git push origin feature/your-feature-name
   ```

9. **创建Pull Request**

### 提交信息规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

### 代码审查

- 所有代码变更都需要通过Pull Request
- 至少需要一名维护者审查
- 确保测试通过
- 确保代码符合规范

## 故障排除

### 常见问题

1. **MongoDB连接失败**
   - 检查MongoDB服务状态
   - 验证连接字符串
   - 检查网络连接

2. **端口被占用**
   - 修改PORT环境变量
   - 停止占用端口的服务

3. **权限问题**
   - 检查文件权限
   - 检查数据库权限

4. **依赖安装失败**
   - 升级pip: `pip install --upgrade pip`
   - 使用国内镜像: `pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt`

### 获取帮助

- 查看 [Issues](../../issues) 页面
- 创建新的Issue
- 联系维护者
