from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Product Service", version="1.0")
PRODUCTS = [
 {"id":1,"name":"Nova X Smartphone","category":"Phones","brand":"Nova","price":24999,"rating":4.5,"stock":18,"description":"5G smartphone with 128GB storage and an excellent camera","tags":["phone","5g","camera","android"]},
 {"id":2,"name":"Pulse Pro Headphones","category":"Audio","brand":"Pulse","price":3999,"rating":4.4,"stock":42,"description":"Wireless noise cancelling over-ear headphones","tags":["headphones","wireless","audio","noise cancelling"]},
 {"id":3,"name":"AeroBook 14 Laptop","category":"Computers","brand":"Aero","price":62999,"rating":4.7,"stock":12,"description":"Lightweight laptop with 16GB RAM and 512GB SSD","tags":["laptop","computer","work","student"]},
 {"id":4,"name":"FitTrack Smartwatch","category":"Wearables","brand":"FitTrack","price":5999,"rating":4.1,"stock":30,"description":"Fitness smartwatch with heart rate and sleep tracking","tags":["watch","fitness","wearable"]},
 {"id":5,"name":"Echo Mini Speaker","category":"Audio","brand":"Echo","price":2499,"rating":4.2,"stock":25,"description":"Compact Bluetooth portable speaker","tags":["speaker","bluetooth","audio"]},
 {"id":6,"name":"Click 4K Webcam","category":"Accessories","brand":"Click","price":3299,"rating":4.3,"stock":20,"description":"4K webcam for meetings and streaming","tags":["webcam","camera","work"]},
 {"id":7,"name":"Nova X Power Bank","category":"Accessories","brand":"Nova","price":1799,"rating":4.0,"stock":55,"description":"20000mAh fast charging power bank","tags":["charger","power bank","phone"]},
 {"id":8,"name":"MechLite Keyboard","category":"Accessories","brand":"MechLite","price":4499,"rating":4.6,"stock":16,"description":"Mechanical keyboard with tactile switches","tags":["keyboard","computer","gaming"]},
 {"id":9,"name":"VisionTab 11 Tablet","category":"Computers","brand":"Vision","price":21999,"rating":4.3,"stock":14,"description":"11 inch tablet for reading, entertainment and study","tags":["tablet","student","screen"]},
 {"id":10,"name":"RunFlex Shoes","category":"Lifestyle","brand":"RunFlex","price":2999,"rating":4.2,"stock":38,"description":"Lightweight running shoes for daily training","tags":["shoes","running","fitness"]}
]
@app.get("/health")
def health(): return {"status":"ok","service":"products"}
@app.get("/products")
def list_products(category: Optional[str]=None):
    return [p for p in PRODUCTS if not category or p["category"].lower()==category.lower()]
@app.get("/products/{product_id}")
def get_product(product_id:int):
    for p in PRODUCTS:
        if p["id"]==product_id: return p
    raise HTTPException(404,"Product not found")
@app.get("/categories")
def categories(): return sorted({p["category"] for p in PRODUCTS})
