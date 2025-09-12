import os
import shutil
import uuid
from pathlib import Path
import multiprocessing # ★ multiprocessing をインポート

from fastapi import FastAPI, File, UploadFile, HTTPException, Form # BackgroundTasksは不要に

# (他のimport文は変更なし)
from helper.save_upload import save_upload_file
from helper.process_music import Music
from helper.gemini import GeminiProcessor

# (FastAPIアプリとディレクトリの定義は変更なし)
app = FastAPI()
UPLOAD_DIR = Path("./temp_uploads")
SPLEETER_OUTPUT_DIR = Path("./spleeter_output")
ANALYSIS_RESULTS_DIR = Path("./analysis_results")
UPLOAD_DIR.mkdir(exist_ok=True)
SPLEETER_OUTPUT_DIR.mkdir(exist_ok=True)
ANALYSIS_RESULTS_DIR.mkdir(exist_ok=True)

# --------------------------------------------------------------------------
# ★★★ 重い処理を行う関数を、プロセスの外に定義する ★★★
# この関数が、完全に独立した「調理専用の厨房」で実行される
# --------------------------------------------------------------------------
def analysis_process_worker(temp_filepath: Path, job_id: str, user_prompt: str):
    analysis_result_path = ANALYSIS_RESULTS_DIR / f"{job_id}.txt"
    spleeter_job_output_dir = None
    
    try:
        print(f"[{job_id}] 新規プロセスでモデルを初期化しています...")
        local_music_processor = Music(stems="spleeter:5stems")
        local_gemini_processor = GeminiProcessor(model_name="gemini-1.5-pro-latest")
        print(f"[{job_id}] モデルの初期化が完了。")

        print(f"[{job_id}] Spleeterによるボーカル分離を開始...")
        local_music_processor.divide(
            input_file_path=str(temp_filepath),
            output_base_dir=str(SPLEETER_OUTPUT_DIR)
        )
        spleeter_job_output_dir = local_music_processor.output_directory
        vocals_path = spleeter_job_output_dir / "vocals.wav"
        
        ### ログ追加 ###
        print(f"[{job_id}] Spleeter処理が完了。ボーカルファイルパス: {vocals_path}")

        if not vocals_path.exists():
            raise FileNotFoundError("ボーカルファイルの抽出に失敗しました。")

        print(f"[{job_id}] Geminiによる分析を開始...")
        final_prompt = f"以下の音声ファイルを分析し、ユーザーの要望に答えてください。\n\nユーザーの要望: '{user_prompt}'"
        
        ### ログ追加 ###
        print(f"[{job_id}] Geminiにファイルをアップロードしています...")

        analysis_text = local_gemini_processor.generate_response(
            user_prompt=final_prompt, file_path=str(vocals_path)
        )

        ### ログ追加 ###
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

# --------------------------------------------------------------------------
# APIエンドポイント (メインの厨房)
# モデルの初期化はここからは削除する
# --------------------------------------------------------------------------

@app.post("/api/analyze")
async def start_music_analysis(
    file: UploadFile = File(...),
    prompt: str = Form("この曲の歌詞、歌い方、雰囲気を総合的に分析してください。")
):
    """【受付】リクエストを受け付け、別のプロセスで重い処理を開始する"""
    try:
        saved_filepath = await save_upload_file(file, UPLOAD_DIR)
        job_id = saved_filepath.stem
        
        # ★★★ 新しいプロセスを作成し、バックグラウンドで実行を開始 ★★★
        process = multiprocessing.Process(
            target=analysis_process_worker, # 実行する関数
            args=(saved_filepath, job_id, prompt) # その関数に渡す引数
        )
        process.start() # プロセスを開始 (非同期で、すぐに次の行に進む)

        return {
            "message": "分析リクエストを受け付けました。処理には数分かかることがあります。",
            "job_id": job_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"リクエストの受付中にエラーが発生しました: {e}")

# (status と result のエンドポイントは変更なしでOK)
# (前の /api/analyze エンドポイントのコードはそのまま)

# ...

@app.get("/api/analysis-status/{job_id}")
async def get_analysis_status(job_id: str):
    """
    【進捗確認】指定されたjob_idの分析が完了したか確認する。
    """
    if ".." in job_id or "/" in job_id:
        raise HTTPException(status_code=400, detail="無効なJob IDです。")
    
    result_file = ANALYSIS_RESULTS_DIR / f"{job_id}.txt"
    if result_file.exists():
        return {"status": "complete"}
    else:
        return {"status": "processing"}


@app.get("/api/analysis-result/{job_id}")
async def get_analysis_result(job_id: str):
    """
    【結果取得】完了した分析結果のテキストを返す。
    """
    if ".." in job_id or "/" in job_id:
        raise HTTPException(status_code=400, detail="無効なJob IDです。")

    result_file = ANALYSIS_RESULTS_DIR / f"{job_id}.txt"
    if not result_file.exists():
        raise HTTPException(status_code=404, detail="結果が見つかりません。処理中か、Job IDが間違っている可能性があります。")
    
    with open(result_file, "r", encoding="utf-8") as f:
        content = f.read()

    return {"job_id": job_id, "analysis": content}