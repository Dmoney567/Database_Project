from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import RedirectResponse
import mysql
import mysql.connector
from app.database_Connection import get_db_conn  

router = APIRouter()


@router.post("/dashboard/materials/create")
async def create_material(
    raw_mat_name: str = Form(),
    raw_mat_quantity: int = Form()
):
    conn = get_db_conn()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO RAW_MATERIAL (raw_mat_name, raw_mat_quantity)
            VALUES (%s, %s)
        """, (raw_mat_name, raw_mat_quantity))

        conn.commit()

    finally:
        cursor.close()
        conn.close()

    return RedirectResponse(url="/dashboard", status_code=302)



@router.post("/dashboard/materials/update")
async def update_material(
    raw_mat_id: int = Form(),
    raw_mat_name: str = Form(),
    raw_mat_quantity: int = Form()
):
    conn = get_db_conn()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE RAW_MATERIAL
            SET raw_mat_name = %s,
                raw_mat_quantity = %s
            WHERE raw_mat_id = %s
        """, (raw_mat_name, raw_mat_quantity, raw_mat_id))

        conn.commit()

    finally:
        cursor.close()
        conn.close()

    return RedirectResponse(url="/dashboard", status_code=302)





@router.post("/dashboard/materials/delete")
async def delete_material(raw_mat_id: int = Form()):
    conn = get_db_conn()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "DELETE FROM RAW_MATERIAL WHERE raw_mat_id = %s",
            (raw_mat_id,)
        )

        conn.commit()

    except mysql.connector.IntegrityError:
        conn.rollback()
        raise HTTPException(
            status_code=400,
            detail="Cannot delete raw material: it is referenced in the bill of materials."
        )

    finally:
        cursor.close()
        conn.close()

    return RedirectResponse(url="/dashboard", status_code=302)