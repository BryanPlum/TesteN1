import random
import re
import bcrypt

def generate_code():
    return str(random.randint(100000, 999999))

def validate_password(password):
    if len(password) < 8:
        return "A senha deve ter pelo menos 8 caracteres"

    if not re.search(r"[A-Z]", password):
        return "A senha deve ter letra maiúscula"

    if not re.search(r"[a-z]", password):
        return "A senha deve ter letra minúscula"

    if not re.search(r"\d", password):
        return "A senha deve ter número"

    return None

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())