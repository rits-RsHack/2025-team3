import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException

sys.path.append(str(Path(__file__).resolve().parent.parent))

from helper.db_handler import get_history_by_user_id

router = APIRouter()


@router.get("/history/{user_id}")
async def get_user_history(user_id: str):
    if ".." in user_id or "/" in user_id:
        raise HTTPException(status_code=400, detail="無効なUser IDです。")

    try:
        history = get_history_by_user_id(user_id)
        return history
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"履歴の取得中にエラーが発生しました: {e}"
        )
