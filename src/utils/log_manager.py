"""
ログ管理モジュール
"""
import os
import sys
from datetime import datetime
from loguru import logger
import telegram

class LogManager:
    """
    ログ管理を行うクラス
    """
    
    def __init__(self, config=None):
        """
        ログ管理の初期化
        
        Args:
            config (dict, optional): 設定情報。指定がない場合は環境変数から読み込み
        """
        # 設定の読み込み
        self.config = config or {}
        self.log_level = self.config.get('log_level') or os.getenv('LOG_LEVEL', 'INFO')
        self.telegram_bot_token = self.config.get('telegram_bot_token') or os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = self.config.get('telegram_chat_id') or os.getenv('TELEGRAM_CHAT_ID')
        
        # ログディレクトリの作成
        os.makedirs('logs', exist_ok=True)
        
        # ロガーの設定
        self._setup_logger()
        
        # Telegramボットの初期化
        self.telegram_bot = None
        if self.telegram_bot_token and self.telegram_chat_id:
            try:
                self.telegram_bot = telegram.Bot(token=self.telegram_bot_token)
                logger.info("Telegram notification enabled")
            except Exception as e:
                logger.error(f"Failed to initialize Telegram bot: {e}")
    
    def _setup_logger(self):
        """
        ロガーの設定
        """
        # デフォルトのハンドラを削除
        logger.remove()
        
        # ファイルへのログ出力
        log_file = f"logs/bot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        logger.add(log_file, rotation="1 day", level=self.log_level)
        
        # コンソールへのログ出力
        logger.add(sys.stdout, level=self.log_level)
        
        logger.info(f"Logger initialized with level: {self.log_level}")
    
    async def send_telegram_notification(self, message):
        """
        Telegramに通知を送信
        
        Args:
            message (str): 送信するメッセージ
        """
        if self.telegram_bot and self.telegram_chat_id:
            try:
                await self.telegram_bot.send_message(chat_id=self.telegram_chat_id, text=message)
                logger.info(f"Telegram notification sent: {message}")
            except Exception as e:
                logger.error(f"Failed to send Telegram notification: {e}")
        else:
            logger.debug(f"Telegram notification not configured, message: {message}")
    
    async def log_critical(self, message):
        """
        重大なエラーをログに記録し、Telegramに通知
        
        Args:
            message (str): ログメッセージ
        """
        logger.critical(message)
        await self.send_telegram_notification(f"🚨 CRITICAL: {message}")
    
    async def log_error(self, message):
        """
        エラーをログに記録し、Telegramに通知
        
        Args:
            message (str): ログメッセージ
        """
        logger.error(message)
        await self.send_telegram_notification(f"❌ ERROR: {message}")
    
    async def log_warning(self, message):
        """
        警告をログに記録し、Telegramに通知
        
        Args:
            message (str): ログメッセージ
        """
        logger.warning(message)
        await self.send_telegram_notification(f"⚠️ WARNING: {message}")
    
    async def log_info(self, message, notify=False):
        """
        情報をログに記録し、オプションでTelegramに通知
        
        Args:
            message (str): ログメッセージ
            notify (bool): Telegramに通知するかどうか
        """
        logger.info(message)
        if notify:
            await self.send_telegram_notification(f"ℹ️ INFO: {message}")
    
    async def log_arbitrage_opportunity(self, drift_rate, bybit_rate, rate_diff):
        """
        裁定機会をログに記録し、Telegramに通知
        
        Args:
            drift_rate (float): Driftのファンディングレート
            bybit_rate (float): Bybitのファンディングレート
            rate_diff (float): ファンディングレートの差
        """
        message = f"Arbitrage opportunity found! Drift: {drift_rate}, Bybit: {bybit_rate}, Diff: {rate_diff}"
        logger.info(message)
        await self.send_telegram_notification(f"💰 {message}")
    
    async def log_position_opened(self, exchange, side, size, price):
        """
        ポジションオープンをログに記録し、Telegramに通知
        
        Args:
            exchange (str): 取引所名
            side (str): 取引方向
            size (float): ポジションサイズ
            price (float): 価格
        """
        message = f"Position opened on {exchange}: {side} {size} @ {price}"
        logger.info(message)
        await self.send_telegram_notification(f"🔓 {message}")
    
    async def log_position_closed(self, exchange, side, size, price, pnl=None):
        """
        ポジションクローズをログに記録し、Telegramに通知
        
        Args:
            exchange (str): 取引所名
            side (str): 取引方向
            size (float): ポジションサイズ
            price (float): 価格
            pnl (float, optional): 損益
        """
        message = f"Position closed on {exchange}: {side} {size} @ {price}"
        if pnl is not None:
            message += f", PnL: {pnl}"
        logger.info(message)
        await self.send_telegram_notification(f"🔒 {message}")
    
    async def log_daily_summary(self, drift_balance, bybit_balance, total_pnl):
        """
        日次サマリーをログに記録し、Telegramに通知
        
        Args:
            drift_balance (float): Driftの残高
            bybit_balance (float): Bybitの残高
            total_pnl (float): 合計損益
        """
        message = f"Daily summary - Drift balance: {drift_balance}, Bybit balance: {bybit_balance}, Total PnL: {total_pnl}"
        logger.info(message)
        await self.send_telegram_notification(f"📊 {message}")
