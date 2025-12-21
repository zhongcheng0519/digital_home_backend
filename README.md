# Digital Home Backend (数字家)

A privacy-focused family asset management backend with **Zero-Knowledge End-to-End Encryption**.

## 🔐 Security Philosophy

The server **NEVER** has access to decryption keys. All sensitive data is encrypted on the client side:
- User private keys are encrypted with user passwords
- Family shared keys are encrypted with RSA public keys
- Event content is encrypted with family AES keys

## 🚀 Tech Stack

- **Python**: 3.10+
- **Web Framework**: FastAPI
- **Database ORM**: SQLModel
- **Database**: PostgreSQL (asyncpg driver)
- **Migrations**: Alembic
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt (passlib)

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app entry
│   ├── core/
│   │   ├── config.py        # Settings
│   │   └── security.py      # JWT & password utilities
│   ├── db/
│   │   ├── session.py       # Async DB session
│   │   └── init_db.py       # Database initialization
│   ├── models/              # SQLModel classes
│   │   ├── user.py
│   │   ├── family.py
│   │   └── milestone.py
│   └── api/
│       ├── deps.py          # Dependencies (auth)
│       └── v1/
│           ├── api.py       # Router setup
│           └── endpoints/
│               ├── auth.py
│               ├── family.py
│               └── milestone.py
├── alembic/                 # Database migrations
├── requirements.txt
├── .env.example
└── README.md
```

## 🛠️ Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and update the values:

```bash
cp .env.example .env
```

Edit `.env`:
```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/digital_home
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

### 3. Setup Database

Make sure PostgreSQL is running and create the database:

```bash
createdb digital_home
```

### 4. Run Migrations (Optional)

If you want to use Alembic for migrations:

```bash
# Initialize migrations
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

**Note**: The app will auto-create tables on startup using `SQLModel.metadata.create_all()`.

### 5. Run the Server

```bash
uvicorn app.main:app --reload
```

The API will be available at: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

## 📡 API Endpoints

### Authentication (`/api/v1/auth`)

- `POST /register` - Register a new user
- `POST /login` - Login and get JWT token

### Family Management (`/api/v1/family`)

- `POST /` - Create a new family
- `POST /member` - Add a member to family
- `GET /my` - Get all families user belongs to

### Milestones (`/api/v1/milestone`)

- `POST /` - Create a milestone
- `GET /?family_id=X&year=YYYY` - List milestones (filtered by family and optionally by year)

## 🔑 Authentication Flow

1. **Register**: Client generates RSA key pair, encrypts private key with password, sends public key and encrypted private key to server
2. **Login**: Server validates credentials, returns JWT token and user info (including encrypted keys)
3. **Authenticated Requests**: Include JWT token in `Authorization: Bearer <token>` header

## 🗄️ Database Schema

### User
- `id`, `phone` (unique), `username`, `hashed_password`
- `public_key` (RSA Public Key, PEM)
- `encrypted_private_key` [CIPHER] (RSA Private Key encrypted by password)

### Family
- `id`, `name`, `owner_id`

### FamilyMember
- `family_id`, `user_id` (composite PK)
- `role` ("owner" or "member")
- `encrypted_family_key` [CIPHER] (AES Family Key encrypted by User's Public Key)

### Milestone
- `id`, `family_id`, `creator_id`
- `event_date` (plain date for sorting)
- `content_ciphertext` [CIPHER] (content encrypted by Family AES Key)
- `created_at`

## 🔒 Encryption Model

**[CIPHER]** fields are encrypted on the client and treated as opaque strings by the server.

1. User creates password → derives encryption key
2. User generates RSA key pair
3. Private key encrypted with password-derived key
4. Family owner generates AES family key
5. Family key encrypted with each member's RSA public key
6. Milestone content encrypted with family AES key

The server **never** sees plaintext sensitive data.

## 📝 License

Private project for Digital Home (数字家).
