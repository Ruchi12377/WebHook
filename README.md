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

### 1. システム依存関係のインストール

Raspberry Pi上で以下のコマンドを実行して、必要なシステム依存関係をインストールします：

```bash
# システムの更新
sudo apt update
sudo apt upgrade -y

# Node.jsとnpmのインストール
sudo apt install -y nodejs npm

# Python 3とvenvモジュールのインストール
sudo apt install -y python3 python3-venv

# Gitのインストール
sudo apt install -y git
```

### 2. リポジトリをクローン

```bash
git clone https://github.com/Ruchi12377/webhook.git
cd webhook
```

### 3. Node.js依存関係のインストール

```bash
cd webhook
npm install
```

これにより、以下の主要な依存関係がインストールされます：
- express: Webhookサーバーの実装に使用
- dotenv: 環境変数の管理
- typescript: TypeScriptコンパイラ

### 4. 環境変数の設定

`.env` ファイルをプロジェクトのルートに作成し、以下の変数を設定します：

```bash
PORT=3000
WEBHOOK_SECRET=your_github_webhook_secret
REPO_PATH=/home/pi/your-project
VENV_PATH=/home/pi/your-project/venv
SERVICE_NAME=your-service
```

### 5. ビルド

```bash
npm run build
```

### 6. systemdサービスとしてインストール

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

## Python依存関係の自動インストールについて

このWebhookサーバーは、GitHubからのプッシュイベントを受信すると、以下の処理を自動的に行います：

1. 設定したPython仮想環境がない場合は作成
2. 仮想環境をアクティベート
3. `requirements.txt`に記載された依存関係をインストール

これにより、Pythonプロジェクトの依存関係は自動的に管理されます。`requirements.txt`ファイルは監視対象のPythonプロジェクト内に配置する必要があります。

## 開発

開発時には以下のコマンドでサーバーを起動できます：

```bash
npm run dev
```

## ライセンス

このプロジェクトは ISC ライセンスの下で公開されています。