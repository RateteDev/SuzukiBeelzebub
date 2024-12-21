# Discord Bot セットアップガイド

## 前提条件

### 必要なソフトウェア
1. Python 3.8以上
2. FFmpeg
3. Discord Bot Token
4. Google Gemini API Key

### Pythonパッケージ
- discord.py v2.3.2
- python-dotenv v1.0.0
- google-generativeai v0.3.2
- gTTS v2.5.0
- PyNaCl v1.5.0

## インストール手順

### 1. リポジトリのクローン
```bash
git clone [リポジトリURL]
cd [プロジェクトディレクトリ]
```

### 2. 環境変数の設定
`.env`ファイルをプロジェクトルートに作成し、以下の内容を設定：
```env
MY_API_TOKEN=your_discord_bot_token
MY_API_KEY=your_gemini_api_key
```

### 3. 依存パッケージのインストール
```bash
pip install -r requirements.txt
```

### 4. FFmpegのインストール
#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install -y ffmpeg
```

#### Windows
1. [FFmpeg公式サイト](https://ffmpeg.org/download.html)からダウンロード
2. システム環境変数のPATHに追加

## ボットの設定

### Discord Developer Portalでの設定
1. [Discord Developer Portal](https://discord.com/developers/applications)にアクセス
2. 「New Application」をクリック
3. Bot設定で以下の権限を有効化：
   - Read Messages/View Channels
   - Send Messages
   - Connect
   - Speak
   - Use Slash Commands
4. OAuth2 URLを生成し、ボットをサーバーに招待

### Gemini APIの設定
1. [Google Cloud Console](https://console.cloud.google.com/)でプロジェクトを作成
2. Gemini APIを有効化
3. APIキーを生成

## 起動方法

### 開発環境での起動
```bash
python main.py
```

### 本番環境での起動（バックグラウンド）
```bash
nohup python main.py > bot.log 2>&1 &
```

## ディレクトリ構造
```
.
├── doc/                # ドキュメント
├── src/               # ソースコード
│   ├── discord_bot/   # Discordボット関連
│   ├── services/      # 各種サービス
│   └── utils/         # ユーティリティ
├── tests/             # テストコード
├── .env               # 環境変数
├── main.py            # エントリーポイント
└── requirements.txt   # 依存パッケージ
```

## トラブルシューティング

### 一般的な問題
1. ボットが起動しない
   - 環境変数の設定を確認
   - 依存パッケージのインストール状態を確認
   - ログファイルを確認

2. 音声が再生されない
   - FFmpegのインストールを確認
   - ボットの権限設定を確認
   - VC接続状態を確認

3. APIエラー
   - APIキーの有効性を確認
   - レート制限の確認
   - ネットワーク接続の確認

### ログの確認
- ログファイル: `discord_bot.log`
- フォーマット: `時刻 - モジュール名 - ログレベル - メッセージ`

## 開発環境のセットアップ

### 1. 仮想環境の作成
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 2. 開発用パッケージのインストール
```bash
pip install -r requirements.txt
```

### 3. コードフォーマット
```bash
# 必要に応じてblackやflake8をインストール
pip install black flake8
black .
flake8
```
