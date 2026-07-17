import math
from typing import List
from app.market_data.models import HistoricalPriceSeries
from app.analysis.models import RiskMetrics

class RiskEngine:
    """
    Computes risk metrics like Beta, Volatility, Sharpe, Drawdown from timeseries data.
    """
    
    def _calculate_returns(self, prices: List[float]) -> List[float]:
        returns = []
        for i in range(1, len(prices)):
            if prices[i-1] != 0:
                returns.append((prices[i] - prices[i-1]) / prices[i-1])
            else:
                returns.append(0)
        return returns

    def _mean(self, data: List[float]) -> float:
        if not data: return 0.0
        return sum(data) / len(data)
        
    def _variance(self, data: List[float], mean: float) -> float:
        if len(data) < 2: return 0.0
        return sum((x - mean) ** 2 for x in data) / (len(data) - 1)
        
    def _covariance(self, x: List[float], y: List[float], mean_x: float, mean_y: float) -> float:
        if len(x) != len(y) or len(x) < 2: return 0.0
        return sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(len(x))) / (len(x) - 1)

    def compute(
        self,
        asset_history: HistoricalPriceSeries,
        market_history: HistoricalPriceSeries,
        risk_free_rate: float = 0.04
    ) -> RiskMetrics:
        
        # We need daily closing prices. Assume they are aligned by date in production.
        # For simplicity in this engine, we pair them by index.
        min_len = min(len(asset_history.prices), len(market_history.prices))
        
        asset_prices = [p.close for p in asset_history.prices[:min_len]]
        market_prices = [p.close for p in market_history.prices[:min_len]]
        
        asset_returns = self._calculate_returns(asset_prices)
        market_returns = self._calculate_returns(market_prices)
        
        if not asset_returns:
            return RiskMetrics(beta=1.0, volatility=0.0, sharpe_ratio=0.0, sortino_ratio=0.0, max_drawdown=0.0, alpha=0.0, correlation_to_market=1.0)
            
        mean_asset = self._mean(asset_returns)
        mean_market = self._mean(market_returns)
        
        var_asset = self._variance(asset_returns, mean_asset)
        var_market = self._variance(market_returns, mean_market)
        
        cov = self._covariance(asset_returns, market_returns, mean_asset, mean_market)
        
        # Volatility (Annualized std dev, assuming ~252 trading days)
        std_dev = math.sqrt(var_asset)
        volatility = std_dev * math.sqrt(252)
        
        # Beta
        beta = cov / var_market if var_market != 0 else 1.0
        
        # Correlation
        correlation = cov / (math.sqrt(var_asset) * math.sqrt(var_market)) if (var_asset > 0 and var_market > 0) else 0.0
        
        # Alpha (Annualized)
        annualized_asset_return = mean_asset * 252
        annualized_market_return = mean_market * 252
        alpha = annualized_asset_return - (risk_free_rate + beta * (annualized_market_return - risk_free_rate))
        
        # Sharpe Ratio
        excess_return = annualized_asset_return - risk_free_rate
        sharpe_ratio = excess_return / volatility if volatility != 0 else 0.0
        
        # Sortino Ratio (Downside deviation)
        downside_returns = [r for r in asset_returns if r < 0]
        if downside_returns:
            downside_mean = self._mean(downside_returns)
            downside_var = self._variance(downside_returns, downside_mean)
            downside_dev = math.sqrt(downside_var) * math.sqrt(252)
            sortino_ratio = excess_return / downside_dev if downside_dev != 0 else 0.0
        else:
            sortino_ratio = 0.0
            
        # Max Drawdown
        max_drawdown = 0.0
        peak = asset_prices[0] if asset_prices else 0.0
        for price in asset_prices:
            if price > peak:
                peak = price
            drawdown = (peak - price) / peak if peak > 0 else 0.0
            if drawdown > max_drawdown:
                max_drawdown = drawdown
                
        return RiskMetrics(
            beta=beta,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            max_drawdown=max_drawdown,
            alpha=alpha,
            correlation_to_market=correlation
        )
