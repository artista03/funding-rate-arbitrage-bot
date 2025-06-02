"""
ファンディングレート裁定ボットのメインロジック
"""
import os
import asyncio
import time
from datetime import datetime
import schedule
from loguru import logger
from dotenv import load_dotenv

from src.drift.client import DriftClient
from src.bybit.client import BybitClient
from src.utils.config import Config

# 環境変数の読み込み
load_dotenv()

class ArbitrageBot:
    """
    Drift ProtocolとBybit間のファンディングレート裁定を行うボットクラス
    """
    
    def __init__(self):
        """
        ボットの初期化
        """
        # 設定の読み込み
        self.config = Config()
        
        # クライアントの初期化
        self.drift_client = DriftClient()
        self.bybit_client = BybitClient()
        
        # ロガーの設定
        self._setup_logger()
        
        logger.info("Arbitrage bot initialized")
    
    def _setup_logger(self):
        """
        ロガーの設定
        """
        log_level = os.getenv("LOG_LEVEL", "INFO")
        logger.remove()  # デフォルトのハンドラを削除
        logger.add("logs/bot_{time}.log", rotation="1 day", level=log_level)
        logger.add(lambda msg: print(msg), level=log_level)
    
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
    
    async def get_positions(self):
        """
        両取引所からポジション情報を取得
        
        Returns:
            tuple: (drift_position, bybit_position)
        """
        # Drift Protocolからポジション情報を取得
        drift_position = await self.drift_client.get_position()
        
        # Bybitからポジション情報を取得
        bybit_position = self.bybit_client.get_position()
        
        logger.info(f"Positions - Drift: {drift_position}, Bybit: {bybit_position}")
        
        return drift_position, bybit_position
    
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
        threshold = float(os.getenv("FUNDING_RATE_THRESHOLD", "0.01")) / 100  # パーセントから小数に変換
        
        # 裁定機会があるかチェック
        if abs(rate_diff) > threshold:
            logger.info(f"Arbitrage opportunity found! Rate difference: {rate_diff}")
            return True
        else:
            logger.info(f"No arbitrage opportunity. Rate difference: {rate_diff}")
            return False
    
    async def execute_arbitrage(self):
        """
        裁定取引を実行
        """
        # ファンディングレートを取得
        drift_rate, bybit_rate = await self.get_funding_rates()
        
        if drift_rate is None or bybit_rate is None:
            logger.warning("Failed to get funding rates")
            return
        
        # 現在のポジションを取得
        drift_position, bybit_position = await self.get_positions()
        
        # ポジションサイズを取得
        position_size_usd = float(os.getenv("POSITION_SIZE_USD", "100"))
        
        # ファンディングレートの差に基づいてポジションを構築
        if drift_rate > bybit_rate:
            # Drift: short, Bybit: long
            logger.info("Strategy: Drift (short) / Bybit (long)")
            
            # 既存のポジションをチェック
            if drift_position["size"] > 0:
                await self.drift_client.close_position(side="long")
            
            if bybit_position["side"] == "Sell":
                self.bybit_client.close_position(side="Sell")
            
            # 新しいポジションを開く
            await self.drift_client.open_position(side="short", size=position_size_usd)
            self.bybit_client.open_position(side="Buy", size=position_size_usd)
            
        else:
            # Drift: long, Bybit: short
            logger.info("Strategy: Drift (long) / Bybit (short)")
            
            # 既存のポジションをチェック
            if drift_position["size"] < 0:
                await self.drift_client.close_position(side="short")
            
            if bybit_position["side"] == "Buy":
                self.bybit_client.close_position(side="Buy")
            
            # 新しいポジションを開く
            await self.drift_client.open_position(side="long", size=position_size_usd)
            self.bybit_client.open_position(side="Sell", size=position_size_usd)
        
        logger.info("Arbitrage executed successfully")
    
    async def check_and_rebalance(self):
        """
        ポジションのバランスをチェックし、必要に応じて再調整
        """
        # 現在のポジションを取得
        drift_position, bybit_position = await self.get_positions()
        
        # バランス調整のしきい値を取得
        balance_threshold = float(os.getenv("BALANCE_ADJUSTMENT_THRESHOLD", "10")) / 100  # パーセントから小数に変換
        
        # ポジションサイズを比較
        drift_size = abs(drift_position["size"])
        bybit_size = abs(bybit_position["size"]) if bybit_position["side"] != "None" else 0
        
        if drift_size == 0 or bybit_size == 0:
            logger.info("One or both positions are zero, no rebalancing needed")
            return
        
        # サイズの差を計算
        size_diff_percent = abs(drift_size - bybit_size) / max(drift_size, bybit_size)
        
        # しきい値を超えた場合は再調整
        if size_diff_percent > balance_threshold:
            logger.info(f"Position imbalance detected: {size_diff_percent:.2%}")
            
            # 再調整のロジックを実装
            # 例: 大きい方のポジションを小さい方に合わせる
            if drift_size > bybit_size:
                # Driftのポジションを縮小
                new_size = bybit_size
                side = "long" if drift_position["size"] > 0 else "short"
                await self.drift_client.close_position(side=side)
                await self.drift_client.open_position(side=side, size=new_size)
                logger.info(f"Rebalanced Drift position to {new_size}")
            else:
                # Bybitのポジションを縮小
                new_size = drift_size
                side = bybit_position["side"]
                self.bybit_client.close_position(side=side)
                self.bybit_client.open_position(side=side, size=new_size)
                logger.info(f"Rebalanced Bybit position to {new_size}")
        else:
            logger.info(f"Positions are balanced: {size_diff_percent:.2%}")
    
    async def check_price_deviation(self):
        """
        価格乖離をチェック
        
        Returns:
            bool: 価格乖離が大きい場合はTrue
        """
        # 現在のポジションを取得
        drift_position, bybit_position = await self.get_positions()
        
        # 価格がない場合はスキップ
        if drift_position["entry_price"] == 0 or bybit_position["entry_price"] == 0:
            return False
        
        # 価格乖離のしきい値を取得
        price_threshold = float(os.getenv("PRICE_DEVIATION_THRESHOLD", "1.5")) / 100  # パーセントから小数に変換
        
        # 価格乖離を計算
        price_diff_percent = abs(drift_position["entry_price"] - bybit_position["entry_price"]) / max(drift_position["entry_price"], bybit_position["entry_price"])
        
        # しきい値を超えた場合は警告
        if price_diff_percent > price_threshold:
            logger.warning(f"Price deviation detected: {price_diff_percent:.2%}")
            return True
        else:
            logger.info(f"Price deviation is within threshold: {price_diff_percent:.2%}")
            return False
    
    async def run_once(self):
        """
        1回の実行サイクル
        """
        try:
            logger.info("Starting arbitrage check cycle")
            
            # 裁定機会があるかチェック
            opportunity = await self.check_arbitrage_opportunity()
            
            if opportunity:
                # 裁定取引を実行
                await self.execute_arbitrage()
            
            # ポジションのバランスをチェック
            await self.check_and_rebalance()
            
            # 価格乖離をチェック
            await self.check_price_deviation()
            
            logger.info("Arbitrage check cycle completed")
        
        except Exception as e:
            logger.error(f"Error in arbitrage cycle: {e}")
    
    async def run(self):
        """
        ボットを実行
        """
        logger.info("Starting arbitrage bot")
        
        # チェック間隔を取得
        check_interval = int(os.getenv("CHECK_INTERVAL_SECONDS", "3600"))
        
        while True:
            await self.run_once()
            logger.info(f"Waiting for {check_interval} seconds until next check")
            await asyncio.sleep(check_interval)

async def main():
    """
    メイン関数
    """
    # 環境変数の読み込み
    load_dotenv()
    
    # ボットの初期化と実行
    bot = ArbitrageBot()
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())
