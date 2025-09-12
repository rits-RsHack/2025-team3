import subprocess
import sys
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

sys.path.append(str(Path(__file__).resolve().parent.parent))
from helper.db_handler import log_operation

router = APIRouter()


def convert_mp4_to_mp3(input_path: Path, output_path: Path):
    command = ["ffmpeg", "-i", str(input_path), "-vn", "-q:a", "0", str(output_path)]
    print(f"FFmpegコマンドを実行: {' '.join(command)}")
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print("FFmpegの変換が正常に完了しました.")
    except FileNotFoundError:
        raise RuntimeError("FFmpegがインストールされていないか、PATHが通っていません.")
    except subprocess.CalledProcessError as e:
        print("FFmpeg Error:", e.stderr)
        raise RuntimeError(f"MP4からMP3への変換に失敗しました: {e.stderr}")


def cleanup_files_and_log(
    files_to_delete: list[Path], user_id: str, original_filename: str, status: str
):
    for file_path in files_to_delete:
        if file_path.exists():
            try:
                file_path.unlink()
                print(f"クリーンアップ: {file_path} を削除しました.")
            except OSError as e:
                print(f"クリーンアップエラー: {file_path} の削除に失敗しました - {e}")

    log_operation(
        user_id=user_id,
        operation_type="mp4_to_mp3",
        source_filename=original_filename,
        status=status,
    )


@router.post("/mp4-to-mp3")
async def handle_mp4_to_mp3_conversion(
    file: UploadFile = File(...),
    user_id: str = Form(...),
):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_input_file:
        try:
            content = await file.read()
            temp_input_file.write(content)
            temp_input_filepath = Path(temp_input_file.name)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"一時ファイルの保存に失敗: {e}"
            )
        finally:
            await file.close()

    log_operation(
        user_id=user_id,
        operation_type="mp4_to_mp3",
        source_filename=file.filename,
        status="started",
    )

    output_filename = f"{temp_input_filepath.stem}.mp3"
    output_filepath = temp_input_filepath.with_name(output_filename)

    try:
        convert_mp4_to_mp3(temp_input_filepath, output_filepath)

        files_for_cleanup = [temp_input_filepath, output_filepath]

        return FileResponse(
            path=output_filepath,
            media_type="audio/mpeg",
            filename=output_filename,
            background=BackgroundTask(
                cleanup_files_and_log,
                files_to_delete=files_for_cleanup,
                user_id=user_id,
                original_filename=file.filename,
                status="completed",
            ),
        )
    except RuntimeError as e:
        log_operation(
            user_id=user_id,
            operation_type="mp4_to_mp3",
            source_filename=file.filename,
            status=f"failed: {e}",
        )
        if temp_input_filepath.exists():
            temp_input_filepath.unlink()
        raise HTTPException(status_code=500, detail=str(e))
