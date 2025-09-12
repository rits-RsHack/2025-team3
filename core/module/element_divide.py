import io
# Musicクラスのインポートパスを修正 (moduleディレクトリから見てhelperは一つ上の階層にある)
import sys
import tempfile
import zipfile
from pathlib import Path

# FastAPIからAPIRouterをインポートする
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

sys.path.append(str(Path(__file__).resolve().parent.parent))
from helper.process_music import Music

# APIRouterのインスタンスを作成
# これがこのモジュール専用のミニFastAPIアプリのようになる
router = APIRouter()

# --- モデルの初期化 ---
# 注意: モデルの初期化はメインアプリで行うのが望ましいが、
# ここでMusicクラスを使うために一時的に初期化する。
# より良い設計は、main.pyで初期化したインスタンスを依存性注入で渡すこと。
try:
    music_processor = Music(stems="spleeter:5stems")
except Exception as e:
    # 実際のエラーハンドリングはmain.pyに任せるのが良い
    print(f"警告: element_divide.pyでSpleeterモデルの再初期化を試みました。 {e}")
    music_processor = None


# @app.postではなく、@router.post を使う
@router.post("/element_divide")
async def separate_and_download(file: UploadFile = File(...)):
    if not music_processor:
        raise HTTPException(
            status_code=503, detail="音楽分離サービスが利用できません。"
        )

    """
    音声ファイルをアップロードし、分離処理を行い、結果をZIPでダウンロードさせる。
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        input_filepath = temp_dir_path / file.filename
        try:
            with open(input_filepath, "wb") as buffer:
                buffer.write(await file.read())
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"一時ファイルの保存に失敗しました: {e}"
            )
        finally:
            await file.close()

        print(f"分離処理を開始: {input_filepath}")
        try:
            music_processor.divide(
                input_file_path=str(input_filepath), output_base_dir=str(temp_dir_path)
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"音楽の分離処理中にエラーが発生しました: {e}"
            )

        output_subdir = music_processor.output_directory
        if not output_subdir or not output_subdir.exists():
            raise HTTPException(
                status_code=404, detail="分離されたファイルが見つかりません。"
            )
        print(f"分離処理が完了。出力先: {output_subdir}")

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_f:
            for separated_file in output_subdir.glob("*.wav"):
                zip_f.write(separated_file, arcname=separated_file.name)

        zip_buffer.seek(0)

        original_stem = Path(file.filename).stem
        zip_filename = f"{original_stem}_separated.zip"
        print(f"ZIPファイルを生成し、ダウンロードを開始します: {zip_filename}")

        return StreamingResponse(
            content=zip_buffer,
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={zip_filename}"},
        )
