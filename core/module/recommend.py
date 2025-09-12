import multiprocessing
import os
import shutil
# helperパッケージ内のモジュールをインポート
# (インポートパスを解決するためにsys.pathを追加)
import sys
from pathlib import Path

# FastAPIからAPIRouterをインポート
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

sys.path.append(str(Path(__file__).resolve().parent.parent))
from helper.gemini import GeminiProcessor
from helper.process_music import Music
from helper.save_upload import save_upload_file

# --- APIRouterのインスタンスを作成 ---
# これがこのモジュール専用のルーターになる
router = APIRouter()

# --- 定数とディレクトリ設定 ---
# このモジュール内で完結させる
UPLOAD_DIR = Path("./temp_uploads")
SPLEETER_OUTPUT_DIR = Path("./spleeter_output")
ANALYSIS_RESULTS_DIR = Path("./analysis_results")


# 起動時に一度だけディレクトリをチェック・作成
# (メインアプリ起動時に実行される)
@router.on_event("startup")
async def startup_event():
    UPLOAD_DIR.mkdir(exist_ok=True)
    SPLEETER_OUTPUT_DIR.mkdir(exist_ok=True)
    ANALYSIS_RESULTS_DIR.mkdir(exist_ok=True)
    print("分析用ディレクトリの準備が完了しました。")


# --- バックグラウンドプロセスで実行されるワーカー関数 ---
# (この関数の内容は変更なし)
def analysis_process_worker(temp_filepath: Path, job_id: str, user_prompt: str):
    analysis_result_path = ANALYSIS_RESULTS_DIR / f"{job_id}.txt"
    spleeter_job_output_dir = None
    try:
        print(f"[{job_id}] 新規プロセスでモデルを初期化しています...")
        local_music_processor = Music(stems="spleeter:5stems")
        local_gemini_processor = GeminiProcessor(model_name="gemini-2.5-pro")
        print(f"[{job_id}] モデルの初期化が完了。")

        print(f"[{job_id}] Spleeterによるボーカル分離を開始...")
        local_music_processor.divide(
            input_file_path=str(temp_filepath), output_base_dir=str(SPLEETER_OUTPUT_DIR)
        )
        spleeter_job_output_dir = local_music_processor.output_directory
        vocals_path = spleeter_job_output_dir / "vocals.wav"
        print(f"[{job_id}] Spleeter処理が完了。ボーカルファイルパス: {vocals_path}")

        if not vocals_path.exists():
            raise FileNotFoundError("ボーカルファイルの抽出に失敗しました。")

        print(f"[{job_id}] Geminiによる分析を開始...")
        final_prompt = f"以下の音声ファイルを分析し、ユーザーの要望に答えてください。\n\nユーザーの要望: '{user_prompt}'"
        print(f"[{job_id}] Geminiにファイルをアップロードしています...")
        analysis_text = local_gemini_processor.generate_response(
            user_prompt=final_prompt, file_path=str(vocals_path)
        )
        print(f"[{job_id}] Geminiの分析テキスト生成が完了。")

        with open(analysis_result_path, "w", encoding="utf-8") as f:
            f.write(analysis_text)
        print(f"[{job_id}] 分析結果を保存しました。")

    except Exception as e:
        error_message = f"処理中にエラーが発生しました。\n詳細: {str(e)}"
        with open(analysis_result_path, "w", encoding="utf-8") as f:
            f.write(error_message)
        print(f"[{job_id}] エラーが発生したため、エラー内容をファイルに記録しました。")
    finally:
        if temp_filepath.exists():
            temp_filepath.unlink()
        if spleeter_job_output_dir and spleeter_job_output_dir.exists():
            shutil.rmtree(spleeter_job_output_dir)
        print(f"[{job_id}] プロセスがクリーンアップを完了し、終了します。")


# --- APIエンドポイントの定義 (@app.post -> @router.post) ---


@router.post("/analyze")
async def start_music_analysis(
    file: UploadFile = File(...),
    prompt: str = Form("この曲の歌詞、歌い方、雰囲気を総合的に分析してください。"),
):
    """【受付】リクエストを受け付け、別のプロセスで重い処理を開始する"""
    # (この関数の内容は変更なし)
    try:
        saved_filepath = await save_upload_file(file, UPLOAD_DIR)
        job_id = saved_filepath.stem
        process = multiprocessing.Process(
            target=analysis_process_worker,
            args=(saved_filepath, job_id, prompt),
        )
        process.start()
        return {
            "message": "分析リクエストを受け付けました。処理には数分かかることがあります。",
            "job_id": job_id,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"リクエストの受付中にエラーが発生しました: {e}"
        )


@router.get("/analysis-status/{job_id}")
async def get_analysis_status(job_id: str):
    """【進捗確認】指定されたjob_idの分析が完了したか確認する。"""
    # (この関数の内容は変更なし)
    if ".." in job_id or "/" in job_id:
        raise HTTPException(status_code=400, detail="無効なJob IDです。")
    result_file = ANALYSIS_RESULTS_DIR / f"{job_id}.txt"
    if result_file.exists():
        return {"status": "complete"}
    else:
        return {"status": "processing"}


@router.get("/analysis-result/{job_id}")
async def get_analysis_result(job_id: str):
    """【結果取得】完了した分析結果のテキストを返す。"""
    # (この関数の内容は変更なし)
    if ".." in job_id or "/" in job_id:
        raise HTTPException(status_code=400, detail="無効なJob IDです。")
    result_file = ANALYSIS_RESULTS_DIR / f"{job_id}.txt"
    if not result_file.exists():
        raise HTTPException(status_code=404, detail="結果が見つかりません。")
    with open(result_file, "r", encoding="utf-8") as f:
        content = f.read()
    return {"job_id": job_id, "analysis": content}
