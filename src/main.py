from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import List
import databases
import sqlalchemy
from jose import JWTError, jwt

DATABASE_URL = "sqlite:///ecommerce.db"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

products = sqlalchemy.Table(
    "products",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column("price", sqlalchemy.Float),
)

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

class Product(BaseModel):
    id: int
    name: str
    price: float

class User(BaseModel):
    username: str

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return User(username=username)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.on_event("startup")
async def startup():
    engine = sqlalchemy.create_engine(DATABASE_URL)
    metadata.create_all(engine)
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/products/", response_model=List[Product])
async def get_products(current_user: User = Depends(get_current_user)):
    query = products.select()
    return await database.fetch_all(query)

@app.post("/products/", response_model=Product)
async def create_product(product: Product, current_user: User = Depends(get_current_user)):
    query = products.insert().values(name=product.name, price=product.price)
    last_record_id = await database.execute(query)
    return {**product.dict(), "id": last_record_id}