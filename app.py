from fastapi import FastAPI, File, Header, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import FastAPI, File, Header, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import pandas as pd
import jwt
from fastapi import FastAPI, Header, HTTPException
import tempfile
# from awswrangler import S3
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

        # validate file size
    if len(file) > 1000000:
        raise HTTPException(status_code=400, detail="File size exceeded the limit")

        # write the bytes to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, mode='w+b') as temp:
        temp.write(file)
        temp.seek(0)
        # read the CSV file and check the column names
        df = pd.read_csv(temp.name)
        if set(df.columns) != {"partner_name","partner_id","user_id","amount_used"}:
            raise HTTPException(status_code=400, detail="Invalid column names")
    
    ##to write in local storage
        else:
            with open("./downloaded_corr_data.csv", "wb") as f:
                f.write(file)
    return {"file_size": len(file),"upload_status":True}

@app.get("/download")
async def create_download_file(x_token: str = Header(None)):
    decoded = verify_jwt(x_token)
    if decoded["sub"] != "testuser":
        raise HTTPException(status_code=400, detail="Not authenticated")
        # Read CSV file from S3 bucket
    # s3 = S3()
    # df = s3.read_csv(bucket='my-bucket', key='path/to/file.csv')
    # #Return the Dataframe as a file response
    # return FileResponse(df.to_csv(), headers={'Content-Disposition': 'attachment;filename=file.csv'})
    # return FileResponse(path='created_file.csv', headers={'Content-Disposition': 'attachment;filename=file.csv'})

@app.get("/")
async def read_root():
    return {"Hello": "World"}

import sqlite3

def add_partner_details(partner_name: str, fnf: str, max_credit_limit: int):
    conn = sqlite3.connect('partners.db')
    c = conn.cursor()
    c.execute("""
CREATE TABLE IF NOT EXISTS partners (
    partner_name TEXT, 
    fnf TEXT, 
    max_credit_limit INTEGER
)""")
    c.execute("INSERT INTO partners (partner_name, fnf, max_credit_limit) VALUES (?,?,?)", (partner_name, fnf, max_credit_limit))
    conn.commit()
    conn.close()
@app.post("/partner-details")
async def add_partner_details_api(partner_name: str, fnf: str, max_credit_limit: int, x_token: str = Header(None)):
    decoded = verify_jwt(x_token)
    if decoded["sub"] != "testuser":
        raise HTTPException(status_code=400, detail="Not authenticated")
    add_partner_details(partner_name, fnf, max_credit_limit)
    return {"message": "Partner details added successfully"}

