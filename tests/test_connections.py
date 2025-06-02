"""
テスト実行スクリプト
"""
import asyncio
import os
from dotenv import load_dotenv
from loguru import logger

from src.drift.client import DriftClient
from src.bybit.client import BybitClient
from src.utils.config import Config
from src.utils.log_manager import LogManager

# 環境変数の読み込み
load_dotenv()

async def test_drift_connection():
    """Drift Protocolの接続テスト"""
    logger.info("Testing Drift Protocol connection...")
    
    try:
        drift_client = DriftClient()
        logger.info(f"Drift client initialized with address: {drift_client.keypair.public_key}")
        
        # ファンディングレートの取得テスト
        funding_rate = await drift_client.get_funding_rate()
        logger.info(f"Drift funding rate: {funding_rate}")
        
        # ポジション情報の取得テスト
        position = await drift_client.get_position()
        logger.info(f"Drift position: {position}")
        
        # アカウント残高の取得テスト
        balance = await drift_client.get_account_balance()
        logger.info(f"Drift account balance: {balance}")
        
        logger.success("Drift Protocol connection test passed!")
        return True
    except Exception as e:
        logger.error(f"Drift Protocol connection test failed: {e}")
        return False

def test_bybit_connection():
    """Bybitの接続テスト"""
    logger.info("Testing Bybit connection...")
    
    try:
        bybit_client = BybitClient()
        
        # ファンディングレートの取得テスト
        funding_rate = bybit_client.get_funding_rate()
        logger.info(f"Bybit funding rate: {funding_rate}")
        
        # ポジション情報の取得テスト
        position = bybit_client.get_position()
        logger.info(f"Bybit position: {position}")
        
        # アカウント残高の取得テスト
        balance = bybit_client.get_account_balance()
        logger.info(f"Bybit account balance: {balance}")
        
        logger.success("Bybit connection test passed!")
        return True
    except Exception as e:
        logger.error(f"Bybit connection test failed: {e}")
        return False

async def test_log_manager():
    """ログ管理のテスト"""
    logger.info("Testing log manager...")
    
    try:
        log_manager = LogManager()
        
        # 各種ログレベルのテスト
        await log_manager.log_info("This is an info message", notify=False)
        await log_manager.log_warning("This is a warning message")
        
        # Telegramが設定されている場合のみ通知テスト
        if log_manager.telegram_bot and log_manager.telegram_chat_id:
            await log_manager.log_info("This is a test notification", notify=True)
            await log_manager.log_arbitrage_opportunity(0.001, -0.001, 0.002)
        
        logger.success("Log manager test passed!")
        return True
    except Exception as e:
        logger.error(f"Log manager test failed: {e}")
        return False

async def test_config():
    """設定の読み込みテスト"""
    logger.info("Testing configuration...")
    
    try:
        config = Config()
        logger.info(f"Configuration loaded: {config.get_dict()}")
        
        # 設定の検証
        is_valid = config.validate()
        if is_valid:
            logger.success("Configuration validation passed!")
        else:
            logger.warning("Configuration validation failed. Some required fields are missing.")
        
        return is_valid
    except Exception as e:
        logger.error(f"Configuration test failed: {e}")
        return False

async def main():
    """メイン関数"""
    # ロガーの設定
    logger.remove()
    logger.add("logs/test_{time}.log", rotation="1 day", level="DEBUG")
    logger.add(lambda msg: print(msg), level="DEBUG")
    
    logger.info("Starting test script...")
    
    # 設定のテスト
    config_result = await test_config()
    
    # 接続テスト
    drift_result = await test_drift_connection()
    bybit_result = test_bybit_connection()
    
    # ログ管理のテスト
    log_result = await test_log_manager()
    
    # テスト結果のサマリー
    logger.info("Test results summary:")
    logger.info(f"Configuration test: {'PASSED' if config_result else 'FAILED'}")
    logger.info(f"Drift Protocol connection test: {'PASSED' if drift_result else 'FAILED'}")
    logger.info(f"Bybit connection test: {'PASSED' if bybit_result else 'FAILED'}")
    logger.info(f"Log manager test: {'PASSED' if log_result else 'FAILED'}")
    
    if all([config_result, drift_result, bybit_result, log_result]):
        logger.success("All tests passed! The bot is ready for operation.")
    else:
        logger.error("Some tests failed. Please check the logs for details.")

if __name__ == "__main__":
    asyncio.run(main())
