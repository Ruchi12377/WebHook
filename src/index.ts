import express from 'express';
import crypto from 'crypto';
import { exec } from 'child_process';
import * as fs from 'fs';
import * as path from 'path';
import dotenv from 'dotenv';

// 環境変数の読み込み
dotenv.config();

const app = express();
app.use(express.json());

// 環境変数から設定を読み込み
const PORT = process.env.PORT || 3000;
const SECRET = process.env.WEBHOOK_SECRET || '';
const REPO_PATH = process.env.REPO_PATH || '/home/pi/my-project';
const VENV_PATH = process.env.VENV_PATH || '/home/pi/my-project/venv';
const SERVICE_NAME = process.env.SERVICE_NAME || 'my-service';

// コマンド実行関数
const executeCommand = (command: string): Promise<string> => {
  return new Promise((resolve, reject) => {
    exec(command, (error, stdout, stderr) => {
      if (error) {
        console.error(`Error executing command: ${error.message}`);
        return reject(error);
      }
      if (stderr) {
        console.warn(`Command stderr: ${stderr}`);
      }
      console.log(`Command output: ${stdout}`);
      resolve(stdout);
    });
  });
};

// GitHub Webhookのシグネチャ検証
const verifySignature = (payload: any, signature: string): boolean => {
  if (!SECRET) {
    console.warn('Webhook secret not configured. Skipping signature verification.');
    return true;
  }

  const hmac = crypto.createHmac('sha256', SECRET);
  const digest = 'sha256=' + hmac.update(JSON.stringify(payload)).digest('hex');
  return crypto.timingSafeEqual(
    Buffer.from(digest),
    Buffer.from(signature)
  );
};

// GitHubからのWebhookエンドポイント
app.post('/webhook', async (req, res) => {
  try {
    const signature = req.headers['x-hub-signature-256'] as string;
    
    // シグネチャ検証
    if (!signature || !verifySignature(req.body, signature)) {
      console.error('Invalid signature');
      return res.status(401).send('Unauthorized');
    }

    const event = req.headers['x-github-event'];
    const payload = req.body;

    // pushイベントのみを処理
    if (event !== 'push') {
      console.log(`Ignoring ${event} event`);
      return res.status(200).send('Event ignored');
    }

    console.log('Received push event, processing deployment...');

    // 処理のステップ
    const steps = [
      // 1. リポジトリに移動
      `cd ${REPO_PATH}`,
      
      // 2. git pull の実行
      `${REPO_PATH} && git pull`,
      
      // 3. Pythonの仮想環境が存在しなければ作成
      `if [ ! -d "${VENV_PATH}" ]; then python3 -m venv ${VENV_PATH}; fi`,
      
      // 4. 仮想環境をアクティベートして依存関係をインストール
      `cd ${REPO_PATH} && source ${VENV_PATH}/bin/activate && pip install -r requirements.txt`,
      
      // 5. systemdサービスを再起動
      `sudo systemctl restart ${SERVICE_NAME}`
    ];

    // コマンドを順番に実行
    try {
      for (const command of steps) {
        console.log(`Executing: ${command}`);
        await executeCommand(command);
      }
      console.log('Deployment completed successfully');
      res.status(200).send('Deployment completed');
    } catch (error) {
      console.error('Deployment failed:', error);
      res.status(500).send('Deployment failed');
    }
  } catch (error) {
    console.error('Error processing webhook:', error);
    res.status(500).send('Internal server error');
  }
});

// サーバー起動
app.listen(PORT, () => {
  console.log(`Webhook server listening on port ${PORT}`);
  console.log(`Repository path: ${REPO_PATH}`);
  console.log(`Virtual env path: ${VENV_PATH}`);
  console.log(`Service name: ${SERVICE_NAME}`);
  console.log(`Webhook secret configured: ${Boolean(SECRET)}`);
});