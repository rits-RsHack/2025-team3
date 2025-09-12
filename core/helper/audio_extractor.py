import subprocess
from pathlib import Path


class AudioExtractor:

    @staticmethod
    def extract_audio(input_path: Path, output_path: Path):

        command = [
            "ffmpeg",
            "-i",
            str(input_path),
            "-vn",
            "-acodec",
            "pcm_s16le",
            "-ar",
            "16000",
            "-ac",
            "1",
            str(output_path),
        ]
        print(f"FFmpegで音声を抽出しています: {' '.join(command)}")
        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
            print("音声の抽出が完了しました。")
        except FileNotFoundError:
            raise RuntimeError(
                "FFmpegがインストールされていないか、PATHが通っていません。"
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"音声の抽出に失敗しました: {e.stderr}")
