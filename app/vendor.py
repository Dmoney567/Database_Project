from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi import HTTPException
import mysql.connector
 
from app.database_Connection import get_db_conn
router = APIRouter()


@router.post("/dashboard/vendors/create")
async def create_vendor(
    vend_name: str = Form(),
    vend_address: str = Form(),
    vend_phone: str = Form(),
    vend_email: str = Form()
):
    conn = get_db_conn()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO VENDOR (vend_name, vend_address, vend_phone, vend_email)
            VALUES (%s, %s, %s, %s)
        """, (vend_name, vend_address, vend_phone, vend_email))

        conn.commit()

    finally:
        cursor.close()
        conn.close()

    return RedirectResponse(url="/dashboard", status_code=302)


@router.post("/dashboard/vendors/update")
async def update_vendor(
    vendor_id: int = Form(),
    vend_name: str = Form(),
    vend_address: str = Form(),
    vend_phone: str = Form(),
    vend_email: str = Form()
):
    conn = get_db_conn()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE VENDOR
            SET vend_name = %s,
                vend_address = %s,
                vend_phone = %s,
                vend_email = %s
            WHERE vend_id = %s
        """, (vend_name, vend_address, vend_phone, vend_email, vendor_id))

        conn.commit()

    finally:
        cursor.close()
        conn.close()

    return RedirectResponse(url="/dashboard", status_code=302)


@router.post("/dashboard/vendors/delete")
async def delete_vendor(vendor_id: int = Form()):
    conn = get_db_conn()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "DELETE FROM VENDOR WHERE vend_id = %s",
            (vendor_id,)
        )
        conn.commit()

    except mysql.connector.IntegrityError:
        conn.rollback()
        raise HTTPException(
            status_code=400,
            detail="Cannot delete vendor: they have existing production orders."
        )

    finally:
        cursor.close()
        conn.close()

    return RedirectResponse(url="/dashboard", status_code=302)