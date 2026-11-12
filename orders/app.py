from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, timezone
from uuid import uuid4
app=FastAPI(title="Order Service")
ORDERS=[]
class OrderIn(BaseModel):
    user_id:str="guest"
    items:list[dict]
    total:float
@app.get("/health")
def health(): return {"status":"ok","service":"orders"}
@app.post("/orders")
def create_order(order:OrderIn):
    record={"order_id":str(uuid4()),"user_id":order.user_id,"items":order.items,"total":order.total,"status":"PLACED","created_at":datetime.now(timezone.utc).isoformat()}
    ORDERS.append(record); return record
@app.get("/orders/{user_id}")
def get_orders(user_id:str): return [o for o in ORDERS if o["user_id"]==user_id]
