from fastapi import FastAPI, Request
from decouple import config
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from fastapi_mail import FastMail, MessageSchema,ConnectionConfig
import json
from app import EMAIL, PSWRD
import os



app = FastAPI()

EMAIL = os.getenv("EMAIL")
PSWRD = os.getenv("PSWRD")

origins = [
    "http://localhost:3000",
    "localhost:3000",
    "*"
]

conf = ConnectionConfig(
    MAIL_USERNAME = EMAIL,
    MAIL_PASSWORD = PSWRD,
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_TLS = True,
    MAIL_SSL = False
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

DIR_PATH = os.getcwd()

@app.get("/", tags=["root"])
async def read_root() -> dict:
    return {"message": "Backend is working great!!!"}

@app.get("/get_products")
async def read_db_products() -> dict:
    with open(f'{DIR_PATH}\\app\\database.json') as json_file:
        products = json.load(json_file)
    return products

@app.post("/save_project")
async def save_project(request: Request):
    data = await request.form()
    data = jsonable_encoder(data)
    if len(data.keys())==0:
        return {"message":"No data passed"}
    with open(f'{DIR_PATH}\\app\\database.json','r') as json_file:
        products = json.load(json_file)
        products["products"].append({
            "key": int(data["key"]),
            "name": data["title"],
            "size": data["size"],
            "visible": True,
        })
        print(products)
    with open(f'{DIR_PATH}\\app\\database.json','w') as json_file:
        json_file.write(json.dumps(products,indent=4))
    return {"message": "Your product has been saved successfully"}

@app.get("/delete_project/{key}")
async def save_project(key: int):
    with open(f'{DIR_PATH}\\app\\database.json','r') as json_file:
        products = json.load(json_file)
        for product in products["products"]:
            if product["key"] == key:
                products["products"].remove(product)
    with open(f'{DIR_PATH}\\app\\database.json','w') as json_file:
        json_file.write(json.dumps(products,indent=4))
    return {"message": "Your product has been deleted successfully"}

def get_template(mail,msg):
    return f"""<h1>This Mail is autogenerated and sent to both you and Binod Merchandise</h1><p>Mail: {mail}</p><p>Message: {msg}</p>"""

@app.post("/email")
async def email(request: Request):
    data = await request.form()
    data = jsonable_encoder(data)
    message = MessageSchema(
        subject="Contacted from Binod Merchandise",
        recipients=[data["email"],EMAIL],
        body=get_template(data["email"],data["message"]),
        subtype="html"
        )
    fm = FastMail(conf)
    await fm.send_message(message)
    return {"message": "Email sent successfully"}

'''
{
	"products": [
		{ "key": 1, "name": "Cool Jacket", "size": "XL", "visible": true },
		{ "key": 2, "name": "Matte black T-shirt", "size": "L", "visible": true },
		{ "key": 3, "name": "Party jacket", "size": "M", "visible": true },
		{ "key": 4, "name": "Everyday jeans", "size": "L", "visible": true },
		{ "key": 5, "name": "Pattern T-Shirt", "size": "XL", "visible": true },
		{ "key": 6, "name": "Fancy grey scarfed", "size": "M", "visible": true },
		{ "key": 7, "name": "Formal affair", "size": "S", "visible": true }
	]
}
'''