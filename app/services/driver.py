from sqlalchemy.orm import Session
from app.models.drivers import DriverModel
from app.schemas.driver import DriverCreate, DriverUpdate
from app.models.user import User




def create_driverService(db: Session, driver_data: DriverCreate, current_user: User):
    # Create new driver instance
    
    
    if db.query(DriverModel).filter(DriverModel.name == driver_data.name).first():
        raise HTTPException(status_code=400, detail="Driver with this name already exists")
    
    new_driver = DriverModel(
        user_id=driver_data.user_id,
        name =driver_data.name,
        license_no=driver_data.license_no,
        created_by=current_user.user_id,
        is_active=driver_data.is_active,
          
    )
    
    # Add and commit driver to the database
    db.add(new_driver)
    db.commit()
    db.refresh(new_driver)
    
    return new_driver




def get_allDriversService(db: Session,current_user: User):
    """Get all active Drivers"""
    
    Drivers = db.query(DriverModel).filter(DriverModel.is_deleted == False).all()
    

def get_driver(db: Session, driver_id: int):
    return db.query(DriverModel).filter(DriverModel.driver_id == driver_id).first()




# def update_driver(db: Session, driver_id: int, update_data: DriverUpdate):
#     driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
#     if driver:
#         for key, value in update_data.dict(exclude_unset=True).items():
#             setattr(driver, key, value)
#         db.commit()
#         db.refresh(driver)
#     return driver

def delete_driverService(db: Session, driver_id: int):
    """Soft delete a role."""
    
    db_driver = db.query(DriverModel).filter(DriverModel.driver_id == driver_id, DriverModel.is_deleted == False).first()
    
    if not db_driver:
        raise HTTPException(status_code=404, detail="Driver not found or already deleted")
    
    # Mark the driver as deleted and inactive
    db_driver.is_deleted = True
    db_driver.is_active = False
    db.commit()
    db.refresh(db_driver)
    
    return db_driver
