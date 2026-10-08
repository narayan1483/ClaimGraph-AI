"""
ClaimGraph AI — Devices & Products API Router.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.dependencies import get_current_user
from app.claims.schemas import DeviceBrief, ProductBrief
from app.common.schemas import SuccessResponse
from app.core.database import get_db_session
from app.devices.models import Device, Product
from app.users.models import User

router = APIRouter(prefix="/devices", tags=["Devices & Products"])


class ProductCreateRequest(BaseModel):
    name: str = Field(..., min_length=1)
    category: str = "Electronics"
    manufacturer: str = "Generic"
    model_number: str = "MOD-001"
    msrp: float = 999.0
    warranty_period_months: int = 12

class DeviceCreateRequest(BaseModel):
    serial_number: str = Field(..., min_length=1)
    product_id: Optional[str] = None
    product_name: Optional[str] = None
    category: Optional[str] = "Electronics"
    manufacturer: Optional[str] = "Generic"
    model_number: Optional[str] = "MOD-001"
    customer_id: Optional[str] = None
    purchase_price: Optional[float] = 999.0
    purchase_date: Optional[datetime] = None
    status: str = "ACTIVE"

@router.get(
    "",
    response_model=SuccessResponse[List[DeviceBrief]],
    summary="List devices",
)
async def list_devices(
    _current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[List[DeviceBrief]]:
    """List insured physical devices."""
    stmt = select(Device).options(selectinload(Device.product)).limit(100)
    res = await db.execute(stmt)
    devices = list(res.scalars().all())
    return SuccessResponse(
        data=[DeviceBrief.model_validate(d) for d in devices],
        message="Devices retrieved",
    )


@router.post(
    "",
    response_model=SuccessResponse[DeviceBrief],
    summary="Register a new device",
)
async def create_device(
    payload: DeviceCreateRequest,
    _current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[DeviceBrief]:
    """Register an insured physical device, auto-creating product catalog entry if needed."""
    prod_id = payload.product_id
    if not prod_id:
        prod_stmt = select(Product).filter(Product.name == (payload.product_name or "Standard Device")).limit(1)
        existing_prod = (await db.execute(prod_stmt)).scalars().first()
        if existing_prod:
            prod_id = existing_prod.id
        else:
            new_prod = Product(
                name=payload.product_name or "Standard Device",
                category=payload.category or "Electronics",
                manufacturer=payload.manufacturer or "Generic",
                model_number=payload.model_number or "MOD-001",
                msrp=payload.purchase_price or 999.0,
            )
            db.add(new_prod)
            await db.flush()
            prod_id = new_prod.id

    dev = Device(
        serial_number=payload.serial_number,
        product_id=prod_id,
        customer_id=payload.customer_id,
        purchase_date=payload.purchase_date,
        purchase_price=payload.purchase_price,
        status=payload.status,
    )
    db.add(dev)
    await db.commit()
    await db.refresh(dev)
    await db.refresh(dev, attribute_names=["product"])
    return SuccessResponse(
        data=DeviceBrief.model_validate(dev),
        message="Device registered successfully",
    )


@router.get(
    "/products",
    response_model=SuccessResponse[List[ProductBrief]],
    summary="List product catalog",
)
async def list_products(
    _current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[List[ProductBrief]]:
    """List insurable catalog products."""
    stmt = select(Product).limit(100)
    res = await db.execute(stmt)
    products = list(res.scalars().all())
    return SuccessResponse(
        data=[ProductBrief.model_validate(p) for p in products],
        message="Products retrieved",
    )

