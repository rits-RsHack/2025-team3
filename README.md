# team3 - Audily: Audily
## サービスの概要
1.楽曲分離 \
Deezerの Spleeter を利用し、楽曲を自動で「ボーカル」「伴奏」「ドラム」「ベース」「ピアノ」に分離 \
出力形式: wav\
2.AIによる楽曲分析機能\
ユーザーが楽曲をアップロードすると、各曲の特徴（ボーカル比率、ドラムの強さ、テンポなど）を解析\
AIへのプロンプトは変更可能

## プレビュー
### トップページ
<img width="1920" height="1200" alt="スクリーンショット (57)" src="https://github.com/user-attachments/assets/e75a9e75-df9d-44a5-92e2-3b2d8b4cf26d" />
### ログインページ
<img width="1920" height="1200" alt="スクリーンショット (62)" src="https://github.com/user-attachments/assets/ae8ea335-0da3-4d56-8e45-453c411d3544" />
### メニュー画面
<img width="1920" height="1200" alt="スクリーンショット (58)" src="https://github.com/user-attachments/assets/b0aaa0aa-f095-437f-8af5-17ab01c421af" />
### Source Separation（楽曲分離）
<img width="1920" height="1200" alt="スクリーンショット (59)" src="https://github.com/user-attachments/assets/3d654273-845d-46a8-9eae-d387e537336d" />
### AI Music Analysis (楽曲分析)
<img width="1920" height="1200" alt="スクリーンショット (60)" src="https://github.com/user-attachments/assets/c47f7e1b-3378-4a72-8863-190ac5c96198" />

## 使用技術
使用言語:TypeScript,CSS,JavaScript,Python\
楽曲分離機能:ffmpeg,Spleeter\
楽曲分析機能:Gemini API

## 実装した機能
ログイン機能(メールアドレス+パスワード)
Source Separation(楽曲分離)
Music Recomendation(AIによる楽曲分析)

## 役割分担
### Zawa
ユーザー体験の設計と、フロントエンド開発。その他システムの大部分を担当。\
### Famous
バックエンドの各機能を、クライアント側とデータ通信させるための「APIエンドポイント」の設計、実装、およびテストを担当。

## アピールポイント
AI Music Analysisでは負荷を分散させるために、APIエンドポイントを3つに分割。

## 改善点

## 特にフィードバックが欲しいところ (任意)
