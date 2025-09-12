from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# --- 各モジュールからルーターをインポート ---
# 既存のelement_divideルーター
from module.element_divide import router as element_divide_router
from module.recommend import router as analyze_music_router

app = FastAPI(
    title="Audily Core API",
    description="音楽処理と分析のためのバックエンドAPI",
    version="1.0.0",
)

origins = [
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    element_divide_router,
    prefix="/api",  # URLの接頭辞
    tags=["Audio Separation (Sync)"],  # ドキュメント用のタグ
)
app.include_router(
    analyze_music_router,
    prefix="/api",  # こちらも同じ接頭辞
    tags=["Music Analysis (Async)"],  # ドキュメント用のタグ
)


# --- 3. ルートパスの動作確認用エンドポイント ---
@app.get("/")
def read_root():
    return {"message": "Welcome to Audily Core API"}
