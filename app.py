from fastapi import FastAPI, File, Header, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import FastAPI, File, Header, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import pandas as pd
import jwt
from fastapi import FastAPI, Header, HTTPException

import io


app = FastAPI()

security = HTTPBasic()

SECRET_KEY = "mysecretkey"

def create_jwt(data: dict):
    encoded = jwt.encode(data, SECRET_KEY, algorithm='HS256')
    return encoded.decode()

def verify_jwt(token: str):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return decoded
    except jwt.PyJWTError:
        raise HTTPException(status_code=400, detail="Invalid token")

@app.post("/login")
async def login(username: str, password: str):
    # hardcoded username and password
    valid_username = "testuser"
    valid_password = "testpassword"

    # check if the provided username and password match the hardcoded values
    if username != valid_username or password != valid_password:
        raise HTTPException(status_code=400, detail="Invalid username or password")

    # create a JWT token for the user
    data = {"sub": username}
    token = create_jwt(data)

    # return the token to the user
    return {"token": token}

@app.post("/upload")
async def create_upload_file(file: bytes = File(...), x_token: str = Header(None)):
    decoded = verify_jwt(x_token)
    if decoded["sub"] != "testuser":
        raise HTTPException(status_code=400, detail="Not authenticated")
    with open("./downloaded_data.csv", "wb") as f:
        f.write(file)
    return {"file_size": len(file)}

@app.get("/download")
async def create_download_file(x_token: str = Header(None)):
    decoded = verify_jwt(x_token)
    if decoded["sub"] != "testuser":
        raise HTTPException(status_code=400, detail="Not authenticated")
    data = {'partner_name': ['uber'], 'partner_id': ['1234'], 'user_id': ['2234'], 'amount_used': [10000]}
    df = pd.DataFrame(data)
    df.to_csv('created_file.csv', index=False)
    return FileResponse(path='created_file.csv', headers={'Content-Disposition': 'attachment;filename=file.csv'})

@app.get("/")
async def read_root():
    return {"Hello": "World"}

