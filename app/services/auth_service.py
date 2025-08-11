from datetime import datetime, timedelta
from typing import Annotated
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from app.error.auth_exception import get_user_except
from app.vo.auth_vo import Users
from passlib.context import CryptContext
from jose import JWTError,jwt

SECRET_KEY = '197b2c37c391bed93fe80344fe73b806947a65e36206e05a1a23c2fa12702fe3'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth_bearer = OAuth2PasswordBearer(tokenUrl="/auth/token")
token_dependency = Annotated[str,Depends(oauth_bearer)]


def authentication_user(email:str,password:str,db):
    user = db.query(Users).filter(Users.email==email).first()
    if not user:
        return False
    if not bcrypt_context.verify(password,user.password):
        return False
    return user

def create_access_token(username:str,user_id:int,expires_delta:timedelta):
    encode={'sub':username,'id':user_id}
    expire=datetime.utcnow()+expires_delta
    encode.update({'exp':expire})
    return jwt.encode(encode,SECRET_KEY,algorithm=ALGORITHM)

def get_current_user(token:token_dependency):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=ALGORITHM)
        user_name = payload.get("sub")
        id  = payload.get("id")
        if user_name is None:
            raise get_user_except()
        return {"username": user_name, "id":id}
    except JWTError:
        get_user_except()
