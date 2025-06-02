"""
Render.comへのデプロイ手順と環境変数設定ガイド
"""

# Render.comデプロイガイド

このドキュメントでは、ファンディングレート裁定ボットをRender.comにデプロイする手順を説明します。

## 前提条件

- Render.comのアカウントを持っていること
- GitHubなどのGitリポジトリにコードをプッシュしていること
- Solanaのキーペアファイルを用意していること
- BybitのAPIキーとシークレットを取得していること

## デプロイ手順

### 1. Render.comでの新規サービス作成

1. Render.comにログインし、ダッシュボードから「New +」ボタンをクリックします。
2. 「Web Service」を選択します。
3. GitHubなどのリポジトリと連携し、ボットのリポジトリを選択します。

### 2. サービス設定

以下の設定を行います：

- **Name**: 任意のサービス名（例：`funding-rate-arbitrage-bot`）
- **Region**: お好みのリージョン（通常は取引所に近いリージョンが望ましい）
- **Branch**: デプロイするブランチ（通常は `main` または `master`）
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python -m src.bot`

### 3. 環境変数の設定

「Environment」タブで以下の環境変数を設定します：

#### 必須環境変数

- `SOLANA_PRIVATE_KEY_PATH`: Solanaキーペアのパス（Render.comでは `/etc/secrets/solana_keypair.json` などに設定）
- `SOLANA_RPC_URL`: SolanaのRPC URL（例：`https://api.mainnet-beta.solana.com`）
- `BYBIT_API_KEY`: BybitのAPIキー
- `BYBIT_API_SECRET`: BybitのAPIシークレット

#### オプション環境変数

- `BYBIT_TESTNET`: テストネットを使用するかどうか（`true` または `false`、デフォルトは `false`）
- `POSITION_SIZE_USD`: ポジションサイズ（USD、デフォルトは `100`）
- `MAX_POSITION_SIZE_USD`: 最大ポジションサイズ（USD、デフォルトは `200`）
- `FUNDING_RATE_THRESHOLD`: ファンディングレートのしきい値（%、デフォルトは `0.01`）
- `PRICE_DEVIATION_THRESHOLD`: 価格乖離のしきい値（%、デフォルトは `1.5`）
- `BALANCE_ADJUSTMENT_THRESHOLD`: バランス調整のしきい値（%、デフォルトは `10`）
- `CHECK_INTERVAL_SECONDS`: チェック間隔（秒、デフォルトは `3600`）
- `LOG_LEVEL`: ログレベル（`DEBUG`、`INFO`、`WARNING`、`ERROR`、`CRITICAL`、デフォルトは `INFO`）
- `TELEGRAM_BOT_TOKEN`: Telegramボットトークン（通知機能を使用する場合）
- `TELEGRAM_CHAT_ID`: TelegramチャットID（通知機能を使用する場合）

### 4. シークレットファイルの設定

Solanaキーペアファイルは、Render.comの「Secrets」機能を使用して安全に保存します：

1. 「Environment」タブで「Add Secret File」をクリックします。
2. **Filename**: `/etc/secrets/solana_keypair.json`
3. **Contents**: Solanaキーペアファイルの内容（JSON形式）

### 5. デプロイ

すべての設定が完了したら、「Create Web Service」ボタンをクリックしてデプロイを開始します。

## 環境変数の詳細説明

### Solana/Drift Protocol設定

- `SOLANA_PRIVATE_KEY_PATH`: Solanaウォレットのキーペアファイルのパス。Render.comでは通常 `/etc/secrets/solana_keypair.json` などに設定します。
- `SOLANA_RPC_URL`: SolanaのRPC URL。無料のRPCエンドポイントを使用する場合は `https://api.mainnet-beta.solana.com` などを指定します。商用利用の場合は、Alchemy、Infura、QuickNodeなどの有料RPCプロバイダーの使用を検討してください。

### Bybit API設定

- `BYBIT_API_KEY`: BybitのAPIキー。Bybitのアカウント設定から取得できます。
- `BYBIT_API_SECRET`: BybitのAPIシークレット。APIキーと一緒に生成されます。
- `BYBIT_TESTNET`: テストネットを使用するかどうか。本番環境では `false` に設定します。

### ボット設定

- `POSITION_SIZE_USD`: 各ポジションのサイズ（USD）。初期設定は100 USDです。
- `MAX_POSITION_SIZE_USD`: 最大ポジションサイズ（USD）。リスク管理のために設定します。
- `FUNDING_RATE_THRESHOLD`: 裁定取引を実行するためのファンディングレート差のしきい値（%）。例えば、`0.01` は0.01%を意味します。
- `PRICE_DEVIATION_THRESHOLD`: 価格乖離の警告しきい値（%）。
- `BALANCE_ADJUSTMENT_THRESHOLD`: ポジションバランスの調整しきい値（%）。
- `CHECK_INTERVAL_SECONDS`: ファンディングレートをチェックする間隔（秒）。

### ログ設定

- `LOG_LEVEL`: ログレベル。`DEBUG`、`INFO`、`WARNING`、`ERROR`、`CRITICAL` のいずれかを指定します。
- `TELEGRAM_BOT_TOKEN`: Telegram通知を使用する場合のボットトークン。
- `TELEGRAM_CHAT_ID`: Telegram通知を送信するチャットID。

## トラブルシューティング

### デプロイに失敗する場合

- ログを確認して、エラーメッセージを特定します。
- 必要なすべての環境変数が正しく設定されているか確認します。
- Solanaキーペアファイルが正しいJSON形式であることを確認します。

### ボットが正常に動作しない場合

- ログを確認して、エラーメッセージを特定します。
- APIキーとシークレットが正しいことを確認します。
- ネットワーク接続に問題がないか確認します。
- ファンディングレートのしきい値が適切に設定されているか確認します。

## 監視とメンテナンス

- Render.comのダッシュボードでログを定期的に確認します。
- Telegram通知を設定している場合は、重要なイベントの通知を確認します。
- 定期的にボットのパフォーマンスを評価し、必要に応じてパラメータを調整します。
