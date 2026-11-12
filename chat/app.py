import os, re, httpx
from fastapi import FastAPI
from pydantic import BaseModel
app=FastAPI(title="Local AI Shopping Assistant")
PRODUCTS_URL=os.getenv("PRODUCTS_URL","http://localhost:8001")
SEARCH_URL=os.getenv("SEARCH_URL","http://localhost:8002")
RECOMMENDATIONS_URL=os.getenv("RECOMMENDATIONS_URL","http://localhost:8005")
class ChatIn(BaseModel):
    message:str
    user_id:str="guest"
@app.get("/health")
def health(): return {"status":"ok","service":"chat"}
@app.post("/chat")
async def chat(body:ChatIn):
    msg=body.message.lower().strip()
    async with httpx.AsyncClient(timeout=10) as c:
        if any(x in msg for x in ["recommend","suggest","what should","popular","trending"]):
            r=await c.get(f"{RECOMMENDATIONS_URL}/recommendations",params={"limit":4}); products=r.json()["results"]
            return {"intent":"recommendation","reply":"Here are some products I'd recommend based on ratings, category relevance and popularity.","products":products}
        if any(x in msg for x in ["hi","hello","hey"]):
            return {"intent":"greeting","reply":"Hi! I'm ShopSphere, your local shopping assistant. Ask me to find products, suggest something, or search within a budget.","products":[]}
        budget_match=re.search(r"(?:under|below|less than|within|budget of)\s*₹?\s*([0-9,]+)",msg)
        max_price=int(budget_match.group(1).replace(",","")) if budget_match else None
        category_words=["phone","headphone","laptop","computer","watch","speaker","tablet","shoes","webcam","keyboard"]
        q=next((w for w in category_words if w in msg),body.message)
        params={"q":q}
        if max_price: params["max_price"]=max_price
        r=await c.get(f"{SEARCH_URL}/search",params=params)
        products=r.json()["results"][:5]
        if products:
            prefix=f"Found {len(products)} matching product(s)"
            if max_price: prefix+=f" under ₹{max_price:,}"
            return {"intent":"product_search","reply":prefix+". Here are the best matches.","products":products}
        return {"intent":"fallback","reply":"I can help find products, filter by budget, or recommend popular items. Try: 'headphones under 5000' or 'recommend a laptop'.","products":[]}
