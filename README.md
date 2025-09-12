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
![alt text](<スクリーンショット (57).png>)
### ログインページ
![alt text](<スクリーンショット (62).png>)
### メニュー画面
![alt text](<スクリーンショット (58).png>)
### Source Separation（楽曲分離）
![alt text](<スクリーンショット (59).png>)
### AI Music Analysis (楽曲分析)
![alt text](<スクリーンショット (60).png>)

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
