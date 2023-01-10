from enum import Enum
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from fastapi import FastAPI, File, UploadFile
import io


app = FastAPI()


class PartnerName(str, Enum):
    ewi_a = "uber"
    ewi_b = "porter"
    ewa = "others"

class Item(BaseModel):
    name: str
    description: str
    price: float
    tax: str



@app.get("/partners/{partner_name}")
async def get_model(partner_name: PartnerName):
    if partner_name is PartnerName.ewi_a:
        return {"partner_name": partner_name, "message": f"Current partner is {partner_name}"}

    if partner_name.value == "Porter":
        return {"partner_name": partner_name, "message": f"Current partner is {partner_name}"}

    return {"partner_name": partner_name, "message": "Some fing EWA Partners"}

@app.post("/items/")
async def create_item(item: Item):
    return item

@app.get("/get_csv")
async def get_csv():

    df = pd.DataFrame(
        [["xxxyyy", 10], ["aabb", 20]], 
        columns=["user_id", "usage"]
    )
    return StreamingResponse(
        iter([df.to_csv(index=False)]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=data.csv"}
    )

@app.post("/upload")
def upload(file: UploadFile = File(...)):
    try:
        contents = file.file.read()
        with open(file.filename, 'wb') as f:
            f.write(contents)
    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()

    return {"message": f"Successfully uploaded {file.filename}"}