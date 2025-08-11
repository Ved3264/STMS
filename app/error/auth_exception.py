from fastapi import HTTPException
from streamlit import status

def get_user_except():
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return credentials_exception
def email_check():
    credential = HTTPException(status_code=400, detail="Email already registered")
    return credential