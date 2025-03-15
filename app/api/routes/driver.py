from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.driver import get_allDriversService, create_driverService, delete_driverService
from app.schemas.driver import DriverCreate, DriverResponse, DeleteResponse
from app.utils.auth import get_current_user
from app.models.user import User
from app.models.drivers import DriverModel


router = APIRouter()

@router.get("/", status_code=status.HTTP_200_OK)
def get_list_drivers_endpoint(
     db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
	
):	
    db_drivers = db.query(DriverModel).filter(DriverModel.is_deleted == False).all()
    
    return {
        "message": "Drivers retrieved successfully",
        "drivers": db_drivers
    }
    
    
@router.put("/{driver_id}", status_code=status.HTTP_200_OK)
def get_driver_endpoint(driver_id: int, db: Session = Depends(get_db)):
    db_driver = db.query(DriverModel).filter(DriverModel.driver_id == driver_id, DriverModel.is_deleted == False).first()
    
    return {
        "message": "Drivers retrieved successfully",
        "drivers": db_driver
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_driver(
    driver: DriverCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):  
    try:
        new_driver = create_driverService(
            db=db,
            driver_data=driver,
            current_user=current_user
        )
        
        created_by_name = db.query(User).filter(User.user_id == new_driver.created_by).first().first_name
        
        return { 
            "message": " Driver created successfully",
            "service_type": new_driver, 
            "created_by_name": created_by_name 
            }
        
    except HTTPException as e:
        raise e


# @router.get("/{driver_id}", response_model=schemas.DriverResponse)
# def get_driver(driver_id: int, db: Session = Depends(get_db)):
#     driver = services.get_driver(db, driver_id)
#     if not driver:
#         raise HTTPException(status_code=404, detail="Driver not found")
#     return driver




@router.delete("/{driver_id}", response_model=DeleteResponse)
def delete_driver_endpoint(
    driver_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    
    """ Soft delete a payment by ID."""
    
    driver = delete_driverService(db, driver_id)
    
    if  driver is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    return {"message" : "Driver Mode deeleted successfully"}
