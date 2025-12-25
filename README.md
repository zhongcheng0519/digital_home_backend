# Digital Home Backend (数字家)

一个专注于隐私的家庭资产管理后端，支持**零知识端到端加密**。

## 🔐 安全理念

服务器**永远不会**拥有解密密钥。所有敏感数据都在客户端进行加密：
- 用户私钥使用用户密码加密
- 家庭共享密钥使用 RSA 公钥加密
- 事件内容使用家庭 AES 密钥加密

## 🚀 技术栈

- **Python**: 3.10+
- **包管理器**: uv (现代 Python 包管理工具)
- **Web 框架**: FastAPI
- **数据库 ORM**: SQLModel
- **数据库**: PostgreSQL (asyncpg 驱动)
- **迁移工具**: Alembic
- **身份认证**: JWT (python-jose)
- **密码哈希**: bcrypt (passlib)

## 📁 项目结构

```
backend/
├── app/
│   ├── main.py              # FastAPI 应用入口
│   ├── core/
│   │   ├── config.py        # 配置设置
│   │   └── security.py      # JWT 和密码工具
│   ├── db/
│   │   ├── session.py       # 异步数据库会话
│   │   └── init_db.py       # 数据库初始化
│   ├── models/              # SQLModel 类
│   │   ├── user.py
│   │   ├── family.py
│   │   └── milestone.py
│   └── api/
│       ├── deps.py          # 依赖注入 (身份认证)
│       └── v1/
│           ├── api.py       # 路由配置
│           └── endpoints/
│               ├── auth.py
│               ├── family.py
│               └── milestone.py
├── alembic/                 # 数据库迁移
├── pyproject.toml           # uv 项目配置和依赖管理
├── .env.example
└── README.md
```

## 🛠️ 安装设置

### 1. 安装依赖

**使用 uv（推荐）：**

```bash
# 安装项目依赖
uv sync

# 或者只安装生产依赖
uv sync --no-dev
```

### 2. 配置环境

将 `.env.example` 复制到 `.env` 并更新配置：

```bash
cp .env.example .env
```

编辑 `.env`:
```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/digital_home
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

### 3. 设置数据库

确保 PostgreSQL 正在运行并创建数据库：

```bash
createdb digital_home
```

### 4. 运行迁移（可选）

如果你想使用 Alembic 进行迁移：

```bash
# 初始化迁移
alembic revision --autogenerate -m "Initial migration"

# 应用迁移
alembic upgrade head
```

**注意**：应用启动时将使用 `SQLModel.metadata.create_all()` 自动创建表。

### 5. 运行服务器

```bash
uvicorn app.main:app --reload
```

API 将在以下地址可用：`http://localhost:8000`

API 文档：`http://localhost:8000/docs`

## 📡 API 接口

### 身份认证 (`/api/v1/auth`)

- `POST /register` - 注册新用户
- `POST /login` - 登录并获取 JWT 令牌

### 家庭管理 (`/api/v1/family`)

- `POST /` - 创建新家庭
- `POST /member` - 添加家庭成员
- `GET /my` - 获取用户所属的所有家庭

### 里程碑 (`/api/v1/milestone`)

- `POST /` - 创建里程碑
- `GET /?family_id=X&year=YYYY` - 列出里程碑（按家庭过滤，可选择按年份）

## 🔑 身份认证流程

1. **注册**：客户端生成 RSA 密钥对，用密码加密私钥，向服务器发送公钥和加密后的私钥
2. **登录**：服务器验证凭据，返回 JWT 令牌和用户信息（包括加密的密钥）
3. **认证请求**：在 `Authorization: Bearer <token>` 头中包含 JWT 令牌

## 🗄️ 数据库架构

### User
- `id`, `phone` (唯一), `username`, `hashed_password`
- `public_key` (RSA 公钥, PEM)
- `encrypted_private_key` [CIPHER] (密码加密的 RSA 私钥)

### Family
- `id`, `name`, `owner_id`

### FamilyMember
- `family_id`, `user_id` (复合主键)
- `role` ("owner" 或 "member")
- `encrypted_family_key` [CIPHER] (用户公钥加密的 AES 家庭密钥)

### Milestone
- `id`, `family_id`, `creator_id`
- `event_date` (用于排序的纯日期)
- `content_ciphertext` [CIPHER] (家庭 AES 密钥加密的内容)
- `created_at`

## 🔒 加密模型

**[CIPHER]** 字段在客户端加密，被服务器视为不透明的字符串。

1. 用户创建密码 → 派生加密密钥
2. 用户生成 RSA 密钥对
3. 私钥用密码派生的密钥加密
4. 家庭所有者生成 AES 家庭密钥
5. 家庭密钥用每个成员的 RSA 公钥加密
6. 里程碑内容用家庭 AES 密钥加密

服务器**永远**不会看到明文敏感数据。

## 📝 许可证

Digital Home (数字家) 私有项目。