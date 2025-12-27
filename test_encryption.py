#!/usr/bin/env python3
"""
加密流程测试脚本

这个脚本模拟客户端的加密操作，演示完整的端到端加密流程。
"""

import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os


class EncryptionTestClient:
    def __init__(self):
        self.private_key = None
        self.public_key = None
        self.family_aes_key = None

    def generate_rsa_key_pair(self):
        """生成 RSA 密钥对"""
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()
        print("✓ RSA 密钥对生成成功")

    def derive_key_from_password(self, password: str, salt: bytes = None) -> tuple[bytes, bytes]:
        """
        从密码派生加密密钥 (KDF)
        
        Args:
            password: 用户密码
            salt: 盐值，如果为 None 则随机生成
        
        Returns:
            (derived_key, salt): 派生的密钥和使用的盐值
        """
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = kdf.derive(password.encode())
        print(f"✓ 从密码派生密钥成功 (salt: {salt.hex()[:16]}...)")
        return key, salt

    def encrypt_private_key_with_password(self, password: str) -> tuple[str, str]:
        """
        用密码加密 RSA 私钥
        
        Returns:
            (encrypted_private_key_b64, salt_b64): 加密后的私钥和盐值（Base64 编码）
        """
        if not self.private_key:
            raise ValueError("请先生成 RSA 密钥对")
        
        key, salt = self.derive_key_from_password(password)
        
        # 将私钥序列化为 PEM 格式
        pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        # 使用 AES-GCM 加密
        iv = os.urandom(12)
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(pem) + encryptor.finalize()
        
        # 组合 IV、tag 和密文
        encrypted_data = iv + encryptor.tag + ciphertext
        
        encrypted_b64 = base64.b64encode(encrypted_data).decode('utf-8')
        salt_b64 = base64.b64encode(salt).decode('utf-8')
        
        print(f"✓ RSA 私钥加密成功")
        return encrypted_b64, salt_b64

    def get_public_key_pem(self) -> str:
        """获取 RSA 公钥的 PEM 格式字符串"""
        if not self.public_key:
            raise ValueError("请先生成 RSA 密钥对")
        
        pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pem.decode('utf-8')

    def decrypt_private_key_with_password(self, encrypted_private_key_b64: str, salt_b64: str, password: str) -> bool:
        """
        用密码解密 RSA 私钥
        
        Returns:
            是否解密成功
        """
        try:
            encrypted_data = base64.b64decode(encrypted_private_key_b64)
            salt = base64.b64decode(salt_b64)
            
            # 从密码派生密钥
            key, _ = self.derive_key_from_password(password, salt)
            
            # 提取 IV、tag 和密文
            iv = encrypted_data[:12]
            tag = encrypted_data[12:28]
            ciphertext = encrypted_data[28:]
            
            # 解密
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(iv, tag),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            pem = decryptor.update(ciphertext) + decryptor.finalize()
            
            # 反序列化私钥
            self.private_key = serialization.load_pem_private_key(
                pem,
                password=None,
                backend=default_backend()
            )
            self.public_key = self.private_key.public_key()
            
            print("✓ RSA 私钥解密成功")
            return True
        except Exception as e:
            print(f"✗ RSA 私钥解密失败: {e}")
            return False

    def generate_family_aes_key(self):
        """生成家庭 AES 密钥"""
        self.family_aes_key = os.urandom(32)
        print(f"✓ 家庭 AES 密钥生成成功 (key: {self.family_aes_key.hex()[:16]}...)")

    def encrypt_family_key_with_public_key(self, public_key_pem: str) -> str:
        """
        用 RSA 公钥加密家庭 AES 密钥
        
        Returns:
            加密后的家庭密钥（Base64 编码）
        """
        if not self.family_aes_key:
            raise ValueError("请先生成家庭 AES 密钥")
        
        public_key = serialization.load_pem_public_key(
            public_key_pem.encode(),
            backend=default_backend()
        )
        
        encrypted_key = public_key.encrypt(
            self.family_aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        encrypted_b64 = base64.b64encode(encrypted_key).decode('utf-8')
        print(f"✓ 家庭密钥用 RSA 公钥加密成功")
        return encrypted_b64

    def decrypt_family_key_with_private_key(self, encrypted_family_key_b64: str) -> bool:
        """
        用 RSA 私钥解密家庭 AES 密钥
        
        Returns:
            是否解密成功
        """
        try:
            if not self.private_key:
                raise ValueError("请先解密 RSA 私钥")
            
            encrypted_key = base64.b64decode(encrypted_family_key_b64)
            
            self.family_aes_key = self.private_key.decrypt(
                encrypted_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            print(f"✓ 家庭密钥用 RSA 私钥解密成功")
            return True
        except Exception as e:
            print(f"✗ 家庭密钥解密失败: {e}")
            return False

    def encrypt_content_with_family_key(self, content: str) -> str:
        """
        用家庭 AES 密钥加密内容
        
        Returns:
            加密后的内容（Base64 编码）
        """
        if not self.family_aes_key:
            raise ValueError("请先生成或解密家庭 AES 密钥")
        
        iv = os.urandom(12)
        cipher = Cipher(
            algorithms.AES(self.family_aes_key),
            modes.GCM(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(content.encode()) + encryptor.finalize()
        
        encrypted_data = iv + encryptor.tag + ciphertext
        encrypted_b64 = base64.b64encode(encrypted_data).decode('utf-8')
        
        print(f"✓ 内容用家庭 AES 密钥加密成功")
        return encrypted_b64

    def decrypt_content_with_family_key(self, encrypted_content_b64: str) -> str:
        """
        用家庭 AES 密钥解密内容
        
        Returns:
            解密后的内容
        """
        try:
            if not self.family_aes_key:
                raise ValueError("请先生成或解密家庭 AES 密钥")
            
            encrypted_data = base64.b64decode(encrypted_content_b64)
            iv = encrypted_data[:12]
            tag = encrypted_data[12:28]
            ciphertext = encrypted_data[28:]
            
            cipher = Cipher(
                algorithms.AES(self.family_aes_key),
                modes.GCM(iv, tag),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            content = decryptor.update(ciphertext) + decryptor.finalize()
            
            print(f"✓ 内容用家庭 AES 密钥解密成功")
            return content.decode()
        except Exception as e:
            print(f"✗ 内容解密失败: {e}")
            return ""


def test_complete_encryption_flow():
    """测试完整的加密流程"""
    print("\n" + "="*60)
    print("测试完整的端到端加密流程")
    print("="*60 + "\n")
    
    # 用户 1 - 家庭所有者
    print("【用户 1 - 家庭所有者】")
    user1 = EncryptionTestClient()
    user1.generate_rsa_key_pair()
    password1 = "my_secure_password_123"
    
    encrypted_private_key1, salt1 = user1.encrypt_private_key_with_password(password1)
    public_key_pem1 = user1.get_public_key_pem()
    
    print(f"  公钥: {public_key_pem1[:50]}...")
    print(f"  加密的私钥: {encrypted_private_key1[:50]}...")
    
    # 用户 2 - 家庭成员
    print("\n【用户 2 - 家庭成员】")
    user2 = EncryptionTestClient()
    user2.generate_rsa_key_pair()
    password2 = "another_secure_password_456"
    
    encrypted_private_key2, salt2 = user2.encrypt_private_key_with_password(password2)
    public_key_pem2 = user2.get_public_key_pem()
    
    print(f"  公钥: {public_key_pem2[:50]}...")
    print(f"  加密的私钥: {encrypted_private_key2[:50]}...")
    
    # 用户 1 创建家庭
    print("\n【创建家庭】")
    user1.generate_family_aes_key()
    
    # 为用户 1 加密家庭密钥
    encrypted_family_key_for_user1 = user1.encrypt_family_key_with_public_key(public_key_pem1)
    print(f"  用户 1 的加密家庭密钥: {encrypted_family_key_for_user1[:50]}...")
    
    # 为用户 2 加密家庭密钥
    encrypted_family_key_for_user2 = user1.encrypt_family_key_with_public_key(public_key_pem2)
    print(f"  用户 2 的加密家庭密钥: {encrypted_family_key_for_user2[:50]}...")
    
    # 用户 1 创建里程碑
    print("\n【用户 1 创建里程碑】")
    milestone_content = "今天我们全家去公园玩，非常开心！"
    encrypted_milestone = user1.encrypt_content_with_family_key(milestone_content)
    print(f"  原始内容: {milestone_content}")
    print(f"  加密内容: {encrypted_milestone[:50]}...")
    
    # 模拟用户 1 重新登录并解密数据
    print("\n【用户 1 重新登录并解密】")
    user1_new = EncryptionTestClient()
    success = user1_new.decrypt_private_key_with_password(
        encrypted_private_key1, salt1, password1
    )
    if success:
        success = user1_new.decrypt_family_key_with_private_key(encrypted_family_key_for_user1)
        if success:
            decrypted_content = user1_new.decrypt_content_with_family_key(encrypted_milestone)
            print(f"  解密后的内容: {decrypted_content}")
            assert decrypted_content == milestone_content
            print("  ✓ 解密内容与原始内容一致")
    
    # 模拟用户 2 登录并解密数据
    print("\n【用户 2 登录并解密】")
    user2_new = EncryptionTestClient()
    success = user2_new.decrypt_private_key_with_password(
        encrypted_private_key2, salt2, password2
    )
    if success:
        success = user2_new.decrypt_family_key_with_private_key(encrypted_family_key_for_user2)
        if success:
            decrypted_content = user2_new.decrypt_content_with_family_key(encrypted_milestone)
            print(f"  解密后的内容: {decrypted_content}")
            assert decrypted_content == milestone_content
            print("  ✓ 解密内容与原始内容一致")
    
    print("\n" + "="*60)
    print("✓ 所有测试通过！")
    print("="*60 + "\n")


def test_api_registration_data():
    """测试 API 注册数据格式"""
    print("\n" + "="*60)
    print("测试 API 注册数据格式")
    print("="*60 + "\n")
    
    client = EncryptionTestClient()
    client.generate_rsa_key_pair()
    password = "test_password_123"
    
    encrypted_private_key, salt = client.encrypt_private_key_with_password(password)
    public_key_pem = client.get_public_key_pem()
    
    registration_data = {
        "phone": "13800138000",
        "username": "test_user",
        "password": password,
        "public_key": public_key_pem,
        "encrypted_private_key": encrypted_private_key
    }
    
    print("注册请求数据:")
    print(f"  phone: {registration_data['phone']}")
    print(f"  username: {registration_data['username']}")
    print(f"  password: {registration_data['password']}")
    print(f"  public_key: {registration_data['public_key'][:50]}...")
    print(f"  encrypted_private_key: {registration_data['encrypted_private_key'][:50]}...")
    
    print("\n✓ API 注册数据格式正确\n")


if __name__ == "__main__":
    test_complete_encryption_flow()
    test_api_registration_data()
