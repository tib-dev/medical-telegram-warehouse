from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..dependencies import get_db
from ..schemas import MessageSearchResult

router = APIRouter(prefix="/api/search", tags=["Search"])


@router.get("/messages", response_model=list[MessageSearchResult])
def search_messages(query: str, limit: int = 20, db: Session = Depends(get_db)):
    sql = text("""
        SELECT
            message_id,
            channel_name,
            message_text,
            view_count,
            message_date::text
        FROM marts.fct_messages
        WHERE message_text ILIKE :q
        ORDER BY view_count DESC
        LIMIT :limit
    """)

    result = db.execute(
        sql, {"q": f"%{query}%", "limit": limit}
    )

    return result.mappings().all()
