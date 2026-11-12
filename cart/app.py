import os, httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
app=FastAPI(title="Cart Service")
PRODUCTS_URL=os.getenv("PRODUCTS_URL","http://localhost:8001")
CARTS={}
class AddItem(BaseModel):
    user_id:str="guest"
    product_id:int
    quantity:int=1
@app.get("/health")
def health(): return {"status":"ok","service":"cart"}
@app.get("/cart/{user_id}")
async def get_cart(user_id:str):
    items=CARTS.get(user_id,{})
    async with httpx.AsyncClient() as c:
        response=await c.get(f"{PRODUCTS_URL}/products")
        products={p["id"]:p for p in response.json()}
    result=[]; total=0
    for pid,qty in items.items():
        p=products.get(pid)
        if p:
            line={**p,"quantity":qty,"subtotal":p["price"]*qty}; total+=line["subtotal"]; result.append(line)
    return {"user_id":user_id,"items":result,"total":total}
@app.post("/cart/items")
async def add_item(item:AddItem):
    if item.quantity<1: raise HTTPException(400,"Quantity must be positive")
    async with httpx.AsyncClient() as c:
        r=await c.get(f"{PRODUCTS_URL}/products/{item.product_id}")
        if r.status_code!=200: raise HTTPException(404,"Product not found")
        product=r.json()
    cart=CARTS.setdefault(item.user_id,{})
    new_qty=cart.get(item.product_id,0)+item.quantity
    if new_qty>product["stock"]: raise HTTPException(400,"Not enough stock")
    cart[item.product_id]=new_qty
    return await get_cart(item.user_id)
@app.delete("/cart/{user_id}/items/{product_id}")
async def remove_item(user_id:str,product_id:int):
    CARTS.setdefault(user_id,{}).pop(product_id,None)
    return await get_cart(user_id)
