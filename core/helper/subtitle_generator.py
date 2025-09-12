from pathlib import Path


class SubtitleGenerator:
    @staticmethod
    def create_srt_from_timestamped_data(data: list, output_path: Path):
        srt_content = ""
        for i, item in enumerate(data, 1):
            start_time = item["start"].replace(".", ",")
            end_time = item["end"].replace(".", ",")
            text = item["text"]

            srt_content += f"{i}\n"
            srt_content += f"{start_time} --> {end_time}\n"
            srt_content += f"{text}\n\n"

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(srt_content)
        print(f"正確なタイムスタンプでSRTファイルを生成しました: {output_path}")
