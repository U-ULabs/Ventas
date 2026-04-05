from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Order, OrderItem, Product
from schemas import Order as OrderSchema, OrderItemBase
from auth import get_current_user
from models import User

router = APIRouter()

@router.post("/orders", response_model=OrderSchema)
def create_order(order_items: list[OrderItemBase], db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    total = 0
    order_items_db = []
    for item in order_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        if product.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Not enough stock for product {product.name}")
        total += product.price * item.quantity
        order_items_db.append(OrderItem(product_id=item.product_id, quantity=item.quantity, price=product.price))
        product.stock -= item.quantity

    order = Order(user_id=current_user.id, total=total, items=order_items_db)
    db.add(order)
    db.commit()
    db.refresh(order)
    return order

@router.get("/orders", response_model=list[OrderSchema])
def read_orders(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    orders = db.query(Order).filter(Order.user_id == current_user.id).all()
    return orders

@router.get("/orders/{order_id}", response_model=OrderSchema)
def read_order(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order