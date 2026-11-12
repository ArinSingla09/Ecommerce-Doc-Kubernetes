import os, httpx
from fastapi import FastAPI
app=FastAPI(title="Recommendation Service")
PRODUCTS_URL=os.getenv("PRODUCTS_URL","http://localhost:8001")
@app.get("/health")
def health(): return {"status":"ok","service":"recommendations"}
@app.get("/recommendations")
async def recommend(product_id:int|None=None, category:str|None=None, limit:int=4):
    async with httpx.AsyncClient(timeout=8) as c:
        r=await c.get(f"{PRODUCTS_URL}/products"); r.raise_for_status(); products=r.json()
    selected=next((p for p in products if p["id"]==product_id),None)
    target=category or (selected["category"] if selected else None)
    ranked=[]
    for p in products:
        if product_id and p["id"]==product_id: continue
        score=p["rating"]*2 + min(p["stock"],20)*0.05
        if target and p["category"]==target: score+=3
        if selected:
            overlap=len(set(p["tags"]) & set(selected["tags"]))
            score+=overlap*1.5
        ranked.append({**p,"recommendation_score":round(score,2)})
    ranked.sort(key=lambda x:x["recommendation_score"],reverse=True)
    return {"strategy":"category + tag similarity + rating/popularity","results":ranked[:max(1,min(limit,20))]}
