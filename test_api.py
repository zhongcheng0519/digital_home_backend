import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
import os

BASE_URL = "http://localhost:8000/api/v1"


def generate_rsa_key_pair():
    """生成 RSA 密钥对"""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    return private_key, public_key


def encrypt_private_key(password, private_key):
    """用密码加密私钥"""
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = kdf.derive(password.encode())
    
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    iv = os.urandom(12)
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(pem) + encryptor.finalize()
    encrypted_data = iv + encryptor.tag + ciphertext
    
    return base64.b64encode(encrypted_data).decode('utf-8'), base64.b64encode(salt).decode('utf-8')


def get_public_key_pem(public_key):
    """获取公钥 PEM"""
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return pem.decode('utf-8')


def test_registration_and_login():
    """测试用户注册和登录"""
    print("=" * 60)
    print("测试用户注册和登录")
    print("=" * 60 + "\n")
    
    # 测试注册
    print("测试用户注册...")
    private_key, public_key = generate_rsa_key_pair()
    password = "test_password_123"
    encrypted_private_key, salt = encrypt_private_key(password, private_key)
    public_key_pem = get_public_key_pem(public_key)
    
    register_data = {
        "phone": "13800138000",
        "username": "test_user",
        "password": password,
        "public_key": public_key_pem,
        "encrypted_private_key": encrypted_private_key
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        print(f"注册响应状态码: {response.status_code}")
        print(f"注册响应: {response.json()}")
        
        if response.status_code == 200:
            print("✓ 用户注册成功\n")
        else:
            print(f"✗ 用户注册失败\n")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到服务器，请确保服务器已启动\n")
        print("启动服务器命令: uvicorn app.main:app --reload\n")
        return False
    
    # 测试登录
    print("测试用户登录...")
    login_data = {
        "phone": "13800138000",
        "password": password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"登录响应状态码: {response.status_code}")
        login_result = response.json()
        print(f"登录响应: {login_result}")
        
        if response.status_code == 200:
            print("\n✓ 用户登录成功\n")
            
            token = login_result["access_token"]
            user_info = login_result["user_info"]
            print("用户信息:")
            print(f"  ID: {user_info['id']}")
            print(f"  用户名: {user_info['username']}")
            print(f"  公钥: {user_info['public_key'][:50]}...")
            print(f"  加密的私钥: {user_info['encrypted_private_key'][:50]}...")
            
            print(f"\n访问令牌: {token[:50]}...")
            return token
        else:
            print(f"✗ 用户登录失败\n")
            return None
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到服务器\n")
        return None


if __name__ == "__main__":
    token = test_registration_and_login()
    
    if token:
        print("\n" + "=" * 60)
        print("✓ 所有 API 测试通过！")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("✗ API 测试失败，请检查服务器是否启动")
        print("=" * 60)
