import os
import uuid
from pathlib import Path

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
from spleeter.separator import Separator


class Music:
    def __init__(self, stems: str = "spleeter:5stems") -> None:
        self.separator = Separator(stems)
        print("初期化が完了しました。")

        self.vocals = None
        self.piano = None
        self.drums = None
        self.bass = None
        self.other = None

        self.output_directory = None

    def divide(
        self, input_file_path: str, output_base_dir: str = "./output-python"
    ) -> None:
        input_path = Path(input_file_path)
        if not input_path.exists():
            raise FileNotFoundError(f"入力ファイルが見つかりません: {input_file_path}")

        unique_id = uuid.uuid4()
        output_subdir_name = f"{input_path.stem}_{unique_id}"

        self.output_directory = Path(output_base_dir) / output_subdir_name

        Path(output_base_dir).mkdir(exist_ok=True)

        print(f"ファイルを分離しています... 出力先: {self.output_directory}")

        self.separator.separate_to_file(
            str(input_path),
            output_base_dir,
            filename_format=output_subdir_name + "/{instrument}.{codec}",
        )

        print("分離が完了しました。")

        result_dir = Path(output_base_dir) / output_subdir_name

        self.vocals = result_dir / "vocals.wav"
        self.piano = result_dir / "piano.wav"
        self.drums = result_dir / "drums.wav"
        self.bass = result_dir / "bass.wav"
        self.other = result_dir / "other.wav"

        for part_name, path in self.get_divided_paths().items():
            if not path.exists():
                print(f"警告: {part_name} のファイルが見つかりませんでした: {path}")

    def get_divided_paths(self) -> dict:
        return {
            "vocals": self.vocals,
            "piano": self.piano,
            "drums": self.drums,
            "bass": self.bass,
            "other": self.other,
        }


if __name__ == "__main__":
    music_processor = Music(stems="spleeter:5stems")

    input_audio = "lemon.mp4"

    try:
        music_processor.divide(input_audio)

        print(f"出力ディレクトリ: {music_processor.output_directory}")

        divided_files = music_processor.get_divided_paths()
        for part, file_path in divided_files.items():
            print(f"{part.capitalize():<10}: {file_path}")

    except FileNotFoundError as e:
        print(f"エラー: {e}")
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}")
