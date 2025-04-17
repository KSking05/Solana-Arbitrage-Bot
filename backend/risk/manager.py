import logging
from decimal import Decimal
from typing import Dict, Optional
from sqlalchemy.orm import Session
from ..db import models

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("risk_manager")

class RiskManager:
    def __init__(self, db: Session):
        self.db = db
        logger.info("Initialized Risk Manager")
    
    def assess_trade_risk(self, user_id: int, opportunity_id: int) -> Dict:
        """
        Assess the risk of a trade based on various factors
        Returns a risk score and recommendation
        """
        try:
            # Get opportunity
            opportunity = self.db.query(models.Opportunity).filter(
                models.Opportunity.id == opportunity_id
            ).first()
            
            if not opportunity:
                logger.error(f"Opportunity {opportunity_id} not found")
                return {
                    "risk_score": 10,  # Maximum risk
                    "recommendation": "Do not trade - opportunity not found",
                    "can_execute": False
                }
            
            # Get user settings
            trading_settings = self.db.query(models.Setting).filter(
                models.Setting.user_id == user_id,
                models.Setting.category == "trading"
            ).first()
            
            if not trading_settings:
                logger.error(f"Trading settings not found for user {user_id}")
                return {
                    "risk_score": 8,
                    "recommendation": "Configure trading settings first",
                    "can_execute": False
                }
            
            settings = trading_settings.settings
            user_risk_level = int(settings.get("risk_level", 5))  # 1-10 scale
            min_profit_threshold = Decimal(settings.get("min_profit_threshold", 0.25))
            
            # Calculate base risk score (lower is better)
            risk_score = 5  # Default medium risk
            
            # Factor 1: Price difference
            if opportunity.price_diff_percent < min_profit_threshold:
                risk_score += 3
            elif opportunity.price_diff_percent > min_profit_threshold * 4:
                risk_score -= 2
            elif opportunity.price_diff_percent > min_profit_threshold * 2:
                risk_score -= 1
            
            # Factor 2: Token liquidity (mock implementation)
            # In a real system, you would check actual liquidity on DEXes
            token = self.db.query(models.Token).filter(models.Token.id == opportunity.token_id).first()
            if token:
                if token.symbol == "SOL":
                    risk_score -= 1  # SOL is highly liquid
                elif token.symbol in ["USDC", "USDT"]:
                    risk_score -= 2  # Stablecoins are very liquid
                elif token.symbol in ["BONK", "JTO"]:
                    risk_score += 1  # Meme tokens can be more volatile
            
            # Factor 3: DEX reliability (mock implementation)
            # In a real system, you would check DEX reliability metrics
            buy_dex = self.db.query(models.Dex).filter(models.Dex.id == opportunity.buy_dex_id).first()
            sell_dex = self.db.query(models.Dex).filter(models.Dex.id == opportunity.sell_dex_id).first()
            
            if buy_dex and buy_dex.name == "Jupiter":
                risk_score -= 1  # Jupiter is reliable
            if sell_dex and sell_dex.name == "Jupiter":
                risk_score -= 1
            
            # Adjust risk score based on user's risk tolerance
            adjusted_risk_score = max(1, min(10, risk_score + (5 - user_risk_level)))
            
            # Determine recommendation
            recommendation = "Proceed with caution"
            can_execute = True
            
            if adjusted_risk_score <= 3:
                recommendation = "Low risk trade - good opportunity"
            elif adjusted_risk_score <= 6:
                recommendation = "Moderate risk - proceed with caution"
            elif adjusted_risk_score <= 8:
                recommendation = "High risk - consider skipping"
                can_execute = user_risk_level >= 7  # Only high risk tolerance users should proceed
            else:
                recommendation = "Very high risk - do not trade"
                can_execute = False
            
            return {
                "risk_score": adjusted_risk_score,
                "recommendation": recommendation,
                "can_execute": can_execute,
                "factors": {
                    "price_difference": float(opportunity.price_diff_percent),
                    "min_threshold": float(min_profit_threshold),
                    "user_risk_level": user_risk_level
                }
            }
        
        except Exception as e:
            logger.error(f"Error assessing trade risk: {str(e)}")
            return {
                "risk_score": 9,
                "recommendation": f"Error assessing risk: {str(e)}",
                "can_execute": False
            }
    
    def check_portfolio_risk(self, user_id: int) -> Dict:
        """
        Assess the overall portfolio risk for a user
        """
        try:
            # Get user's wallets
            wallets = self.db.query(models.Wallet).filter(models.Wallet.user_id == user_id).all()
            wallet_ids = [wallet.id for wallet in wallets]
            
            if not wallet_ids:
                return {
                    "risk_level": "Unknown",
                    "recommendation": "Add a wallet to assess portfolio risk",
                    "diversification_score": 0
                }
            
            # Get token balances
            token_balances = self.db.query(models.TokenBalance).filter(
                models.TokenBalance.wallet_id.in_(wallet_ids)
            ).all()
            
            if not token_balances:
                return {
                    "risk_level": "Unknown",
                    "recommendation": "No token balances found",
                    "diversification_score": 0
                }
            
            # Calculate portfolio metrics
            total_value_usd = Decimal("0")
            token_values = {}
            
            for balance in token_balances:
                token = self.db.query(models.Token).filter(models.Token.id == balance.token_id).first()
                if token:
                    # In a real implementation, you would get current token prices
                    # For now, we'll use mock prices
                    price_usd = Decimal("0")
                    if token.symbol == "SOL":
                        price_usd = Decimal("100")
                    elif token.symbol == "USDC":
                        price_usd = Decimal("1")
                    elif token.symbol == "BONK":
                        price_usd = Decimal("0.00000125")
                    elif token.symbol == "RAY":
                        price_usd = Decimal("0.78")
                    elif token.symbol == "JTO":
                        price_usd = Decimal("2.34")
                    
                    value_usd = balance.balance * price_usd
                    token_values[token.symbol] = value_usd
                    total_value_usd += value_usd
            
            # Calculate concentration risk
            max_concentration = Decimal("0")
            most_concentrated_token = None
            
            for token_symbol, value in token_values.items():
                if total_value_usd > 0:
                    concentration = value / total_value_usd
                    if concentration > max_concentration:
                        max_concentration = concentration
                        most_concentrated_token = token_symbol
            
            # Assess diversification
            diversification_score = 0
            if len(token_values) >= 5:
                diversification_score = 10
            elif len(token_values) >= 3:
                diversification_score = 7
            elif len(token_values) >= 2:
                diversification_score = 5
            else:
                diversification_score = 3
            
            # Adjust for concentration
            if max_concentration > Decimal("0.8"):
                diversification_score -= 3
            elif max_concentration > Decimal("0.6"):
                diversification_score -= 2
            elif max_concentration > Decimal("0.4"):
                diversification_score -= 1
            
            # Determine risk level
            risk_level = "Medium"
            recommendation = "Consider diversifying your portfolio"
            
            if diversification_score >= 8:
                risk_level = "Low"
                recommendation = "Well-diversified portfolio"
            elif diversification_score <= 4:
                risk_level = "High"
                recommendation = f"Portfolio heavily concentrated in {most_concentrated_token}"
            
            return {
                "risk_level": risk_level,
                "recommendation": recommendation,
                "diversification_score": diversification_score,
                "total_value_usd": float(total_value_usd),
                "token_count": len(token_values),
                "max_concentration": float(max_concentration) if max_concentration else 0,
                "most_concentrated_token": most_concentrated_token
            }
        
        except Exception as e:
            logger.error(f"Error assessing portfolio risk: {str(e)}")
            return {
                "risk_level": "Unknown",
                "recommendation": f"Error assessing portfolio risk: {str(e)}",
                "diversification_score": 0
            }
