import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from module.element_divide import router as element_divide_router

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

app = FastAPI()

origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(element_divide_router, prefix="/api", tags=["Audio Separation"])


# --- ルートパスの簡単な動作確認用エンドポイント (任意) ---
@app.get("/")
def read_root():
    return {"message": "Audily Core API is running."}
