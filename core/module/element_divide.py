import os
import io
import zipfile
import tempfile
from pathlib import Path

# StreamingResponse と、新しく HTMLResponse をインポート
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse

# Spleeterのコアロジックをインポート
from process_music import Music

# --------------------------------------------------------------------------
# FastAPIアプリケーションの初期設定
# --------------------------------------------------------------------------
app = FastAPI()

# Spleeterモデルの読み込み
try:
    music_processor = Music(stems="spleeter:5stems")
except Exception as e:
    print(f"致命的なエラー: Spleeterモデルの初期化に失敗しました。 {e}")
    exit(1)

# --------------------------------------------------------------------------
# APIエンドポイントの定義
# --------------------------------------------------------------------------


@app.post("/api/element_divide")
async def separate_and_download(file: UploadFile = File(...)):
    """
    【同期的処理】
    音声ファイルをアップロードし、その場で分離処理を実行。
    結果をZIPファイルにまとめて、レスポンスとして直接ダウンロードさせる。
    """
    # (この関数の内容は変更ありません)
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        
        input_filepath = temp_dir_path / file.filename
        try:
            with open(input_filepath, "wb") as buffer:
                buffer.write(await file.read())
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"一時ファイルの保存に失敗しました: {e}")
        finally:
            await file.close()

        print(f"分離処理を開始: {input_filepath}")
        try:
            music_processor.divide(
                input_file_path=str(input_filepath), 
                output_base_dir=str(temp_dir_path)
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"音楽の分離処理中にエラーが発生しました: {e}")
        
        output_subdir = music_processor.output_directory
        if not output_subdir or not output_subdir.exists():
            raise HTTPException(status_code=404, detail="分離されたファイルが見つかりません。")
        print(f"分離処理が完了。出力先: {output_subdir}")

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_f:
            for separated_file in output_subdir.glob('*.wav'):
                zip_f.write(separated_file, separated_file.name)
        
        zip_buffer.seek(0)
        
        original_stem = Path(file.filename).stem
        zip_filename = f"{original_stem}_separated.zip"

        print(f"ZIPファイルを生成し、ダウンロードを開始します: {zip_filename}")

        return StreamingResponse(
            content=zip_buffer,
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={zip_filename}"}
        )