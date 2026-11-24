"""utils.crypto 加密模块测试：加解密往返、密码校验、原子写与异常分支"""
import os
import sqlite3

import pytest

from utils.crypto import (
    MAGIC,
    AlreadyEncryptedError,
    CorruptFileError,
    NotEncryptedError,
    WrongPasswordError,
    change_password_file,
    decrypt_bytes,
    decrypt_file,
    encrypt_bytes,
    encrypt_file,
    is_encrypted_file,
)


@pytest.fixture
def plaintext(tmp_path):
    """构造一个真实可用的明文 SQLite 账本文件"""
    path = tmp_path / 'root.db'
    conn = sqlite3.connect(path)
    conn.execute('CREATE TABLE records (id INTEGER PRIMARY KEY, 金额 REAL)')
    conn.execute("INSERT INTO records (金额) VALUES (100.5)")
    conn.commit()
    conn.close()
    return path


def read_bytes(path):
    with open(path, 'rb') as f:
        return f.read()


def test_encrypt_decrypt_bytes_roundtrip():
    data = b'hello bookkeeping \xe8\xb4\xa6\xe6\x9c\xac'
    blob = encrypt_bytes(data, 'pw123456')
    assert blob.startswith(MAGIC)
    assert decrypt_bytes(blob, 'pw123456') == data


def test_encrypt_bytes_uses_random_salt_and_nonce():
    data = b'same data'
    assert encrypt_bytes(data, 'pw') != encrypt_bytes(data, 'pw')


def test_decrypt_wrong_password_raises():
    blob = encrypt_bytes(b'data', 'right-password')
    with pytest.raises(WrongPasswordError):
        decrypt_bytes(blob, 'wrong-password')


def test_decrypt_corrupt_or_plain_data_raises():
    with pytest.raises(CorruptFileError):
        decrypt_bytes(b'not an encrypted file at all', 'pw')
    blob = bytearray(encrypt_bytes(b'data', 'pw'))
    blob[-1] ^= 0xFF  # 篡改密文，GCM 认证失败
    with pytest.raises((WrongPasswordError, CorruptFileError)):
        decrypt_bytes(bytes(blob), 'pw')


def test_is_encrypted_file(plaintext, tmp_path):
    assert not is_encrypted_file(str(plaintext))
    enc = tmp_path / 'enc.db'
    encrypt_file(str(plaintext), str(enc), 'pw')
    assert is_encrypted_file(str(enc))
    assert not is_encrypted_file(str(tmp_path / 'missing.db'))


def test_encrypt_decrypt_file_roundtrip(plaintext, tmp_path):
    enc = tmp_path / 'enc.db'
    encrypt_file(str(plaintext), str(enc), 'pw')
    # 密文中不应出现明文 SQL 内容
    assert b'CREATE TABLE' not in read_bytes(enc)
    dec = tmp_path / 'dec.db'
    decrypt_file(str(enc), str(dec), 'pw')
    assert read_bytes(dec) == read_bytes(plaintext)


def test_encrypt_file_in_place_and_already_encrypted(plaintext):
    original = read_bytes(plaintext)
    encrypt_file(str(plaintext), str(plaintext), 'pw')
    assert is_encrypted_file(str(plaintext))
    assert read_bytes(plaintext) != original
    with pytest.raises(AlreadyEncryptedError):
        encrypt_file(str(plaintext), str(plaintext), 'pw')
    decrypt_file(str(plaintext), str(plaintext), 'pw')
    assert read_bytes(plaintext) == original


def test_wrong_password_does_not_corrupt_file(plaintext):
    encrypt_file(str(plaintext), str(plaintext), 'pw')
    before = read_bytes(plaintext)
    with pytest.raises(WrongPasswordError):
        decrypt_file(str(plaintext), str(plaintext), 'wrong')
    assert read_bytes(plaintext) == before  # 原子写：失败时原文件不变


def test_change_password_file(plaintext):
    encrypt_file(str(plaintext), str(plaintext), 'old-password')
    change_password_file(str(plaintext), 'old-password', 'new-password')
    with pytest.raises(WrongPasswordError):
        decrypt_file(str(plaintext), str(plaintext), 'old-password')
    dec = str(plaintext) + '.dec'
    decrypt_file(str(plaintext), dec, 'new-password')
    conn = sqlite3.connect(dec)
    row = conn.execute('SELECT 金额 FROM records').fetchone()
    conn.close()
    assert row[0] == 100.5


def test_change_password_wrong_old_raises(plaintext):
    encrypt_file(str(plaintext), str(plaintext), 'old-password')
    before = read_bytes(plaintext)
    with pytest.raises(WrongPasswordError):
        change_password_file(str(plaintext), 'not-old', 'new-password')
    assert read_bytes(plaintext) == before


def test_encrypted_db_is_valid_sqlite_after_decrypt(plaintext, tmp_path):
    """验收标准：解密后的库可被 sqlite 正常打开且数据完整"""
    enc = tmp_path / 'enc.db'
    encrypt_file(str(plaintext), str(enc), 'pw')
    dec = tmp_path / 'dec.db'
    decrypt_file(str(enc), str(dec), 'pw')
    conn = sqlite3.connect(dec)
    rows = conn.execute('SELECT id, 金额 FROM records').fetchall()
    conn.close()
    assert rows == [(1, 100.5)]


def test_atomic_write_leaves_no_tmp_on_success(plaintext):
    encrypt_file(str(plaintext), str(plaintext), 'pw')
    assert not any(f.endswith(f'.tmp-{os.getpid()}') for f in os.listdir(os.path.dirname(plaintext)))
