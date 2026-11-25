# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from crud import (
    create_tables,
    add_user,
    add_fertilizer,
    get_fertilizers,
    create_fertilizer_request,
    get_all_requests,
    update_request_status,
    update_fertilizer_stock,
)

app = FastAPI(title="Tea Fertilizer Distribution System API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

create_tables()


# Request Body Models (Pydantic)
class UserCreate(BaseModel):
    full_name: str
    email: str
    phone_number: str
    address: str
    role: str = "farmer"
    password: str


class FertilizerCreate(BaseModel):
    fertilizer_name: str
    description: str = ""
    quantity_kg: float
    price_per_kg: float


class FertilizerRequestCreate(BaseModel):
    farmer_id: int
    fertilizer_id: int
    requested_qty_kg: float


class StatusUpdate(BaseModel):
    status: str


class StockUpdate(BaseModel):
    quantity_change_kg: float


@app.get("/")
def home():
    return {"message": "Tea Fertilizer Distribution System API is running!"}


@app.post("/users")
def register_user(user: UserCreate):
    success, msg = add_user(
        user.full_name, user.email, user.phone_number, user.address, user.role, user.password
    )
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}


@app.get("/fertilizers")
def list_fertilizers():
    return {"fertilizers": get_fertilizers()}


@app.post("/fertilizers")
def create_fertilizer(item: FertilizerCreate):
    success, msg = add_fertilizer(
        item.fertilizer_name, item.description, item.quantity_kg, item.price_per_kg
    )
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}


@app.get("/requests")
def list_requests():
    return {"requests": get_all_requests()}


@app.post("/requests")
def submit_request(req: FertilizerRequestCreate):
    success, msg = create_fertilizer_request(req.farmer_id, req.fertilizer_id, req.requested_qty_kg)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}


@app.put("/requests/{request_id}/status")
def change_request_status(request_id: int, data: StatusUpdate):
    success, msg = update_request_status(request_id, data.status)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}


@app.put("/fertilizers/{fertilizer_id}/stock")
def change_fertilizer_stock(fertilizer_id: int, data: StockUpdate):
    success, msg = update_fertilizer_stock(fertilizer_id, data.quantity_change_kg)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}