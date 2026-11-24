"""账本文件加密：整文件 AES-256-GCM 加密 + PBKDF2-HMAC-SHA256 密钥派生。

文件格式（全部写入密文文件开头）：
    MAGIC(12) | 版本(1) | 迭代次数(4, 大端) | salt(16) | nonce(12) | AESGCM密文

密码只用于派生密钥，文件中不保存密码或密钥；GCM 认证标签即密码校验手段，
解密认证失败视为密码错误。明文数据库文件不以此 MAGIC 开头，可与密文自动区分。
"""
import os

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

MAGIC = b'BKENCv1\x00\x00\x00\x00'  # 12 字节魔数，标记本软件加密格式
_VERSION = 1
_SALT_LEN = 16
_NONCE_LEN = 12
_KEY_LEN = 32
_HEADER_LEN = len(MAGIC) + 1 + 4 + _SALT_LEN + _NONCE_LEN  # 45 字节

DEFAULT_ITERATIONS = 600_000  # PBKDF2 迭代次数，随文件头保存，便于将来升级强度


class CryptoError(Exception):
    """加密功能基础异常"""


class WrongPasswordError(CryptoError):
    """密码错误或密钥无法通过 GCM 认证"""


class CorruptFileError(CryptoError):
    """文件不是本软件加密格式或内容已损坏"""


class AlreadyEncryptedError(CryptoError):
    """文件已是密文，重复加密被拒绝"""


class NotEncryptedError(CryptoError):
    """文件不是密文，解密被拒绝"""


def _derive_key(password: str, salt: bytes, iterations: int) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=_KEY_LEN,
        salt=salt,
        iterations=iterations,
    )
    return kdf.derive(password.encode('utf-8'))


def encrypt_bytes(data: bytes, password: str, iterations: int = DEFAULT_ITERATIONS) -> bytes:
    """加密字节串，返回完整密文字节（含文件头）"""
    salt = os.urandom(_SALT_LEN)
    nonce = os.urandom(_NONCE_LEN)
    key = _derive_key(password, salt, iterations)
    ciphertext = AESGCM(key).encrypt(nonce, data, MAGIC)
    return (MAGIC + bytes([_VERSION]) + iterations.to_bytes(4, 'big')
            + salt + nonce + ciphertext)


def decrypt_bytes(blob: bytes, password: str) -> bytes:
    """解密密文字节串；密码错误或文件损坏时抛出对应异常"""
    if len(blob) < _HEADER_LEN or not blob.startswith(MAGIC):
        raise CorruptFileError('不是本软件加密的账本文件')
    pos = len(MAGIC)
    version = blob[pos]
    if version != _VERSION:
        raise CorruptFileError(f'不支持的加密格式版本: {version}')
    pos += 1
    iterations = int.from_bytes(blob[pos:pos + 4], 'big')
    pos += 4
    salt = blob[pos:pos + _SALT_LEN]
    pos += _SALT_LEN
    nonce = blob[pos:pos + _NONCE_LEN]
    pos += _NONCE_LEN
    ciphertext = blob[pos:]
    key = _derive_key(password, salt, iterations)
    try:
        return AESGCM(key).decrypt(nonce, ciphertext, MAGIC)
    except InvalidTag:
        raise WrongPasswordError('密码错误或文件已被篡改')


def is_encrypted_file(path: str) -> bool:
    """通过文件头魔数判断是否为加密账本"""
    try:
        with open(path, 'rb') as f:
            return f.read(len(MAGIC)) == MAGIC
    except OSError:
        return False


def _atomic_write(path: str, blob: bytes) -> None:
    """先写同目录临时文件再原子替换，避免中断留下半个文件"""
    tmp_path = f'{path}.tmp-{os.getpid()}'
    try:
        with open(tmp_path, 'wb') as f:
            f.write(blob)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass


def encrypt_file(src_path: str, dst_path: str, password: str) -> None:
    """加密 src_path 文件并写入 dst_path（可相同，即原地加密）"""
    with open(src_path, 'rb') as f:
        data = f.read()
    if data.startswith(MAGIC):
        raise AlreadyEncryptedError('文件已是加密状态')
    _atomic_write(dst_path, encrypt_bytes(data, password))


def decrypt_file(src_path: str, dst_path: str, password: str) -> None:
    """解密 src_path 文件并写入 dst_path（可相同，即原地解密）"""
    with open(src_path, 'rb') as f:
        blob = f.read()
    _atomic_write(dst_path, decrypt_bytes(blob, password))


def change_password_file(path: str, old_password: str, new_password: str) -> None:
    """修改密文文件密码：先用旧密码解密，再用新密码加密后原子写回"""
    with open(path, 'rb') as f:
        blob = f.read()
    data = decrypt_bytes(blob, old_password)  # 旧密码错误在这里抛出 WrongPasswordError
    _atomic_write(path, encrypt_bytes(data, new_password))
