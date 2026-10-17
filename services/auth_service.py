from werkzeug.security import generate_password_hash, check_password_hash
from models.user_model import find_by_identifier, find_by_email, create_user

def register(name, email, password, created_at, role='user'):
    return create_user(name, email, generate_password_hash(password), created_at, role=role)

def authenticate(identifier, password):
    user = find_by_identifier(identifier)
    if user and check_password_hash(user["password"], password):
        return user
    return None

