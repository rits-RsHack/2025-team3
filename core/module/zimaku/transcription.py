import json
from pathlib import Path

from helper.gemini import GeminiProcessor


class Transcriber:
    def __init__(self, gemini_model_name: str = "gemini-2.5-flash"):
        try:
            self.gemini_processor = GeminiProcessor(model_name=gemini_model_name)
        except (ValueError, RuntimeError) as e:
            print(f"致命的なエラー: Transcriberの初期化に失敗しました。 - {e}")
            raise

    def transcribe_audio_with_timestamps(self, audio_file_path: str) -> list:
        audio_path = Path(audio_file_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"音声ファイルが見つかりません: {audio_file_path}")

        prompt = """
        この音声ファイルを非常に正確に文字起こししてください。
        出力は、以下の形式のJSONリストだけにしてください。他のテキストは含めないでください。
        
        [
          {"start": "00:00:02.123", "end": "00:00:05.456", "text": "ここに最初の字幕の文が入ります。"},
          {"start": "00:00:06.789", "end": "00:00:09.999", "text": "そして、これが次の文です。"}
        ]

        タイムスタンプのフォーマットは「HH:MM:SS.ms」を厳守してください。
        各文は、意味の区切りが良い短いフレーズにしてください。
        """

        print(
            f"Geminiにタイムスタンプ付き文字起こしをリクエストしています... ファイル: {audio_file_path}"
        )

        try:
            response_text = self.gemini_processor.generate_response(
                user_prompt=prompt, file_path=str(audio_path)
            )

            cleaned_text = (
                response_text.strip().replace("```json", "").replace("```", "").strip()
            )

            transcribed_data = json.loads(cleaned_text)
            print("タイムスタンプ付き文字起こしが完了しました。")
            return transcribed_data

        except json.JSONDecodeError as e:
            print(f"JSONの解析に失敗しました。Geminiの出力: {response_text}")
            raise RuntimeError(f"Geminiからの応答形式が不正です: {e}")
        except Exception as e:
            raise RuntimeError(
                f"Geminiによるタイムスタンプ付き文字起こし中にエラーが発生しました: {e}"
            )
