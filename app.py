#!/usr/bin/env python3
import os
import json
import hmac
import hashlib
import subprocess
from flask import Flask, request, Response
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

app = Flask(__name__)

# 環境変数から設定を読み込み
PORT = int(os.getenv('PORT', 3000))
SECRET = os.getenv('WEBHOOK_SECRET', '')
REPO_PATH = os.getenv('REPO_PATH', '/home/pi/my-project')
VENV_PATH = os.getenv('VENV_PATH', '/home/pi/my-project/venv')
SERVICE_NAME = os.getenv('SERVICE_NAME', 'my-service')

# コマンド実行関数
def execute_command(command):
    """コマンドを実行し、結果を返す"""
    try:
        result = subprocess.run(command, shell=True, check=True, 
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True)
        if result.stderr:
            print(f"Command stderr: {result.stderr}")
        print(f"Command output: {result.stdout}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        raise

# GitHub Webhookのシグネチャ検証
def verify_signature(payload, signature):
    """ペイロードとシグネチャを検証する"""
    if not SECRET:
        print('Webhook secret not configured. Skipping signature verification.')
        return True
    
    expected_signature = 'sha256=' + hmac.new(
        SECRET.encode(), 
        payload.encode(), 
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected_signature, signature)

@app.route('/webhook', methods=['POST'])
def webhook_handler():
    """GitHubからのWebhookエンドポイント"""
    try:
        # リクエストのペイロードを文字列として取得
        payload_str = request.data.decode('utf-8')
        # JSONとして解析
        payload = json.loads(payload_str) if payload_str else {}
        
        # シグネチャ検証
        signature = request.headers.get('X-Hub-Signature-256')
        if not signature or not verify_signature(payload_str, signature):
            print('Invalid signature')
            return Response('Unauthorized', status=401)
        
        # イベントタイプの確認
        event = request.headers.get('X-GitHub-Event')
        
        # pushイベントのみを処理
        if event != 'push':
            print(f"Ignoring {event} event")
            return Response('Event ignored', status=200)
        
        print('Received push event, processing deployment...')
        
        # 処理のステップ
        steps = [
            # 1. リポジトリに移動して git pull を実行
            f"cd {REPO_PATH} && git pull",
            
            # 2. Pythonの仮想環境が存在しなければ作成
            f"if [ ! -d '{VENV_PATH}' ]; then python3 -m venv {VENV_PATH}; fi",
            
            # 3. 仮想環境をアクティベートして依存関係をインストール
            f"source {VENV_PATH}/bin/activate",

            # 4. 依存関係のインストール
            f"pip install -r {REPO_PATH}/requirements.txt",
            
            # 5. systemdサービスを再起動
            f"sudo systemctl restart {SERVICE_NAME}"
        ]
        
        # コマンドを順番に実行
        try:
            for command in steps:
                print(f"Executing: {command}")
                execute_command(command)
            print('Deployment completed successfully')
            return Response('Deployment completed', status=200)
        except Exception as e:
            print(f'Deployment failed: {e}')
            return Response('Deployment failed', status=500)
            
    except Exception as e:
        print(f'Error processing webhook: {e}')
        return Response('Internal server error', status=500)

@app.route('/')
def index():
    """ルートパスへのアクセス時にAPIが起動中であることを示すメッセージを表示"""
    return Response('Webhook API is running', status=200)

if __name__ == '__main__':
    print(f"Webhook server listening on port {PORT}")
    print(f"Repository path: {REPO_PATH}")
    print(f"Virtual env path: {VENV_PATH}")
    print(f"Service name: {SERVICE_NAME}")
    print(f"Webhook secret configured: {bool(SECRET)}")
    app.run(host='0.0.0.0', port=PORT, debug=False)