"""
設定管理モジュール
"""
import os
from dotenv import load_dotenv

class Config:
    """
    アプリケーション設定を管理するクラス
    """
    
    def __init__(self):
        """
        設定の初期化
        """
        # 環境変数の読み込み
        load_dotenv()
        
        # Solana/Drift Protocol設定
        self.solana_private_key_path = os.getenv("SOLANA_PRIVATE_KEY_PATH")
        self.solana_rpc_url = os.getenv("SOLANA_RPC_URL")
        
        # Bybit API設定
        self.bybit_api_key = os.getenv("BYBIT_API_KEY")
        self.bybit_api_secret = os.getenv("BYBIT_API_SECRET")
        self.bybit_testnet = os.getenv("BYBIT_TESTNET", "false").lower() == "true"
        
        # ボット設定
        self.position_size_usd = float(os.getenv("POSITION_SIZE_USD", "100"))
        self.max_position_size_usd = float(os.getenv("MAX_POSITION_SIZE_USD", "200"))
        self.funding_rate_threshold = float(os.getenv("FUNDING_RATE_THRESHOLD", "0.01")) / 100  # パーセントから小数に変換
        self.price_deviation_threshold = float(os.getenv("PRICE_DEVIATION_THRESHOLD", "1.5")) / 100  # パーセントから小数に変換
        self.balance_adjustment_threshold = float(os.getenv("BALANCE_ADJUSTMENT_THRESHOLD", "10")) / 100  # パーセントから小数に変換
        self.check_interval_seconds = int(os.getenv("CHECK_INTERVAL_SECONDS", "3600"))
        
        # ログ設定
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    def validate(self):
        """
        設定の検証
        
        Returns:
            bool: 設定が有効な場合はTrue
        """
        # 必須項目のチェック
        required_fields = [
            "solana_private_key_path",
            "solana_rpc_url",
            "bybit_api_key",
            "bybit_api_secret"
        ]
        
        for field in required_fields:
            if not getattr(self, field):
                return False
        
        return True
    
    def get_dict(self):
        """
        設定を辞書形式で取得
        
        Returns:
            dict: 設定の辞書
        """
        return {
            "solana_private_key_path": self.solana_private_key_path,
            "solana_rpc_url": self.solana_rpc_url,
            "bybit_api_key": self.bybit_api_key,
            "bybit_api_secret": self.bybit_api_secret,
            "bybit_testnet": self.bybit_testnet,
            "position_size_usd": self.position_size_usd,
            "max_position_size_usd": self.max_position_size_usd,
            "funding_rate_threshold": self.funding_rate_threshold,
            "price_deviation_threshold": self.price_deviation_threshold,
            "balance_adjustment_threshold": self.balance_adjustment_threshold,
            "check_interval_seconds": self.check_interval_seconds,
            "log_level": self.log_level
        }
