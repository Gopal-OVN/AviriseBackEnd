from fastapi import APIRouter
from app.api.routes import auth, menu_permission_router,menu_privilege,menu, order_tracking,permission, role_permission, users, roles, company, branch, industry_type, globle_status, country, state, city,parcel_type,service_type,payment_mode,address_book,vehicle,shipment_status, driver,order_item,order



routes = APIRouter()
routes.include_router(auth.router, prefix="/auth", tags=["Auth"])
routes.include_router(users.router, prefix="/users", tags=["Users"])
routes.include_router(roles.router, prefix="/roles", tags=["Roles"])
routes.include_router(country.router, prefix="/countries", tags=["Countries"])
routes.include_router(state.router, prefix="/states", tags=["States"])
routes.include_router(city.router, prefix="/cities", tags=["Cities"])
routes.include_router(industry_type.router, prefix="/industry-type", tags=["Industry Type"])
routes.include_router(globle_status.router, prefix="/globle-status", tags=["GlobleStatus"])
routes.include_router(company.router, prefix="/companies", tags=["Companies"])
routes.include_router(branch.router, prefix="/branches", tags=["Branches"])
routes.include_router(parcel_type.router, prefix="/parcel_types", tags=["ParcelTypes"])
routes.include_router(payment_mode.router, prefix="/payment_modes", tags=["PaymentModes"])
routes.include_router(service_type.router, prefix="/service-type", tags=["Service Type"])
routes.include_router(address_book.router, prefix="/address_book", tags=["Address Book"])
routes.include_router(driver.router, prefix="/driver", tags=["Drivers"])
routes.include_router(vehicle.router, prefix="/vehicle", tags=["vehicle"])
routes.include_router(shipment_status.router, prefix="/shipment_status", tags=["Shipment Status"])
routes.include_router(order_item.router, prefix="/order_items", tags=["Order Item"])
routes.include_router(order.router, prefix="/orders", tags=["Order"])
routes.include_router(order_tracking.router, prefix="/order_tracking", tags=["Order Tracking"])
routes.include_router(menu.router, prefix="/menu", tags=["Menu"])
routes.include_router(menu_privilege.router, prefix="/menu_privilege", tags=["Menu Privilege"])
routes.include_router(role_permission.router, prefix="/role_permission", tags=["Role Permission"])
routes.include_router(permission.router, prefix="/permission", tags=["Permission"])
routes.include_router(menu_permission_router.router, prefix="/menu_permission_router", tags=["MenuPermission"])










