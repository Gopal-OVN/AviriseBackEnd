from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.utils.auth import get_current_user
from typing import Optional, List, Dict
from app.models.user import User
from datetime import datetime
from app.models.address_book import AddressBookModel
from app.schemas.address_book import GetAddressBookSchema, CreateAddressBookSchema,UpdateAddressBookSchema,DeleteAddressBookSchema
from app.services.address_book import get_all_address_books,get_address_book_by_id,create_address_book,update_address_book,delete_address_book

router = APIRouter()

@router.get("/", status_code=status.HTTP_200_OK)
def get_all_address_books_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, description="Page number"),
    page_size: int = Query(10, description="Number of records per page"),
    is_active: Optional[int] = Query(None, description="Filter by active status"),
    is_deleted: Optional[int] = Query(None, description="Filter by deleted status"),
    pincode: Optional[str] = Query(None, description="Filter by pincode"),
    # customer_id: Optional[int] = Query(None, description="Filter by customer ID")
):
    """
    Endpoint to retrieve all available address_books using a stored procedure.
    """
    try:
        address_books = get_all_address_books(
            db, current_user, page, page_size, is_active, is_deleted, pincode
        )
        total = len(address_books)  # Assuming pagination is handled at DB level

        return {
            "message": "Address books retrieved successfully",
            "total": total,
            "address_books": address_books
        }
    except HTTPException as e:
        return {
            "message": e.detail,
            "address_books": []
        }, e.status_code
    

@router.get("/{address_book_id}", status_code=status.HTTP_200_OK)
def get_address_book_endpoint(address_book_id: int, db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
   
    all_users = db.query(User).all()
    user_dict = {user.user_id: user.first_name for user in all_users}
    # Query the database to find the address_book by ID, ensuring it's not marked as deleted
    address_book = db.query(AddressBookModel).filter(AddressBookModel.address_book_id == address_book_id, AddressBookModel.is_deleted == False).first()

    
    
    # Add the created_by_name to the response
    if address_book:
        address_book.created_by_name = user_dict.get(address_book.created_by, 'Unknown')

    
    address_book = get_address_book_by_id(db, address_book_id)
    if not address_book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address Book not found")
    return {
        "message": "Address Book retrieved successfully",
        "addressbooks": address_book
    }



@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_new_address_book(
    addressBook:CreateAddressBookSchema,
    db: Session=Depends(get_db),
    current_user: User= Depends(get_current_user)
    
    ):
   
    try:
        new_address_book = create_address_book(db=db,address_book_service=addressBook,current_user=current_user)
        
    
    except  Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error creating address book:{str(e)}"
        )
        
    return{
        "message": "Address book was create successfully",
        "addressbooks": new_address_book
        }


@router.put("/{address_book_id}")
async def update_existing_address_book(
    address_book_id: int,
    update_addressBook: UpdateAddressBookSchema,
    db: Session = Depends(get_db),
    current_user: User= Depends(get_current_user)
    
    ):
    """
    Endpoint to update an existing company.

    Updates the company data in the database using the provided company ID
    and the new data. Returns the updated company details if found. 
    Otherwise, returns a 404 error if the company does not exist.
    """
    # Update the company data in the database using the provided company ID
    try: 
        updated_address_book = update_address_book(db=db, address_book_id=address_book_id, update_address_book_service=update_addressBook)
    
        # If the company is not found, raise a 404 error
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company not found : {str(e)}"
        )
    # Return the updated company data
    return{
        "message": "Address book was updated successfully",
        "addressbooks": updated_address_book
        } 


@router.delete("/{address_book_id}",  response_model= DeleteAddressBookSchema)
def delete_address_book_endpoint(
    address_book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    """
    Soft delete a role by ID.
    """
   
        # Attempt to delete the role
    deleted_address_book = delete_address_book(db, address_book_id)
    
    
    if deleted_address_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address Book not found"
            
        )
    return {"message" : "Addrress book deleted successfully",}




