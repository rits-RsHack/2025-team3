import os
import time  # timeモジュールをインポート
from pathlib import Path
from typing import List, Optional, Union

import google.generativeai as genai
from dotenv import load_dotenv


class GeminiProcessor:

    def __init__(self, model_name: str = "gemini-1.5-pro-latest"):
        # ... (初期化のコードは変更なし)
        load_dotenv()
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GOOGLE_API_KEYが見つかりません。.envファイルを確認してください。"
            )
        genai.configure(api_key=self.api_key)
        self.model_name = model_name
        try:
            self.model = genai.GenerativeModel(self.model_name)
            print(f"Geminiモデル '{self.model_name}' の初期化に成功しました。")
        except Exception as e:
            raise RuntimeError(
                f"Geminiモデル '{self.model_name}' の初期化に失敗しました: {e}"
            )
        self.system_prompt = "You are a helpful assistant."

    def generate_response(
        self, user_prompt: str, file_path: Optional[str] = None
    ) -> str:
        if not user_prompt or not isinstance(user_prompt, str):
            raise TypeError("プロンプトは空でない文字列である必要があります。")

        uploaded_file = None
        if file_path:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(
                    f"指定されたファイルが見つかりません: {file_path}"
                )

            print(f"ファイルをアップロードしています: {file_path}...")
            try:
                # ★★★★★ ここからが修正箇所 ★★★★★
                # 1. ファイルをアップロード
                uploaded_file_response = genai.upload_file(path=file_path)
                print(f"アップロード開始。ファイルID: {uploaded_file_response.name}")

                # 2. ファイルの状態が 'ACTIVE' になるまで待機
                print("サーバー側でのファイル処理を待機しています...")
                while uploaded_file_response.state.name == "PROCESSING":
                    time.sleep(5)  # 5秒待機
                    uploaded_file_response = genai.get_file(
                        name=uploaded_file_response.name
                    )
                    print(f"  - 現在の状態: {uploaded_file_response.state.name}")

                if uploaded_file_response.state.name == "FAILED":
                    raise ValueError(
                        f"ファイルの処理に失敗しました: {uploaded_file_response.name}"
                    )

                print("ファイルの準備が完了しました (ACTIVE)。")
                uploaded_file = (
                    uploaded_file_response  # 準備完了したファイルオブジェクトを使用
                )
                # ★★★★★ ここまでが修正箇所 ★★★★★

            except Exception as e:
                raise RuntimeError(
                    f"ファイルのアップロードまたは処理中にエラーが発生しました: {e}"
                )

        try:
            if uploaded_file:
                contents: List[Union[str, object]] = [uploaded_file, user_prompt]
            else:
                contents: List[Union[str, object]] = [user_prompt]

            response = self.model.generate_content(contents)
            return response.text

        except Exception as e:
            print(f"Gemini API呼び出し中にエラーが発生しました: {e}")
            raise


if __name__ == "__main__":
    gemini = GeminiProcessor(model_name="gemini-2.5-pro")

    text_prompt = "オブジェクト指向プログラミングの主な利点を3つ教えてください。"
    print(f"\n--- テキストプロンプト ---")
    print(f"質問: {text_prompt}")
    text_response = gemini.generate_response(text_prompt)
    print("回答:")
    print(text_response)

    image_file = "lemon.mp4"
    image_prompt = "この音楽を説明してください"

    print(f"\n--- ファイル付きプロンプト ---")
    print(f"ファイル: {image_file}")
    print(f"質問: {image_prompt}")

    try:
        image_response = gemini.generate_response(
            user_prompt=image_prompt, file_path=image_file
        )
        print("回答:")
        print(image_response)
    except (FileNotFoundError, RuntimeError) as e:
        print(f"エラー: {e}")
