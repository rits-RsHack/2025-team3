import shutil
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile


async def save_upload_file(file: UploadFile, destination_dir: Path) -> Path:
    unique_id = str(uuid.uuid4())
    unique_stem = f"{unique_id}_{Path(file.filename).stem}"
    file_extension = Path(file.filename).suffix

    saved_filepath = destination_dir / f"{unique_stem}{file_extension}"

    try:
        with open(saved_filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return saved_filepath
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"ファイルの保存に失敗しました: {e}"
        )
    finally:
        file.file.close()
