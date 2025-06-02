"""
Bybit API接続モジュール
"""
import os
import time
from loguru import logger
from pybit.unified_trading import HTTP

class BybitClient:
    """Bybit APIとの接続・操作を行うクライアントクラス"""
    
    def __init__(self, config=None):
        """
        Bybitクライアントの初期化
        
        Args:
            config (dict, optional): 設定情報。指定がない場合は環境変数から読み込み
        """
        # 設定の読み込み
        self.config = config or {}
        self.api_key = self.config.get('api_key') or os.getenv('BYBIT_API_KEY')
        self.api_secret = self.config.get('api_secret') or os.getenv('BYBIT_API_SECRET')
        self.testnet = self.config.get('testnet') or (os.getenv('BYBIT_TESTNET', 'false').lower() == 'true')
        
        # Bybit APIクライアントの初期化
        self.client = HTTP(
            testnet=self.testnet,
            api_key=self.api_key,
            api_secret=self.api_secret
        )
        
        logger.info(f"Bybit client initialized (testnet: {self.testnet})")
    
    def get_funding_rate(self, symbol="BTCUSDT"):
        """
        指定されたシンボルの最新のファンディングレートを取得
        
        Args:
            symbol (str): 取引ペアシンボル
            
        Returns:
            float: ファンディングレート（8時間ごとのレート）
        """
        try:
            logger.info(f"Getting funding rate for {symbol} from Bybit")
            
            # Bybit APIを使用して最新のファンディングレートを取得
            response = self.client.get_funding_rate_history(
                category="linear",
                symbol=symbol,
                limit=1
            )
            
            if response['retCode'] == 0 and response['result']['list']:
                funding_rate = float(response['result']['list'][0]['fundingRate'])
                logger.info(f"Funding rate for {symbol}: {funding_rate}")
                return funding_rate
            else:
                logger.error(f"Failed to get funding rate: {response}")
                return None
        except Exception as e:
            logger.error(f"Error getting funding rate: {e}")
            return None
    
    def get_position(self, symbol="BTCUSDT"):
        """
        指定されたシンボルのポジション情報を取得
        
        Args:
            symbol (str): 取引ペアシンボル
            
        Returns:
            dict: ポジション情報
        """
        try:
            logger.info(f"Getting position for {symbol} from Bybit")
            
            # Bybit APIを使用してポジション情報を取得
            response = self.client.get_positions(
                category="linear",
                symbol=symbol
            )
            
            if response['retCode'] == 0 and response['result']['list']:
                position_data = response['result']['list'][0]
                position = {
                    "size": float(position_data['size']),
                    "side": position_data['side'],
                    "entry_price": float(position_data['entryPrice']),
                    "leverage": float(position_data['leverage']),
                    "liquidation_price": float(position_data['liqPrice']),
                    "unrealized_pnl": float(position_data['unrealisedPnl']),
                    "margin": float(position_data['positionIM'])
                }
                logger.info(f"Position for {symbol}: {position}")
                return position
            else:
                logger.info(f"No position found for {symbol}")
                return {
                    "size": 0.0,
                    "side": "None",
                    "entry_price": 0.0,
                    "leverage": 0.0,
                    "liquidation_price": 0.0,
                    "unrealized_pnl": 0.0,
                    "margin": 0.0
                }
        except Exception as e:
            logger.error(f"Error getting position: {e}")
            return None
    
    def open_position(self, symbol="BTCUSDT", side="Buy", size=0.0, price=None):
        """
        指定されたシンボルでポジションを開く
        
        Args:
            symbol (str): 取引ペアシンボル
            side (str): 取引方向 ("Buy" または "Sell")
            size (float): ポジションサイズ（契約数）
            price (float, optional): 指値価格。Noneの場合は成行注文
            
        Returns:
            dict: 注文結果
        """
        try:
            logger.info(f"Opening {side} position for {size} contracts in {symbol} on Bybit")
            
            # 注文タイプの設定
            order_type = "Market"
            if price is not None:
                order_type = "Limit"
            
            # Bybit APIを使用して注文を実行
            response = self.client.place_order(
                category="linear",
                symbol=symbol,
                side=side,
                orderType=order_type,
                qty=str(size),
                price=str(price) if price is not None else None,
                timeInForce="GTC"
            )
            
            if response['retCode'] == 0:
                order_id = response['result']['orderId']
                logger.info(f"Order placed successfully: {order_id}")
                
                # 注文の詳細を取得
                order_details = self.client.get_order_history(
                    category="linear",
                    orderId=order_id
                )
                
                return {
                    "order_id": order_id,
                    "status": order_details['result']['list'][0]['orderStatus'] if order_details['retCode'] == 0 else "Unknown",
                    "filled_size": float(order_details['result']['list'][0]['cumExecQty']) if order_details['retCode'] == 0 else 0.0,
                    "average_price": float(order_details['result']['list'][0]['avgPrice']) if order_details['retCode'] == 0 else 0.0
                }
            else:
                logger.error(f"Failed to place order: {response}")
                return None
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return None
    
    def close_position(self, symbol="BTCUSDT", side="Buy"):
        """
        指定されたシンボルのポジションを閉じる
        
        Args:
            symbol (str): 取引ペアシンボル
            side (str): 現在のポジション方向 ("Buy" または "Sell")
            
        Returns:
            dict: 注文結果
        """
        try:
            logger.info(f"Closing {side} position in {symbol} on Bybit")
            
            # 現在のポジションを取得
            position = self.get_position(symbol)
            
            if position and position['size'] > 0:
                # 反対方向の注文を出してポジションを閉じる
                close_side = "Sell" if side == "Buy" else "Buy"
                
                # Bybit APIを使用して注文を実行
                response = self.client.place_order(
                    category="linear",
                    symbol=symbol,
                    side=close_side,
                    orderType="Market",
                    qty=str(position['size']),
                    reduceOnly=True,
                    timeInForce="GTC"
                )
                
                if response['retCode'] == 0:
                    order_id = response['result']['orderId']
                    logger.info(f"Position closed successfully: {order_id}")
                    
                    # 注文の詳細を取得
                    order_details = self.client.get_order_history(
                        category="linear",
                        orderId=order_id
                    )
                    
                    return {
                        "order_id": order_id,
                        "status": order_details['result']['list'][0]['orderStatus'] if order_details['retCode'] == 0 else "Unknown",
                        "filled_size": float(order_details['result']['list'][0]['cumExecQty']) if order_details['retCode'] == 0 else 0.0,
                        "average_price": float(order_details['result']['list'][0]['avgPrice']) if order_details['retCode'] == 0 else 0.0
                    }
                else:
                    logger.error(f"Failed to close position: {response}")
                    return None
            else:
                logger.info(f"No position to close for {symbol}")
                return {
                    "order_id": None,
                    "status": "NoPosition",
                    "filled_size": 0.0,
                    "average_price": 0.0
                }
        except Exception as e:
            logger.error(f"Error closing position: {e}")
            return None
    
    def get_account_balance(self):
        """
        アカウント残高を取得
        
        Returns:
            float: アカウント残高（USDT）
        """
        try:
            logger.info("Getting account balance from Bybit")
            
            # Bybit APIを使用してアカウント残高を取得
            response = self.client.get_wallet_balance(
                accountType="UNIFIED",
                coin="USDT"
            )
            
            if response['retCode'] == 0 and response['result']['list']:
                balance = float(response['result']['list'][0]['coin'][0]['walletBalance'])
                logger.info(f"Account balance: {balance} USDT")
                return balance
            else:
                logger.error(f"Failed to get account balance: {response}")
                return None
        except Exception as e:
            logger.error(f"Error getting account balance: {e}")
            return None
