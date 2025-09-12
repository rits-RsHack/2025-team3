import io
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

sys.path.append(str(Path(__file__).resolve().parent.parent))
from helper.db_handler import log_operation
from helper.process_music import Music

router = APIRouter()

SPLEETER_TEMP_DIR = Path("./spleeter_temp_processing")
RESULT_ZIPS_DIR = Path("./result_zips")
SPLEETER_TEMP_DIR.mkdir(exist_ok=True)
RESULT_ZIPS_DIR.mkdir(exist_ok=True)


try:
    music_processor = Music(stems="spleeter:5stems")
except Exception as e:
    print(f"致命的なエラー: Spleeterモデルの初期化に失敗しました。 {e}")
    music_processor = None


def cleanup_file(file_path: Path):
    """バックグラウンドでファイルを削除する"""
    if file_path.exists():
        file_path.unlink()
        print(f"クリーンアップ: {file_path} を削除しました。")


@router.post("/element_divide")
async def separate_and_get_download_url(
    file: UploadFile = File(...), user_id: str = Form(...)
):
    if not music_processor:
        raise HTTPException(
            status_code=503, detail="音楽分離サービスが利用できません。"
        )

    log_operation(
        user_id=user_id,
        operation_type="source_separation",
        source_filename=file.filename,
        status="started",
    )

    # 一時ディレクトリではなく、永続的なディレクトリにSpleeterの出力を保存
    job_id = f"{user_id}_{Path(file.filename).stem}_{Path(tempfile.mktemp()).name}"
    processing_dir = SPLEETER_TEMP_DIR / job_id
    processing_dir.mkdir()

    input_filepath = processing_dir / file.filename

    try:
        with open(input_filepath, "wb") as buffer:
            buffer.write(await file.read())

        await file.close()

        print(f"分離処理を開始: {input_filepath}")
        music_processor.divide(
            input_file_path=str(input_filepath), output_base_dir=str(processing_dir)
        )

        output_subdir = music_processor.output_directory
        if not output_subdir or not output_subdir.exists():
            raise HTTPException(
                status_code=404, detail="分離されたファイルが見つかりません。"
            )
        print(f"分離処理が完了。出力先: {output_subdir}")

        original_stem = Path(file.filename).stem
        zip_filename = f"{original_stem}_separated.zip"
        zip_filepath = RESULT_ZIPS_DIR / zip_filename

        with zipfile.ZipFile(zip_filepath, "w", zipfile.ZIP_DEFLATED) as zip_f:
            for separated_file in output_subdir.glob("*.wav"):
                zip_f.write(separated_file, arcname=separated_file.name)

        print(f"ZIPファイルを生成しました: {zip_filepath}")

        log_operation(
            user_id=user_id,
            operation_type="source_separation",
            source_filename=file.filename,
            status="completed",
        )

        return {"message": "Processing complete!", "download_filename": zip_filename}

    except Exception as e:
        log_operation(
            user_id=user_id,
            operation_type="source_separation",
            source_filename=file.filename,
            status=f"failed: {e.__class__.__name__}",
        )
        if isinstance(e, HTTPException):
            raise e
        else:
            raise HTTPException(
                status_code=500, detail=f"処理中に予期せぬエラーが発生しました: {e}"
            )
    finally:
        if processing_dir.exists():
            shutil.rmtree(processing_dir)


@router.get("/download-zip/{filename}")
async def download_separated_zip(filename: str):
    """生成されたZIPファイルをダウンロードさせるエンドポイント"""
    if ".." in filename or "/" in filename:
        raise HTTPException(status_code=400, detail="無効なファイル名です。")

    file_path = RESULT_ZIPS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="ファイルが見つかりません。")

    # ダウンロード後にファイルを削除するタスクを登録
    return FileResponse(
        file_path,
        media_type="application/zip",
        filename=filename,
        background=BackgroundTask(cleanup_file, file_path=file_path),
    )
