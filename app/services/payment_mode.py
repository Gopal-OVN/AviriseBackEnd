from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.models.payment_mode import PaymentMode 
from app.models.user import User
from app.schemas.payment_mode import CreatePaymentMode, UpdatePaymentModeSchema
from datetime import datetime
from app.utils.auth import get_current_user
from app.services.common_validate_data import get_user_name, validate_payment_name
from app.models.payment_mode import PaymentMode as PaymentModel




#Get Payment
def get_payment(db: Session, payment_id: int):
    """Get a payment by ID."""
    # Query the database to find the payment by ID, ensuring it's not marked as deleted
    return db.query(PaymentModel).filter(PaymentModel.payment_id == payment_id, PaymentModel.is_deleted == False).first()


#Get all Payments
def get_all_payments(db: Session, current_user: User):
    """Get all active payments."""
    # Query the database to get all payments that are not marked as deleted
    payments = db.query(PaymentModel).filter(PaymentModel.is_deleted == False).order_by(PaymentModel.updated_at.desc()).all()
    
    # If no payments are found, raise a 404 error
    if not payments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No payments found"
        )
    
    # Return the list of payments if found
    return payments


#create Payment


def create_payment_mode(db: Session, payment_create_service_data: CreatePaymentMode, current_user: User):
    # Check if payment_name is unique
    
    
    if db.query(PaymentMode).filter(PaymentMode.payment_name == payment_create_service_data.payment_name).first():
    
        raise HTTPException(status_code=400, detail="Payment mode with this name already exists")

    new_payment_mode = PaymentMode(
        payment_name=payment_create_service_data.payment_name,
        description=payment_create_service_data.description,
        is_active=payment_create_service_data.is_active,
        created_by=current_user.user_id  # Add created_by
    )

    db.add(new_payment_mode)
    db.commit()
    db.refresh(new_payment_mode)

    return new_payment_mode




def delete_payment(db: Session, payment_id: int):
    """Soft delete a payment."""
    # Query the payment to be deleted, ensuring it isn't already deleted
    db_payment = db.query(PaymentModel).filter(PaymentModel.payment_id == payment_id, PaymentModel.is_deleted == False).first()
    
    # If payment is not found or already deleted, raise a 404 error
    if not db_payment:
        raise HTTPException(status_code=404, detail="PaymentMode not found or already deleted")
    
    # Mark the payment as deleted and inactive
    db_payment.is_deleted = True
    db_payment.is_active = False
    db.commit()
    db.refresh(db_payment)
    
    # Return the soft-deleted payment
    return db_payment


def update_payment(db: Session, payment_id: int, payment_data: UpdatePaymentModeSchema):
    """Update an existing payment."""
    # Query the payment to update, ensuring it isn't marked as deleted
    db_payment = (db.query(PaymentModel)
                  .filter(PaymentModel.payment_id == payment_id, PaymentModel.is_deleted == False)
                  .first())
    
    # If payment is not found, raise a 404 error
    if not db_payment:
        raise HTTPException(status_code=404, detail="PaymentMode not found")
    
    # Check if the new name is unique (ignore the current record)
    existing_payment = (
        db.query(PaymentModel)
        .filter(PaymentModel.payment_name ==payment_data.payment_name, PaymentModel.payment_id !=payment_id)
        .first()
    )
    
    if existing_payment:
        raise HTTPException(
            status_code =400,
            detail = f"Payment Mode with name '{payment_data.payment_name}' already exists"
        )

     # Update fields dynamically
    update_data = payment_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_payment, key, value)

    db.commit()
    db.refresh(db_payment)
    
    # Return the updated payment
    return db_payment

