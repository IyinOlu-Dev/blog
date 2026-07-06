from argon2 import PasswordHasher

ph = PasswordHasher()

def hash_password(password: str) -> str:
    return ph.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    try:
        return ph.verify(hashed, plain)
    except Exception as e:
        print(f"Password verification failed: {e}")
        return False