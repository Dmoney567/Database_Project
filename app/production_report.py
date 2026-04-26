from fastapi import APIRouter, Form
from fastapi.responses import RedirectResponse

from app.database_Connection import get_db_conn  

router = APIRouter()


@router.post("/dashboard/reports/create")
async def create_report(
    report_date: str = Form(),
    part_id: int = Form(),
    num_parts_finished: int = Form(),
    production_status: int = Form(),
    estimated_completion_date: str = Form(None),
    stage_id: int = Form(None)
):
    conn = get_db_conn()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO PRODUCTION_REPORT
            (report_date, part_id, num_parts_finished, production_status, estimated_completion_date, stage_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            report_date,
            part_id,
            num_parts_finished,
            production_status,
            estimated_completion_date if estimated_completion_date else None,
            stage_id
        ))

        conn.commit()

    finally:
        cursor.close()
        conn.close()

    return RedirectResponse(url="/dashboard", status_code=302)



@router.post("/dashboard/reports/update")
async def update_report(
    report_id: int = Form(),
    report_date: str = Form(),
    part_id: int = Form(),
    num_parts_finished: int = Form(),
    production_status: int = Form(),
    estimated_completion_date: str = Form(None),
    stage_id: int = Form(None)
):
    conn = get_db_conn()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE PRODUCTION_REPORT
            SET report_date = %s,
                part_id = %s,
                num_parts_finished = %s,
                production_status = %s,
                estimated_completion_date = %s,
                stage_id = %s
            WHERE report_id = %s
        """, (
            report_date,
            part_id,
            num_parts_finished,
            production_status,
            estimated_completion_date if estimated_completion_date else None,
            stage_id,
            report_id
        ))

        conn.commit()

    finally:
        cursor.close()
        conn.close()

    return RedirectResponse(url="/dashboard", status_code=302)



@router.post("/dashboard/reports/delete")
async def delete_report(report_id: int = Form()):
    conn = get_db_conn()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "DELETE FROM PRODUCTION_REPORT WHERE report_id = %s",
            (report_id,)
        )
        conn.commit()

    finally:
        cursor.close()
        conn.close()

    return RedirectResponse(url="/dashboard", status_code=302)