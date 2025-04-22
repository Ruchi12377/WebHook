# GitHub Webhook サーバー for Raspberry Pi

このプロジェクトは、ラズベリーパイで動作する GitHub Webhook サーバーです。GitHub リポジトリへのプッシュを検知して、以下の処理を自動的に実行します：

1. リポジトリの最新コードを `git pull` で取得
2. Python の仮想環境での依存関係のインストール
3. 指定した systemd サービスの再起動

## 必要要件

- Raspberry Pi (Raspberry Pi OS)
- Node.js (v12以上)
- npm
- Git
- Python 3 (venv モジュール)
- sudo 権限 (サービス再起動用)

## インストール方法

### 1. リポジトリをクローン

```bash
git clone https://github.com/Ruchi12377/webhook.git
cd webhook
```

### 2. 依存関係のインストール

```bash
npm install
```

### 3. 環境変数の設定

`.env` ファイルをプロジェクトのルートに作成し、以下の変数を設定します：

```bash
PORT=3000
WEBHOOK_SECRET=your_github_webhook_secret
REPO_PATH=/home/pi/your-project
VENV_PATH=/home/pi/your-project/venv
SERVICE_NAME=your-service
```

### 4. ビルド

```bash
npm run build
```

### 5. systemdサービスとしてインストール

```bash
sudo cp webhook.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable webhook
sudo systemctl start webhook
```

## GitHub Webhook の設定

1. GitHub リポジトリの Settings → Webhooks → Add webhook へ移動
2. Payload URL に `http://your-raspberry-pi-ip:3000/webhook` を入力
3. Content type に `application/json` を選択
4. Secret に `.env` ファイルの `WEBHOOK_SECRET` と同じ値を入力
5. プッシュイベントのみ選択（Just the push event）
6. Active にチェックを入れて「Add webhook」をクリック

## 使用方法

Webhook サーバーをインストールして設定した後は、GitHub リポジトリにプッシュするたびに、自動的にラズベリーパイ上のリポジトリが更新され、指定したサービスが再起動されます。

## 開発

開発時には以下のコマンドでサーバーを起動できます：

```bash
npm run dev
```

## ライセンス

このプロジェクトは ISC ライセンスの下で公開されています。