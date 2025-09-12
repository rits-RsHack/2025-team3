import multiprocessing
import subprocess
import sys
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from helper.audio_extractor import AudioExtractor
from helper.db_handler import log_operation
from helper.save_upload import save_upload_file
from helper.subtitle_generator import SubtitleGenerator

from .transcription import Transcriber

router = APIRouter()

UPLOAD_DIR = Path("./temp_uploads_subtitle")
PROCESSING_DIR = Path("./processing_subtitle")
RESULT_DIR = Path("./result_subtitle")
FONT_FILE_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "fonts/NotoSansJP-VariableFont_wght.ttf"
)


@router.on_event("startup")
async def startup_event():
    UPLOAD_DIR.mkdir(exist_ok=True)
    PROCESSING_DIR.mkdir(exist_ok=True)
    RESULT_DIR.mkdir(exist_ok=True)
    print("字幕生成機能用のディレクトリ準備が完了しました。")


def subtitle_worker(
    input_video_path: Path, job_id: str, user_id: str, original_filename: str
):
    job_dir = PROCESSING_DIR / job_id
    job_dir.mkdir(exist_ok=True)

    final_video_path = RESULT_DIR / f"{job_id}.mp4"
    status_file = job_dir / "status.txt"

    def update_status(message: str):
        print(f"[{job_id}] {message}")
        with open(status_file, "w", encoding="utf-8") as f:
            f.write(f"processing: {message}")

    try:
        abs_input_video_path = input_video_path.resolve()
        abs_job_dir = job_dir.resolve()
        abs_audio_path = abs_job_dir / "extracted_audio.wav"
        abs_srt_path = abs_job_dir / "subtitle.srt"
        abs_final_video_path = final_video_path.resolve()
        abs_font_file_path = FONT_FILE_PATH.resolve()

        update_status("音声の抽出を開始しています...")
        AudioExtractor.extract_audio(abs_input_video_path, abs_audio_path)

        update_status("タイムスタンプ付き文字起こしを開始しています (Gemini API)...")
        transcriber = Transcriber()
        timestamped_data = transcriber.transcribe_audio_with_timestamps(
            str(abs_audio_path)
        )

        update_status("字幕ファイル (SRT形式) を生成を開始しています...")
        SubtitleGenerator.create_srt_from_timestamped_data(
            timestamped_data, abs_srt_path
        )

        update_status("動画に字幕を焼き付けています (FFmpeg)...")

        if not abs_font_file_path.exists():
            raise FileNotFoundError(
                f"フォントファイルが見つかりません: {abs_font_file_path}"
            )

        video_filter_value = f"subtitles='{abs_srt_path.as_posix()}':force_style='FontFile={abs_font_file_path.as_posix()}'"
        command = [
            "ffmpeg",
            "-i",
            str(abs_input_video_path),
            "-vf",
            video_filter_value,
            "-c:a",
            "copy",
            str(abs_final_video_path),
        ]
        print(f"実行するFFmpegコマンド: {' '.join(command)}")

        try:
            result = subprocess.run(
                command, check=True, capture_output=True, text=True, encoding="utf-8"
            )
            print("FFmpeg output:", result.stdout)
        except subprocess.CalledProcessError as e:
            error_detail = f"コマンド: {' '.join(e.cmd)}\n終了コード: {e.returncode}\nエラー出力:\n{e.stderr}"
            raise RuntimeError(f"FFmpeg処理中にエラーが発生しました。\n{error_detail}")

        with open(status_file, "w", encoding="utf-8") as f:
            f.write("complete")
        print(f"[{job_id}] 全ての処理が正常に完了しました。")

        log_operation(user_id, "add_subtitle", original_filename, "completed")

    except Exception as e:
        error_message = f"エラーが発生しました: {str(e)}"
        print(f"[{job_id}] {error_message}")
        with open(status_file, "w", encoding="utf-8") as f:
            f.write(f"error: {error_message}")
        log_operation(
            user_id,
            "add_subtitle",
            original_filename,
            f"failed: {e.__class__.__name__}",
        )


@router.post("/add-subtitle")
async def start_subtitle_process(
    file: UploadFile = File(...), user_id: str = Form(...)
):
    saved_filepath = await save_upload_file(file, UPLOAD_DIR)
    job_id = saved_filepath.stem

    log_operation(user_id, "add_subtitle", file.filename, "started")

    process = multiprocessing.Process(
        target=subtitle_worker,
        args=(saved_filepath, job_id, user_id, file.filename),
    )
    process.start()

    return {"message": "字幕生成リクエストを受け付けました。", "job_id": job_id}


@router.get("/subtitle-status/{job_id}")
async def get_subtitle_status(job_id: str):
    if ".." in job_id or "/" in job_id:
        raise HTTPException(status_code=400, detail="無効なJob IDです。")

    status_file = PROCESSING_DIR / job_id / "status.txt"
    if not status_file.exists():
        return {"status": "processing", "detail": "処理を開始しています..."}

    with open(status_file, "r", encoding="utf-8") as f:
        status_text = f.read().strip()

    status, *detail_parts = status_text.split(": ", 1)
    detail = detail_parts[0] if detail_parts else ""

    return {"status": status, "detail": detail}


def cleanup_files(files_to_delete: list[Path]):
    for file_path in files_to_delete:
        if file_path.exists():
            try:
                file_path.unlink()
                print(f"クリーンアップ: {file_path} を削除しました。")
            except OSError as e:
                print(f"クリーンアップエラー: {file_path} の削除に失敗しました - {e}")


@router.get("/download-subtitled-video/{job_id}")
async def download_subtitled_video(job_id: str):
    if ".." in job_id or "/" in job_id:
        raise HTTPException(status_code=400, detail="無効なJob IDです。")

    result_file = RESULT_DIR / f"{job_id}.mp4"
    original_file = UPLOAD_DIR / f"{job_id}.mp4"

    if not result_file.exists():
        raise HTTPException(
            status_code=404, detail="結果ファイルが見つからないか、まだ処理中です。"
        )

    files_for_cleanup = [result_file, original_file]

    return FileResponse(
        result_file,
        media_type="video/mp4",
        filename=f"subtitled_{job_id}.mp4",
        background=BackgroundTask(cleanup_files, files_to_delete=files_for_cleanup),
    )
