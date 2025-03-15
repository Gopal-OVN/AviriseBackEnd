from sqlalchemy.orm import Session
import json
from fastapi import HTTPException,status
from fastapi import Query
from typing import Optional
from app.models.user import User
from app.models.state import State
from app.models.city import City
from app.models.country import Country
from app.models.address_book import AddressBookModel
from app.schemas.address_book import GetAddressBookSchema,CreateAddressBookSchema, UpdateAddressBookSchema
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import text




def get_all_address_books(
    db: Session, 
    current_user: User, 
    page: int = 1, 
    page_size: int = 20, 
    is_active: Optional[int] = None, 
    is_deleted: Optional[int] = None, 
    pincode: Optional[str] = None, 
    # customer_id: Optional[int] = None
):
    """Fetch all address books based on filters."""
    try:
        query = db.query(AddressBookModel).filter(AddressBookModel.is_deleted == False,AddressBookModel.is_manual_generate == True)
        # ,AddressBookModel.is_manual_generate == True
        if is_active is not None:
            query = query.filter(AddressBookModel.is_active == is_active)
        # if name:
        #     query = query.filter(AddressBookModel.name.ilike(f"%{name}%"))
        if pincode:
            query = query.filter(AddressBookModel.pincode == pincode)
        # if customer_id:
        #     query = query.filter(AddressBookModel.customer_id == customer_id)
# offset((page - 1) * page_size).limit(page_size).
        # Apply pagination
        address_books = query.all()

        if not address_books:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No address books found"
            )
        

        for addressBook in address_books:
            addressBook.state_name = db.query(State.name).filter(State.id == addressBook.state_id).scalar()  
            addressBook.city_name = db.query(City.name).filter(City.id == addressBook.city_id).scalar()  


        return address_books

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_address_book_by_id(db: Session, address_book_id: int):
    """Get a address_book by ID."""
    # Query the database to find the address_book by ID, ensuring it's not marked as deleted
    return db.query(AddressBookModel).filter(AddressBookModel.address_book_id == address_book_id, AddressBookModel.is_deleted == False).first()


def create_address_book(db: Session, address_book_service: CreateAddressBookSchema, current_user: User):
    """Create a new address_book."""
    
    # Create a new address_book instance with provided data
    address_book_data = address_book_service.dict()
    # address_book_data["created_by"] = current_user.user_id  # Add created_by manually

    # new_address_book = AddressBookModel(**address_book_data)

    if address_book_data.get("is_manual_generate", True):
        address_book_data["created_by"] = current_user.user_id  # Add created_by manually

        new_address_book = AddressBookModel(**address_book_data)

        # Add the new address_book to the database session and commit the changes
        db.add(new_address_book)
        db.commit()
        db.refresh(new_address_book)

    return new_address_book

    # Add the new address_book to the database session and commit the changes
    # db.add(new_address_book)
    # db.commit()
    # db.refresh(new_address_book)
    
    # Return the newly created address_book
    # return new_address_book


def update_address_book(db: Session, address_book_id: int,update_address_book_service : UpdateAddressBookSchema):
    """
    Update an existing company with the provided data.
    """
    db_address_book = db.query(AddressBookModel).filter(AddressBookModel.address_book_id == address_book_id, AddressBookModel.is_deleted == False).first()
    
    if not db_address_book:
        raise HTTPException(status_code=404, detail="Address book not found ")
        
    
    if db_address_book:
        # Use company.dict() to get only the fields that were updated (exclude_unset=True)
        for key, value in update_address_book_service.dict(exclude_unset=True).items():
            setattr(db_address_book, key, value)
        db.commit()  # Commit the changes
        db.refresh(db_address_book)  # Refresh to reflect the updates
        return db_address_book
    # return None



def delete_address_book(db: Session, address_book_id: int):
    """
    Soft delete a company by marking it as deleted (is_deleted = True).
    """

    
    db_address_book = db.query(AddressBookModel).filter(AddressBookModel.address_book_id == address_book_id, AddressBookModel.is_deleted == False).first()
    
    if not db_address_book:
        raise HTTPException(status_code=404, detail="Address Book not found or already deleted")
        
    
    
    db_address_book.is_deleted = True  # Mark as deleted (soft delete)
    db_address_book.is_active = False
    db.commit()  # Commit the changes
    db.refresh(db_address_book)  # Refresh to update the state
    
    return db_address_book


