# ファンディングレート裁定ボット - セットアップと運用ガイド

## 概要

このプロジェクトは、SolanaのDrift ProtocolとBybit間のファンディングレート差を利用した裁定取引ボットです。両取引所でBTCのロング・ショートポジションを同時に保有することで、価格変動リスクを最小化しながらファンディングレートの差から利益を得ることを目的としています。

## 主な機能

- Drift ProtocolとBybitからのファンディングレート自動取得
- ファンディングレート差に基づく裁定機会の検出
- 自動ポジション構築（Drift: ロング/ショート、Bybit: ショート/ロング）
- ポジションバランスの自動調整
- リスク管理（価格乖離検出、最大ポジションサイズ制限）
- 詳細なログ記録とTelegram通知（オプション）
- Render.comでの24時間自動運用

## ファイル構成

```
crypto_arbitrage_bot/
├── src/
│   ├── drift/
│   │   └── client.py        # Drift Protocol API接続モジュール
│   ├── bybit/
│   │   └── client.py        # Bybit API接続モジュール
│   ├── utils/
│   │   ├── config.py        # 設定管理モジュール
│   │   └── log_manager.py   # ログ管理モジュール
│   └── bot.py               # メインボットロジック
├── tests/
│   ├── test_connections.py  # 接続テストスクリプト
│   └── test_dry_run.py      # ドライランテストスクリプト
├── docs/
│   ├── render_deployment_guide.md  # Render.comデプロイガイド
│   └── test_operation_guide.md     # テスト運用ガイド
├── .env.example             # 環境変数設定例
├── requirements.txt         # 依存パッケージリスト
├── render.yaml              # Render.com設定ファイル
└── README.md                # このファイル
```

## セットアップ手順

### 1. 前提条件

- Solana（Phantomウォレット）アカウント
- Bybitアカウント（APIキー・シークレット）
- Python 3.11以上

### 2. リポジトリのクローンと環境構築

```bash
# リポジトリをクローン
git clone <リポジトリURL>
cd crypto_arbitrage_bot

# 仮想環境の作成と有効化
python -m venv venv
source venv/bin/activate  # Windowsの場合: venv\Scripts\activate

# 依存パッケージのインストール
pip install -r requirements.txt
```

### 3. 環境変数の設定

`.env.example`ファイルをコピーして`.env`ファイルを作成し、必要な情報を設定します：

```bash
cp .env.example .env
```

`.env`ファイルを編集し、以下の項目を設定します：

```
# Solana/Drift Protocol設定
SOLANA_PRIVATE_KEY_PATH=/path/to/your/solana/keypair.json
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com

# Bybit API設定
BYBIT_API_KEY=your_bybit_api_key
BYBIT_API_SECRET=your_bybit_api_secret
BYBIT_TESTNET=false

# ボット設定
POSITION_SIZE_USD=100
MAX_POSITION_SIZE_USD=200
FUNDING_RATE_THRESHOLD=0.01  # 日率換算で0.01%
PRICE_DEVIATION_THRESHOLD=1.5  # 1.5%
BALANCE_ADJUSTMENT_THRESHOLD=10  # 10%
CHECK_INTERVAL_SECONDS=3600  # 1時間ごとにチェック

# ログ設定
LOG_LEVEL=INFO
TELEGRAM_BOT_TOKEN=your_telegram_bot_token  # オプション
TELEGRAM_CHAT_ID=your_telegram_chat_id  # オプション
```

### 4. 接続テスト

設定が正しいか確認するために、接続テストを実行します：

```bash
python -m tests.test_connections
```

すべてのテストが成功すれば、ボットの実行準備が整っています。

### 5. ドライランテスト

実際の取引を行わずにボットのロジックをテストします：

```bash
python -m tests.test_dry_run
```

ログを確認し、ボットが正しく動作しているか確認します。

### 6. ボットの実行

ローカル環境でボットを実行するには：

```bash
python -m src.bot
```

## Render.comへのデプロイ

24時間稼働させるために、Render.comにデプロイする手順は`docs/render_deployment_guide.md`を参照してください。主な手順は以下の通りです：

1. Render.comアカウントを作成
2. 新しいWebサービスを作成
3. GitHubリポジトリと連携
4. 環境変数を設定
5. Solanaキーペアをシークレットファイルとして設定
6. デプロイを実行

## 運用のポイント

### 最適なパラメータ設定

- `FUNDING_RATE_THRESHOLD`: 裁定取引を実行するためのファンディングレート差のしきい値。低すぎると取引コストを回収できない可能性があり、高すぎると裁定機会を逃す可能性があります。初期値は0.01%ですが、実際の運用結果に基づいて調整することをお勧めします。

- `CHECK_INTERVAL_SECONDS`: ファンディングレートをチェックする間隔。Bybitのファンディングレートは8時間ごとに適用されるため、1時間（3600秒）程度の間隔が適切です。

- `POSITION_SIZE_USD`: 各ポジションのサイズ。初期設定は100 USDですが、資金量に応じて調整してください。

### リスク管理

- `PRICE_DEVIATION_THRESHOLD`: 両取引所間の価格乖離のしきい値。価格乖離が大きい場合、裁定取引のリスクが高まる可能性があります。

- `BALANCE_ADJUSTMENT_THRESHOLD`: ポジションバランスの調整しきい値。両取引所のポジションサイズの差がこのしきい値を超えた場合、自動的に調整されます。

### 監視とメンテナンス

- ログを定期的に確認し、ボットの動作状況を監視してください。
- Telegram通知を設定している場合は、重要なイベントの通知を確認してください。
- 定期的にボットのパフォーマンスを評価し、必要に応じてパラメータを調整してください。

## トラブルシューティング

### 接続エラー

- APIキーとシークレットが正しいか確認してください。
- ネットワーク接続に問題がないか確認してください。
- Solana RPCエンドポイントが正常に動作しているか確認してください。

### 取引エラー

- 十分な資金があるか確認してください。
- 取引所の制限やルールに違反していないか確認してください。
- ポジションサイズが最小取引量を満たしているか確認してください。

### ボットが停止した場合

- ログを確認して、エラーメッセージを特定してください。
- Render.comのダッシュボードでサービスのステータスを確認してください。
- 必要に応じてサービスを再起動してください。

## 注意事項

- このボットは教育目的で提供されています。実際の運用は自己責任で行ってください。
- 暗号資産取引にはリスクが伴います。投資可能な資金のみを使用してください。
- 初期段階では少額でテストし、ボットの動作を十分に理解してから資金を増やすことをお勧めします。
- 税務上の取り扱いについては、専門家に相談してください。

## サポートとフィードバック

問題やフィードバックがある場合は、GitHubのIssueを通じてご連絡ください。
