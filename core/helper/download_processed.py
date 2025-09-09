from pathlib import Path

from fastapi import HTTPException
from fastapi.responses import FileResponse


def create_download_response(
    base_dir: Path, dir_name: str, filename: str
) -> FileResponse:
    """パスを検証し、ダウンロード用のFileResponseオブジェクトを作成する"""

    # セキュリティチェック
    if ".." in dir_name or ".." in filename:
        raise HTTPException(status_code=400, detail="無効なファイルパスです。")

    file_path = base_dir / dir_name / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="ファイルが見つかりません。")

    # FileResponseを生成して返す
    return FileResponse(
        path=file_path, media_type="application/octet-stream", filename=filename
    )
