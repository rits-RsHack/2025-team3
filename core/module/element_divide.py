import os
import shutil # クリーンアップでディレクトリごと消すために追加
from pathlib import Path

# BackgroundTasks をインポート
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse

# (他のimport文は変更なし)
from process_music import Music
from save_upload import save_upload_file
from download_processed import create_download_response

# (app = FastAPI() やディレクトリ定義も変更なし)
app = FastAPI()
UPLOAD_DIR = Path("./temp_uploads")
OUTPUT_DIR = Path("./output-python")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
music_processor = Music(stems="spleeter:5stems")

# --------------------------------------------------------------------------
# バックグラウンドで実行する重い処理を、別の関数に切り出す 
# --------------------------------------------------------------------------
def run_spleeter_separation(temp_filepath: Path, output_dir: Path):
    """Spleeterの実行と後片付けを行う関数"""
    try:
        print(f"バックグラウンド処理を開始: {temp_filepath}")
        # Spleeterで音楽を分離する
        music_processor.divide(
            input_file_path=str(temp_filepath),
            output_base_dir=str(output_dir)
        )
        print(f"バックグラウンド処理が正常に完了: {music_processor.output_directory}")
    except Exception as e:
        print(f"バックグラウンド処理中にエラーが発生しました: {e}")
        # エラーが起きた場合、中途半端な出力ディレクトリが残っていれば削除する
        if music_processor.output_directory and music_processor.output_directory.exists():
            shutil.rmtree(music_processor.output_directory)
    finally:
        # 成功・失敗にかかわらず、一時的にアップロードしたファイルを削除する
        if temp_filepath.exists():
            temp_filepath.unlink()
            print(f"一時ファイルが削除されました: {temp_filepath}")

# --------------------------------------------------------------------------
# APIエンドポイントの定義
# --------------------------------------------------------------------------

@app.post("/api/upload")
async def upload_and_start_separation(
    background_tasks: BackgroundTasks, # BackgroundTasks を引数で受け取る
    file: UploadFile = File(...)
):
    """
    音声ファイルをアップロードし、バックグラウンドで分離処理を開始する。
    処理を待たずに、すぐに処理ID（ディレクトリ名）を返す。
    """
    try:
        # 1. ヘルパーを使ってアップロードされたファイルを安全に保存する
        # このファイルパスはバックグラウンドタスクに渡される
        saved_filepath = await save_upload_file(file, UPLOAD_DIR)
        
        # 2. フロントエンドが後で問い合わせるための一意なID（ディレクトリ名）を決定する
        # save_upload_file が作るユニークなファイル名から拡張子を除いたものをIDとする
        output_directory_name = saved_filepath.stem
        
        # 3.  重い処理をバックグラウンドタスクとして登録 
        background_tasks.add_task(
            run_spleeter_separation, # 実行する関数
            saved_filepath,          # その関数に渡す引数1
            OUTPUT_DIR               # その関数に渡す引数2
        )

        # 4. 処理の完了を待たずに、すぐにレスポンスを返す！ 
        print(f"リクエストを受け付けました。処理ID: {output_directory_name}")
        return {
            "message": "ファイルのアップロードを受け付け、分離処理を開始しました。",
            "processing_id": output_directory_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ファイルのアップロード処理中にエラーが発生しました: {str(e)}")


# (status と download のエンドポイントは変更なしでOK)
@app.get("/api/status/{dir_name}")
async def get_separation_status(dir_name: str):
    # (この関数は変更なし)
    if ".." in dir_name or "/" in dir_name:
        raise HTTPException(status_code=400, detail="無効なディレクトリ名です。")
    target_dir = OUTPUT_DIR / dir_name
    if target_dir.exists() and target_dir.is_dir():
        expected_files = ["vocals.wav", "drums.wav", "bass.wav", "other.wav", "piano.wav"]
        if all((target_dir / f).exists() for f in expected_files):
            return {"status": "complete"}
        else:
            return {"status": "processing"}
    else:
        return {"status": "processing"}

@app.get("/api/download/{dir_name}/{filename}")
async def download_separated_file(dir_name: str, filename: str) -> FileResponse:
    # (この関数は変更なし)
    return create_download_response(
        base_dir=OUTPUT_DIR, dir_name=dir_name, filename=filename
    )