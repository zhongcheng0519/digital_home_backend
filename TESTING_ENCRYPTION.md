# 加密流程测试指南

本文档介绍如何测试数字家后端的端到端加密系统。

## 测试方式

### 方式一：运行加密测试脚本

项目提供了一个完整的加密测试脚本 `test_encryption.py`，它模拟了客户端的加密操作。

#### 运行测试

```bash
# 确保已安装依赖
uv sync

# 运行测试脚本
python test_encryption.py
```

#### 测试内容

测试脚本包含两个主要测试：

1. **完整加密流程测试** (`test_complete_encryption_flow`)
   - 模拟两个用户（家庭所有者和家庭成员）
   - 演示从注册到创建里程碑的完整加密流程
   - 验证数据可以正确加密和解密

2. **API 注册数据格式测试** (`test_api_registration_data`)
   - 生成符合 API 要求的注册数据格式
   - 展示如何构造注册请求

#### 测试流程图

```
用户 1（家庭所有者）
  ├─ 生成 RSA 密钥对
  ├─ 用密码加密私钥 → encrypted_private_key1
  ├─ 生成家庭 AES 密钥
  ├─ 用自己的公钥加密家庭密钥 → encrypted_family_key1
  └─ 用家庭密钥加密里程碑内容 → encrypted_milestone

用户 2（家庭成员）
  ├─ 生成 RSA 密钥对
  ├─ 用密码加密私钥 → encrypted_private_key2
  └─ 接收加密的家庭密钥 → encrypted_family_key2

解密测试
  ├─ 用户 1 用密码解密私钥
  ├─ 用户 1 用私钥解密家庭密钥
  ├─ 用户 1 用家庭密钥解密里程碑内容 ✓
  ├─ 用户 2 用密码解密私钥
  ├─ 用户 2 用私钥解密家庭密钥
  └─ 用户 2 用家庭密钥解密里程碑内容 ✓
```

### 方式二：使用 API 手动测试

#### 1. 启动服务器

```bash
uvicorn app.main:app --reload
```

#### 2. 使用 Python 测试脚本

创建一个测试脚本 `test_api.py`：

#### 3. 使用 curl 测试

```bash
# 注册用户
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "13800138000",
    "username": "test_user",
    "password": "test_password_123",
    "public_key": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...",
    "encrypted_private_key": "base64_encoded_encrypted_private_key"
  }'

# 登录用户
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "13800138000",
    "password": "test_password_123"
  }'
```

### 方式三：使用 FastAPI 自动文档

1. 启动服务器后，访问 `http://localhost:8000/docs`
2. 在 Swagger UI 中测试各个 API 端点
3. 使用 `/api/v1/auth/register` 注册用户
4. 使用 `/api/v1/auth/login` 登录并获取 token
5. 使用返回的 token 测试其他需要认证的接口

## 加密流程验证要点

### 1. 密钥生成验证
- ✓ RSA 密钥对生成成功
- ✓ 公钥可以正确序列化为 PEM 格式
- ✓ 私钥可以正确序列化为 PEM 格式

### 2. 私钥加密验证
- ✓ 使用密码派生密钥（KDF）成功
- ✓ 使用派生密钥加密私钥成功
- ✓ 使用正确密码可以解密私钥
- ✓ 使用错误密码无法解密私钥

### 3. 家庭密钥分发验证
- ✓ 家庭 AES 密钥生成成功
- ✓ 使用 RSA 公钥加密家庭密钥成功
- ✓ 使用 RSA 私钥解密家庭密钥成功
- ✓ 不同成员的加密家庭密钥不同

### 4. 内容加密验证
- ✓ 使用家庭 AES 密钥加密内容成功
- ✓ 使用家庭 AES 密钥解密内容成功
- ✓ 解密后的内容与原始内容一致

### 5. 跨用户访问验证
- ✓ 用户 1 可以解密自己加密的数据
- ✓ 用户 2 可以解密用户 1 加密的数据（同一家庭）
- ✓ 没有家庭密钥的用户无法解密数据

## 安全性测试

### 1. 密码强度测试
- 测试弱密码是否能被暴力破解
- 测试密码派生函数（KDF）的迭代次数是否足够

### 2. 密钥管理测试
- 测试私钥是否真的无法从服务器获取
- 测试家庭密钥是否只对家庭成员可见

### 3. 数据泄露测试
- 模拟数据库泄露，验证加密数据是否安全
- 测试即使获取了加密数据，也无法解密

## 常见问题

### Q: 如何验证服务器真的无法解密数据？

A: 检查以下几点：
1. 数据库中存储的是加密后的密文
2. 服务器代码中没有解密逻辑
3. 使用数据库查询工具直接查看数据，确认是密文

### Q: 如何测试家庭成员权限管理？

A:
1. 创建一个家庭
2. 添加两个成员
3. 创建一些里程碑
4. 移除一个成员
5. 验证被移除的成员无法解密新的数据

### Q: 如何测试密码错误的情况？

A:
1. 使用错误密码尝试解密私钥
2. 验证解密失败
3. 验证无法获取家庭密钥
4. 验证无法解密内容

## 下一步

完成加密测试后，你可以：
1. 编写自动化测试套件
2. 进行性能测试
3. 进行安全审计
4. 集成到 CI/CD 流程中
