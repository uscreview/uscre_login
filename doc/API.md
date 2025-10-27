# 用户认证 API 文档

## 概述
- 提供用户认证相关接口：注册、邮箱验证、登录、获取用户信息。
- 返回统一 JSON 格式：code（0 表示成功）、message、data。

## 认证
- 使用 JWT（Bearer token）
- token 有效期为 1 小时

## 统一响应格式（JSON）
成功响应：
```json
{
    "code": 0,
    "message": "success message",
    "data": { /* response data */ }
}
```

错误响应：
```json
{
    "error": "error message"
}
```

## 常见 HTTP 错误码
- `400`: Bad Request — 参数校验失败或请求无效
- `401`: Unauthorized — 认证失败、token无效或过期
- `404`: Not Found — 用户不存在
- `500`: Internal Server Error — 服务内部错误



## 接口列表

### 1. 用户注册 — `POST` `/api/v1/auth/register`

#### 请求头
    Content-Type: application/json

#### 请求体
```json
{
    "username": "alice",
    "email": "alice@example.com",
    "password": "your_password"
}
```

#### 成功响应 (201)
```json
{
    "code": 0,
    "message": "user created, verification email sent",
    "data": {
        "id": "uuid-string",
        "email": "alice@example.com",
        "username": "alice",
        "created_at": "2025-10-27T12:00:00+00:00"
    }
}
```

#### 错误响应
- `400`: 用户已存在
```json
{
    "code": 1,
    "message": "user already exists"
}
```

### 2. 邮箱验证 — `GET` `/api/v1/auth/verify/<token>`

#### 参数
- `token`: 通过邮件发送的验证token

#### 成功响应 (200)
```json
{
    "code": 0,
    "message": "email verified successfully"
}
```

#### 错误响应
- `400`: token无效或过期
```json
{
    "code": 1,
    "message": "invalid or expired token"
}
```
- `404`: 用户不存在
```json
{
    "code": 2,
    "message": "user not found"
}
```
- `200`: 已验证过
```json
{
    "code": 3,
    "message": "already verified"
}
```

### 3. 用户登录 — `POST` `/api/v1/auth/login`

#### 请求头
    Content-Type: application/json

#### 请求体
```json
{
    "email": "alice@example.com",
    "password": "your_password"
}
```

#### 成功响应 (200)
```json
{
    "code": 0,
    "message": "login successful",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### 错误响应
- `401`: 认证失败
```json
{
    "error": "Invalid credentials, incorrect email or password"
}
```

### 4. 获取用户信息 — `GET` `/api/v1/auth/profile`

#### 请求头
    Authorization: Bearer <token>

#### 成功响应 (200)
```json
{
    "username": "alice",
    "email": "alice@example.com",
    "created_at": "2025-10-27T12:00:00+00:00"
}
```

#### 错误响应
- `401`: token缺失
```json
{
    "error": "Missing token"
}
```
- `401`: token过期
```json
{
    "error": "Token expired"
}
```
- `401`: token无效
```json
{
    "error": "Invalid token"
}
```
- `404`: 用户不存在
```json
{
    "error": "User not found"
}
```

## 实现细节

### 安全特性
- JWT token 有效期为1小时
- 使用 `werkzeug.security` 进行密码哈希
- 邮箱验证token有效期为15分钟
- 所有密码相关操作使用安全哈希存储

### 数据验证
- 用户名唯一性检查
- 邮箱唯一性检查
- 邮箱验证流程

### 邮件服务
- 支持通过SMTP发送验证邮件
- 可配置的邮件服务器设置（见环境变量配置）

### 环境变量配置
- `DATABASE_URL`: 数据库连接URL
- `JWT_SECRET_KEY`: JWT签名密钥
- `MAIL_SERVER`: SMTP服务器地址（默认：smtp.gmail.com）
- `MAIL_PORT`: SMTP端口（默认：465）
- `MAIL_USE_TLS`: 是否使用TLS（默认：False）
- `MAIL_USE_SSL`: 是否使用SSL（默认：True）
- `MAIL_USERNAME`: SMTP用户名
- `MAIL_PASSWORD`: SMTP密码
- `MAIL_SENDER_NAME`: 发件人名称（默认：USCRE）
- `MAIL_SENDER_EMAIL`: 发件人邮箱（默认：与MAIL_USERNAME相同）