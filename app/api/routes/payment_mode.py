from fastapi import APIRouter, HTTPException, Depends, status, Form
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.utils.auth import get_current_user
from app.models.user import User
from app.schemas.payment_mode import CreatePaymentMode, UpdatePaymentModeSchema, PaymentModeOut, DeleteResponse
from app.models.payment_mode import PaymentMode
from app.services.payment_mode import  get_all_payments, get_payment, delete_payment, update_payment,create_payment_mode


# Initialize the API router for paymentMode-related endpoints
router = APIRouter()

# response_model=PaymentModeOut,

@router.post("/",  status_code=status.HTTP_201_CREATED)
async def create_new_payment(
    payment: CreatePaymentMode,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Endpoint to create a new paymentMode.

    - **payment**: JSON payload containing `payment_name`, `description`, and `is_active`.
    - **db**: Dependency to access the database session.
    - **current_user**: Dependency to get the current logged-in user.

    Returns the created `PaymentModeOut` object.
    """
    try:
        new_payment = create_payment_mode(
            db=db,
            payment_create_service_data=payment,
            current_user=current_user
        
        
        )
    
        created_by_name = db.query(User).filter(User.user_id == new_payment.created_by).first().first_name
    
        total = db.query(PaymentMode).filter(PaymentMode.is_deleted == False).count()


        return { 
            "message": "Payment Mode created successfully",
            "total": total,
            "service_type": new_payment, 
            "created_by_name": created_by_name 
            }
    except HTTPException as e:
        # If an HTTPException occurs, raise it
        raise e



   




@router.get("/{payment_id}", status_code=status.HTTP_200_OK)
def get_payment_endpoint(payment_id: int, db: Session = Depends(get_db)):
    """
    Endpoint to retrieve a specific payment by its ID.

    - **payment_id**: The ID of the payment to be retrieved.
    - **db**: Dependency to access the database session.

    Returns the payment details if found, otherwise raises a 404 error.
    """
    # Query the database to find the payment by ID, ensuring it's not marked as deleted
    payment = db.query(PaymentMode).filter(PaymentMode.payment_id == payment_id, PaymentMode.is_deleted == False).first()

    
    # Add the created_by_name to the response
    if payment:
        payment.created_by_name = db.query(User).filter(User.user_id == payment.created_by).first().first_name

    
    payment = get_payment(db, payment_id)
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PaymentMode not found")
    return {
        "message": "PaymentMode retrieved successfully",
        "payment": payment
    }
    
    
    

    
    
@router.get("/", status_code=status.HTTP_200_OK)
def get_all_payments_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    """
    Endpoint to retrieve all available payments.

    - **db**: Dependency to access the database session.
    - **current_user**: Dependency to get the current logged-in user.

    Returns a list of payments or an appropriate message if no payments are found.
    """
    # Query the database to get all payments that are not marked as deleted
    payments = db.query(PaymentMode).filter(PaymentMode.is_deleted == False).all()

    
    # Add the created_by_name to the response
    for payment in payments:
        payment.created_by_name = db.query(User).filter(User.user_id == payment.created_by).first().first_name

    
    try:
        # Get all payments for the current user
        payments = get_all_payments(db, current_user)
    except HTTPException as e:
        # Handle exceptions and return an empty payments list with error message
        return {
            "message": e.detail,
            "payments": []
        }, e.status_code
    
    if not payments:
        return {
            "message": "No payments found in the database",
            "payments": []
        }, status.HTTP_204_NO_CONTENT

    return {
        "message": "PaymentModes retrieved sucessfully",
        "payments": payments
    }
    
    
@router.put("/{payment_id}", status_code=status.HTTP_200_OK)
def update_payment_endpoint(
    payment_id: int,
    payment_data:UpdatePaymentModeSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):    
    """
    Update an existing payment by ID.
    """
    # Construct the UpdatePaymentModeSchema schema instance from the form data
    # payment_data = UpdatePaymentModeSchema(payment_name=payment_name,description=description, is_active=is_active, is_deleted=is_deleted)

    # Call the `update_payment` function to update the payment in the database
    updated_payment = update_payment(db, payment_id, payment_data)

    return {
        "message": "PaymentMode successfully updated",
        "payment": updated_payment
    }


@router.delete("/{payment_id}", response_model= DeleteResponse)
def delete_payment_endpoint(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    """
    Soft delete a payment by ID.
    """
    
    delete_payment_Mode = delete_payment(db, payment_id)
   
    if delete_payment_Mode is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment Mode not found"
        )
    
    return {"message" : "Payment Mode deeleted successfully"}