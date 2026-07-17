from app.analysis.models import RatioMetrics, RiskMetrics, ScoreCategory, CompanyScores

class CompanyScoringEngine:
    """
    Translates raw metrics into 0-100 scores with textual explanations.
    Uses generic absolute thresholds. (Production would use sector medians).
    """

    def _score_health(self, ratios: RatioMetrics) -> ScoreCategory:
        score = 50
        exp = []
        
        if ratios.current_ratio > 1.5:
            score += 15
            exp.append(f"Strong current ratio ({ratios.current_ratio:.2f}) indicates good short-term liquidity.")
        elif ratios.current_ratio < 1.0:
            score -= 20
            exp.append(f"Weak current ratio ({ratios.current_ratio:.2f}) suggests potential liquidity issues.")
            
        if ratios.debt_to_equity < 0.5:
            score += 20
            exp.append(f"Conservative debt-to-equity ({ratios.debt_to_equity:.2f}) minimizes solvency risk.")
        elif ratios.debt_to_equity > 2.0:
            score -= 25
            exp.append(f"High debt-to-equity ({ratios.debt_to_equity:.2f}) indicates heavy reliance on leverage.")
            
        if ratios.interest_coverage > 5.0:
            score += 15
            exp.append(f"Excellent interest coverage ({ratios.interest_coverage:.2f}x).")
            
        score = max(0, min(100, score))
        return ScoreCategory(score=score, explanation=" ".join(exp) if exp else "Average financial health.")

    def _score_profitability(self, ratios: RatioMetrics) -> ScoreCategory:
        score = 50
        exp = []
        
        if ratios.operating_margin > 15.0:
            score += 20
            exp.append(f"High operating margin ({ratios.operating_margin:.1f}%).")
        elif ratios.operating_margin < 5.0:
            score -= 15
            exp.append(f"Low operating margin ({ratios.operating_margin:.1f}%).")
            
        if ratios.return_on_equity > 15.0:
            score += 20
            exp.append(f"Strong ROE ({ratios.return_on_equity:.1f}%).")
        elif ratios.return_on_equity < 8.0:
            score -= 10
            exp.append(f"Below average ROE ({ratios.return_on_equity:.1f}%).")
            
        if ratios.return_on_invested_capital > 10.0:
            score += 10
            exp.append(f"Good ROIC ({ratios.return_on_invested_capital:.1f}%).")
            
        score = max(0, min(100, score))
        return ScoreCategory(score=score, explanation=" ".join(exp) if exp else "Average profitability.")

    def _score_growth(self, ratios: RatioMetrics) -> ScoreCategory:
        score = 50
        exp = []
        
        rev = ratios.revenue_cagr_3y or 0.0
        eps = ratios.eps_cagr_3y or 0.0
        
        if rev > 0.15:
            score += 20
            exp.append(f"Excellent revenue growth ({(rev*100):.1f}% CAGR).")
        elif rev < 0.05:
            score -= 15
            exp.append(f"Sluggish revenue growth ({(rev*100):.1f}% CAGR).")
            
        if eps > 0.15:
            score += 20
            exp.append(f"Strong EPS growth ({(eps*100):.1f}% CAGR).")
        elif eps < 0.0:
            score -= 20
            exp.append("Negative historical EPS growth.")
            
        score = max(0, min(100, score))
        return ScoreCategory(score=score, explanation=" ".join(exp) if exp else "Moderate historical growth.")

    def _score_value(self, ratios: RatioMetrics) -> ScoreCategory:
        score = 50
        exp = []
        
        pe = ratios.pe_ratio
        if pe > 0 and pe < 15:
            score += 20
            exp.append(f"Attractive P/E ratio ({pe:.1f}).")
        elif pe > 30:
            score -= 20
            exp.append(f"High P/E ratio ({pe:.1f}) suggests premium valuation.")
            
        peg = ratios.peg_ratio
        if peg and peg > 0 and peg < 1.0:
            score += 20
            exp.append(f"Favorable PEG ratio ({peg:.2f}).")
        elif peg and peg > 2.0:
            score -= 15
            exp.append(f"High PEG ratio ({peg:.2f}).")
            
        ev_ebitda = ratios.ev_to_ebitda
        if ev_ebitda > 0 and ev_ebitda < 10:
            score += 10
            exp.append(f"Low EV/EBITDA ({ev_ebitda:.1f}).")
            
        score = max(0, min(100, score))
        return ScoreCategory(score=score, explanation=" ".join(exp) if exp else "Fairly valued relative to standard metrics.")

    def _score_risk(self, risk: RiskMetrics) -> ScoreCategory:
        score = 50
        exp = []
        
        if risk.beta < 0.8:
            score += 15
            exp.append(f"Low beta ({risk.beta:.2f}) indicates lower market sensitivity.")
        elif risk.beta > 1.3:
            score -= 15
            exp.append(f"High beta ({risk.beta:.2f}) indicates higher volatility than market.")
            
        if risk.max_drawdown > 0.4:
            score -= 20
            exp.append(f"Significant historical drawdown ({(risk.max_drawdown*100):.1f}%).")
            
        if risk.sharpe_ratio > 1.0:
            score += 20
            exp.append(f"Excellent risk-adjusted returns (Sharpe: {risk.sharpe_ratio:.2f}).")
            
        score = max(0, min(100, score))
        return ScoreCategory(score=score, explanation=" ".join(exp) if exp else "Average risk profile.")

    def compute(self, ratios: RatioMetrics, risk: RiskMetrics) -> CompanyScores:
        health = self._score_health(ratios)
        profit = self._score_profitability(ratios)
        growth = self._score_growth(ratios)
        value = self._score_value(ratios)
        risk_score = self._score_risk(risk)
        
        # Quality relies on Profitability + Health
        qual_val = int((health.score + profit.score) / 2)
        quality = ScoreCategory(score=qual_val, explanation="Aggregate of financial health and profitability consistency.")
        
        # Momentum (placeholder without price action metrics, usually derived from RSI/MACD)
        momentum = ScoreCategory(score=50, explanation="Momentum analysis requires near-term technicals.")
        
        overall_val = int(0.2*health.score + 0.2*profit.score + 0.2*growth.score + 0.2*value.score + 0.2*risk_score.score)
        
        exp = "Strong overall fundamentals." if overall_val > 70 else "Weak overall fundamentals." if overall_val < 40 else "Mixed overall fundamentals."
        overall = ScoreCategory(score=overall_val, explanation=exp)
        
        return CompanyScores(
            health_score=health,
            growth_score=growth,
            profitability_score=profit,
            value_score=value,
            risk_score=risk_score,
            quality_score=quality,
            momentum_score=momentum,
            overall_score=overall
        )
