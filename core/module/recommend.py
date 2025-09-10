import os
import shutil
import uuid
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Form

# --------------------------------------------------------------------------
# ヘルパーファイルから必要なクラスと関数をインポート
# --------------------------------------------------------------------------
from save_upload import save_upload_file
from process_music import Music
from gemini import GeminiProcessor

# --------------------------------------------------------------------------
# FastAPIアプリケーションの初期設定
# --------------------------------------------------------------------------
app = FastAPI()

# ディレクトリの定義と作成
UPLOAD_DIR = Path("./temp_uploads")
SPLEETER_OUTPUT_DIR = Path("./spleeter_output")
ANALYSIS_RESULTS_DIR = Path("./analysis_results")
UPLOAD_DIR.mkdir(exist_ok=True)
SPLEETER_OUTPUT_DIR.mkdir(exist_ok=True)
ANALYSIS_RESULTS_DIR.mkdir(exist_ok=True)

# --------------------------------------------------------------------------
# モデルの初期化（サーバー起動時に一度だけ実行）
# --------------------------------------------------------------------------
try:
    print("Spleeterモデルを初期化しています...")
    music_processor = Music(stems="spleeter:5stems")
    print("Geminiモデルを初期化しています...")
    gemini_processor = GeminiProcessor(model_name="gemini-1.5-pro-latest")
except Exception as e:
    print(f"致命的なエラー: モデルの初期化に失敗しました。 {e}")
    # .envファイルに GOOGLE_API_KEY が設定されているか確認してください
    exit(1)

# --------------------------------------------------------------------------
# バックグラウンドで実行する重い処理を関数に切り出す
# --------------------------------------------------------------------------
def run_analysis_task(temp_filepath: Path, job_id: str, user_prompt: str):
    """
    【バックグラウンド処理の本体】
    1. Spleeterでボーカルを分離
    2. Geminiでボーカルを分析
    3. 結果をテキストファイルに保存
    4. 後片付け
    """
    analysis_result_path = ANALYSIS_RESULTS_DIR / f"{job_id}.txt"
    spleeter_job_output_dir = None

    try:
        # --- ステップ1: Spleeterでボーカルを分離 ---
        print(f"[{job_id}] Spleeterによるボーカル分離を開始...")
        music_processor.divide(
            input_file_path=str(temp_filepath),
            output_base_dir=str(SPLEETER_OUTPUT_DIR)
        )
        spleeter_job_output_dir = music_processor.output_directory
        vocals_path = spleeter_job_output_dir / "vocals.wav"

        if not vocals_path.exists():
            raise FileNotFoundError("ボーカルファイルの抽出に失敗しました。")
        print(f"[{job_id}] ボーカル分離が完了: {vocals_path}")

        # --- ステップ2: Geminiでボーカル音声ファイルを分析 ---
        print(f"[{job_id}] Geminiによる分析を開始...")
        # Geminiに渡すプロンプトを組み立てる（音声ファイルだけだと何をすべきか分からないため）
        final_prompt = f"以下の音声ファイルを分析し、ユーザーの要望に答えてください。\n\nユーザーの要望: '{user_prompt}'"
        
        analysis_text = gemini_processor.generate_response(
            user_prompt=final_prompt,
            file_path=str(vocals_path)
        )
        print(f"[{job_id}] Geminiによる分析が完了。")

        # --- ステップ3: 分析結果をファイルに保存 ---
        with open(analysis_result_path, "w", encoding="utf-8") as f:
            f.write(analysis_text)
        print(f"[{job_id}] 分析結果を保存しました: {analysis_result_path}")

    except Exception as e:
        # エラーが発生した場合、エラーメッセージを結果ファイルに書き込む
        error_message = f"処理中にエラーが発生しました。\n詳細: {str(e)}"
        with open(analysis_result_path, "w", encoding="utf-8") as f:
            f.write(error_message)
        print(f"[{job_id}] エラーが発生したため、エラー内容をファイルに記録しました。")

    finally:
        # --- ステップ4: 後片付け ---
        # 一時的なアップロードファイルを削除
        if temp_filepath.exists():
            temp_filepath.unlink()
        # Spleeterが出力したディレクトリ（中のwavファイル含む）を丸ごと削除
        if spleeter_job_output_dir and spleeter_job_output_dir.exists():
            shutil.rmtree(spleeter_job_output_dir)
        print(f"[{job_id}] クリーンアップが完了しました。")

# --------------------------------------------------------------------------
# APIエンドポイントの定義
# --------------------------------------------------------------------------

@app.post("/api/analyze")
async def start_music_analysis(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    prompt: str = Form("この曲の歌詞、歌い方、雰囲気を総合的に分析してください。") # フォームでプロンプトも受け取る
):
    """
    【受付】楽曲ファイルとプロンプトを受け取り、バックグラウンドで分析処理を開始する。
    """
    try:
        saved_filepath = await save_upload_file(file, UPLOAD_DIR)
        job_id = saved_filepath.stem # ファイル名から生成したユニークなID
        
        background_tasks.add_task(
            run_analysis_task,
            saved_filepath,
            job_id,
            prompt
        )
        
        return {
            "message": "分析リクエストを受け付けました。処理には数分かかることがあります。",
            "job_id": job_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"リクエストの受付中にエラーが発生しました: {e}")


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