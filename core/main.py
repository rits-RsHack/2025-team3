from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from helper.db_handler import setup_database
from module.element_divide import router as element_divide_router
from module.history import router as history_router
from module.mp4tomp3 import router as mp4_to_mp3_router
from module.recommend import router as analyze_music_router
from module.zimaku.add_subtitle import router as add_subtitle_router

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
    element_divide_router, prefix="/api", tags=["Audio Separation (Sync)"]
)

app.include_router(analyze_music_router, prefix="/api", tags=["Music Analysis (Async)"])

app.include_router(add_subtitle_router, prefix="/api", tags=["Subtitles"])

app.include_router(mp4_to_mp3_router, prefix="/api", tags=["File Conversion"])

app.include_router(history_router, prefix="/api", tags=["History"])


@app.on_event("startup")
async def startup_event():
    setup_database()


@app.get("/")
def read_root():

    return {"message": "Welcome to Audily Core API"}
