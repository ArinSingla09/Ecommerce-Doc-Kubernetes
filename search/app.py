import os, httpx
from fastapi import FastAPI
from rapidfuzz import fuzz
app=FastAPI(title="Search Service")
PRODUCTS_URL=os.getenv("PRODUCTS_URL","http://localhost:8001")
@app.get("/health")
def health(): return {"status":"ok","service":"search"}
@app.get("/search")
async def search(q:str="", category:str|None=None, min_price:float|None=None, max_price:float|None=None):
    async with httpx.AsyncClient(timeout=8) as c:
        r=await c.get(f"{PRODUCTS_URL}/products"); r.raise_for_status(); products=r.json()
    terms=q.lower().split()
    results=[]
    for p in products:
        if category and p["category"].lower()!=category.lower(): continue
        if min_price is not None and p["price"]<min_price: continue
        if max_price is not None and p["price"]>max_price: continue
        hay=" ".join([p["name"],p["category"],p["brand"],p["description"]," ".join(p["tags"])]).lower()
        score=max([fuzz.token_set_ratio(q.lower(),hay)] + [max(fuzz.partial_ratio(t, hay), 100 if t in hay else 0) for t in terms]) if q else 50
        if not q or score>=35: results.append({**p,"search_score":round(score,1)})
    results.sort(key=lambda x:(x["search_score"],x["rating"]),reverse=True)
    return {"query":q,"count":len(results),"results":results}
