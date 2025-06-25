# API文档

## 基础信息

- **基础URL**: `http://localhost:3333`
- **API前缀**: `/api`
- **数据格式**: JSON
- **认证方式**: 无（可根据需要添加）

## 通用响应格式

### 成功响应

```json
{
  "message": "操作成功信息",
  "data": "响应数据（可选）"
}
```

### 错误响应

```json
{
  "error": "错误描述",
  "message": "详细错误信息（可选）"
}
```

## 端点列表

### 1. 保存数据 (`POST /api/save`)

保存数据到指定的数据库和集合。

#### 请求参数

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| db_name | string | 是 | 目标数据库名称 |
| collection_name | string | 是 | 目标集合名称 |
| uuid | string | 否 | 数据唯一标识，不提供则自动生成 |
| uuid_name | string | 否 | UUID字段名，默认为"uuid" |
| title | string | 否 | 数据标题 |
| content | string | 否 | JSON格式的数据内容 |

#### 请求示例

```bash
curl -X POST http://localhost:3333/api/save \
  -H "Content-Type: application/json" \
  -d '{
    "db_name": "my_database",
    "collection_name": "my_collection",
    "title": "测试数据",
    "content": "{\"key\": \"value\", \"number\": 123}"
  }'
```

#### 响应示例

```json
{
  "message": "Data saved successfully",
  "id": {"uuid": "123e4567-e89b-12d3-a456-426614174000"},
  "is_new": true
}
```

#### 特殊处理

- **列表数据**: 如果content解析为数组，会自动包装在"list"字段中
- **时间戳**: 自动添加created_at和updated_at字段
- **UUID生成**: 使用UUIDv4标准

### 2. 搜索数据 (`GET /api/search`)

支持复杂查询条件的数据搜索。

#### 查询参数

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| db_name | string | 是 | 数据库名称 |
| collection_name | string | 是 | 集合名称 |
| uuid_name | string | 否 | UUID字段名，默认为"uuid" |
| uuid | string | 否 | UUID值 |
| conditions | string | 否 | JSON格式的查询条件 |
| sorts | string | 否 | JSON格式的排序条件 |
| limit | integer | 否 | 限制返回数量，默认5 |
| skip | integer | 否 | 跳过数量，默认0 |

#### 请求示例

```bash
# 基本查询
curl "http://localhost:3333/api/search?db_name=my_db&collection_name=my_collection&uuid=123&limit=10"

# 复杂查询
curl "http://localhost:3333/api/search?db_name=my_db&collection_name=my_collection&conditions={\"title\":\"测试\"}&sorts={\"created_at\":-1}&limit=20&skip=10"
```

#### 响应示例

```json
[
  {
    "uuid": "123e4567-e89b-12d3-a456-426614174000",
    "title": "测试数据",
    "data": {
      "key": "value",
      "number": 123
    },
    "created_at": 1640995200000,
    "updated_at": 1640995200000
  }
]
```

#### 查询条件示例

```json
// 精确匹配
{"title": "测试标题"}

// 模糊匹配
{"title": {"$regex": "测试", "$options": "i"}}

// 数值范围
{"age": {"$gte": 18, "$lte": 65}}

// 时间范围
{"created_at": {"$gte": 1640995200000, "$lte": 1641081600000}}

// 多条件组合
{"status": "active", "type": "user"}
```

#### 排序条件示例

```json
// 单字段排序
{"created_at": -1}

// 多字段排序
{"created_at": -1, "title": 1}
```

### 3. 健康检查 (`GET /api/health`)

检查应用和数据库连接状态。

#### 请求示例

```bash
curl http://localhost:3333/api/health
```

#### 响应示例

**正常状态**:

```json
{
  "status": "healthy",
  "message": "服务运行正常",
  "database": "connected"
}
```

**异常状态**:

```json
{
  "status": "unhealthy",
  "message": "服务异常",
  "database": "disconnected",
  "error": "连接错误详情"
}
```

## 错误码说明

| 状态码 | 说明 | 示例 |
|--------|------|------|
| 200 | 请求成功 | 正常响应 |
| 400 | 请求参数错误 | 缺少必需参数 |
| 404 | 资源不存在 | 接口不存在 |
| 405 | 请求方法不允许 | 使用错误的HTTP方法 |
| 500 | 服务器内部错误 | 数据库连接失败 |
| 503 | 服务不可用 | 健康检查失败 |

## 使用示例

### 完整的数据操作流程

```bash
# 1. 保存数据
curl -X POST http://localhost:3333/api/save \
  -H "Content-Type: application/json" \
  -d '{
    "db_name": "user_db",
    "collection_name": "profiles",
    "title": "用户资料",
    "content": "{\"name\": \"张三\", \"age\": 25, \"email\": \"zhangsan@example.com\"}"
  }'

# 2. 查询数据
curl "http://localhost:3333/api/search?db_name=user_db&collection_name=profiles&conditions={\"data.name\":\"张三\"}"

# 3. 检查服务状态
curl http://localhost:3333/api/health
```

### 批量操作示例

```bash
# 批量保存用户数据
for i in {1..5}; do
  curl -X POST http://localhost:3333/api/save \
    -H "Content-Type: application/json" \
    -d "{
      \"db_name\": \"user_db\",
      \"collection_name\": \"profiles\",
      \"title\": \"用户$i\",
      \"content\": \"{\\\"name\\\": \\\"用户$i\\\", \\\"age\\\": $((20 + i))}\"
    }"
done

# 分页查询所有用户
curl "http://localhost:3333/api/search?db_name=user_db&collection_name=profiles&limit=10&skip=0"
curl "http://localhost:3333/api/search?db_name=user_db&collection_name=profiles&limit=10&skip=10"
```

## 最佳实践

1. **数据库命名**: 使用有意义的数据库和集合名称
2. **UUID管理**: 建议使用有业务含义的UUID
3. **查询优化**: 合理使用索引，避免复杂的查询条件
4. **错误处理**: 始终检查响应状态码和错误信息
5. **分页查询**: 大数据量时使用分页查询
6. **监控**: 定期调用健康检查接口监控服务状态
