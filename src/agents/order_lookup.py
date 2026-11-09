from __future__ import annotations

import re
import sqlite3

from src.common.paths import DATABASE_PATH

ORDER_ID_PATTERN = re.compile(r"^ORD-\d{6}$", re.IGNORECASE)


def lookup_order(order_id: str, db_path=None) -> dict:
    db_path = db_path or DATABASE_PATH
    oid = str(order_id).strip().upper()
    if not ORDER_ID_PATTERN.match(oid):
        return {"found": False, "error": "invalid_order_id_format"}
    if not db_path.exists():
        return {"found": False, "error": "database_not_initialized"}
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.execute(
            """
            SELECT o.order_id, o.customer_id, o.order_ts, o.status, o.order_amount, o.delivery_minutes
            FROM orders o
            WHERE o.order_id = ?
            """,
            (oid,),
        )
        row = cur.fetchone()
        if not row:
            return {"found": False, "error": "order_not_found"}
        return {
            "found": True,
            "order_id": row[0],
            "customer_id": row[1],
            "order_date": row[2],
            "order_status": row[3],
            "order_amount": row[4],
            "delivery_minutes": row[5],
        }
    finally:
        conn.close()
