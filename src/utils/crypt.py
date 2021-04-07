from passlib.context import CryptContext


passwordContext = CryptContext(schemes = ["bcrypt"], deprecated = "auto")

def create_crypt_password(password: str):
    return passwordContext.hash(password)

def verify_crypt_password(password, hash_password):
    return passwordContext.verify(password, hash_password)