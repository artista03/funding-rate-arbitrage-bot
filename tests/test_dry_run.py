"""
ドライランモード用のテストスクリプト
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

# ドライランモード（実際の取引は行わない）
DRY_RUN = True

class ArbitrageTestBot:
    """
    ファンディングレート裁定ボットのテスト実行クラス
    """
    
    def __init__(self):
        """
        テストボットの初期化
        """
        # 設定の読み込み
        self.config = Config()
        
        # クライアントの初期化
        self.drift_client = DriftClient()
        self.bybit_client = BybitClient()
        
        # ログ管理の初期化
        self.log_manager = LogManager()
        
        logger.info("Arbitrage test bot initialized")
    
    async def get_funding_rates(self):
        """
        両取引所からファンディングレートを取得
        
        Returns:
            tuple: (drift_rate, bybit_rate)
        """
        # Drift Protocolからファンディングレートを取得
        drift_rate = await self.drift_client.get_funding_rate()
        
        # Bybitからファンディングレートを取得
        bybit_rate = self.bybit_client.get_funding_rate()
        
        logger.info(f"Funding rates - Drift: {drift_rate}, Bybit: {bybit_rate}")
        
        return drift_rate, bybit_rate
    
    async def check_arbitrage_opportunity(self):
        """
        裁定機会があるかチェック
        
        Returns:
            bool: 裁定機会がある場合はTrue
        """
        # ファンディングレートを取得
        drift_rate, bybit_rate = await self.get_funding_rates()
        
        if drift_rate is None or bybit_rate is None:
            logger.warning("Failed to get funding rates")
            return False
        
        # ファンディングレートの差を計算
        rate_diff = drift_rate - bybit_rate
        
        # しきい値を取得
        threshold = self.config.funding_rate_threshold
        
        # 裁定機会があるかチェック
        if abs(rate_diff) > threshold:
            logger.info(f"Arbitrage opportunity found! Rate difference: {rate_diff}")
            await self.log_manager.log_arbitrage_opportunity(drift_rate, bybit_rate, rate_diff)
            return True
        else:
            logger.info(f"No arbitrage opportunity. Rate difference: {rate_diff}")
            return False
    
    async def simulate_arbitrage(self):
        """
        裁定取引をシミュレーション（ドライランモード）
        """
        # ファンディングレートを取得
        drift_rate, bybit_rate = await self.get_funding_rates()
        
        if drift_rate is None or bybit_rate is None:
            logger.warning("Failed to get funding rates")
            return
        
        # ポジションサイズを取得
        position_size_usd = self.config.position_size_usd
        
        # ファンディングレートの差に基づいてポジションを構築
        if drift_rate > bybit_rate:
            # Drift: short, Bybit: long
            logger.info("Strategy: Drift (short) / Bybit (long)")
            
            if not DRY_RUN:
                # 実際の取引を行う場合のコード
                await self.drift_client.open_position(side="short", size=position_size_usd)
                self.bybit_client.open_position(side="Buy", size=position_size_usd)
            else:
                # ドライランモードでのシミュレーション
                logger.info(f"[DRY RUN] Would open SHORT position on Drift for {position_size_usd} USD")
                logger.info(f"[DRY RUN] Would open LONG position on Bybit for {position_size_usd} USD")
            
            # ログに記録
            await self.log_manager.log_info(f"Simulated arbitrage: Drift (short) / Bybit (long) for {position_size_usd} USD", notify=True)
            
        else:
            # Drift: long, Bybit: short
            logger.info("Strategy: Drift (long) / Bybit (short)")
            
            if not DRY_RUN:
                # 実際の取引を行う場合のコード
                await self.drift_client.open_position(side="long", size=position_size_usd)
                self.bybit_client.open_position(side="Sell", size=position_size_usd)
            else:
                # ドライランモードでのシミュレーション
                logger.info(f"[DRY RUN] Would open LONG position on Drift for {position_size_usd} USD")
                logger.info(f"[DRY RUN] Would open SHORT position on Bybit for {position_size_usd} USD")
            
            # ログに記録
            await self.log_manager.log_info(f"Simulated arbitrage: Drift (long) / Bybit (short) for {position_size_usd} USD", notify=True)
        
        logger.info("Arbitrage simulation completed")
    
    async def run_test_cycle(self):
        """
        テストサイクルを実行
        """
        try:
            logger.info("Starting arbitrage test cycle")
            
            # 裁定機会があるかチェック
            opportunity = await self.check_arbitrage_opportunity()
            
            if opportunity:
                # 裁定取引をシミュレーション
                await self.simulate_arbitrage()
            
            logger.info("Arbitrage test cycle completed")
            
        except Exception as e:
            logger.error(f"Error in arbitrage test cycle: {e}")
            await self.log_manager.log_error(f"Test cycle error: {e}")

async def main():
    """
    メイン関数
    """
    # ロガーの設定
    logger.remove()
    logger.add("logs/test_run_{time}.log", rotation="1 day", level="DEBUG")
    logger.add(lambda msg: print(msg), level="DEBUG")
    
    logger.info("Starting arbitrage bot test run...")
    logger.info(f"DRY RUN mode: {DRY_RUN}")
    
    # テストボットの初期化と実行
    bot = ArbitrageTestBot()
    await bot.run_test_cycle()
    
    logger.info("Test run completed")

if __name__ == "__main__":
    asyncio.run(main())
