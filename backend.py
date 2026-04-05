from fastapi import FastAPI
from database import engine, Base
from routes import user, product, order

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Shopping Store Backend", version="1.0.0")

app.include_router(user.router, prefix="/api", tags=["users"])
app.include_router(product.router, prefix="/api", tags=["products"])
app.include_router(order.router, prefix="/api", tags=["orders"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Shopping Store Backend"}