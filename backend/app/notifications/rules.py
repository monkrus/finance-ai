from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class RulesEngine:
    def __init__(self):
        self.operators = {
            ">": lambda a, b: a > b,
            "<": lambda a, b: a < b,
            ">=": lambda a, b: a >= b,
            "<=": lambda a, b: a <= b,
            "==": lambda a, b: a == b,
            "!=": lambda a, b: a != b,
        }

    def _resolve_target(self, payload: Dict[str, Any], target: str) -> Any:
        """
        Resolves dot-notated targets (e.g. 'AAPL.price' or 'portfolio.total_loss') 
        from the flat/nested payload dictionary.
        """
        parts = target.split('.')
        current = payload
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        return current

    def _evaluate_node(self, node: Dict[str, Any], payload: Dict[str, Any]) -> bool:
        if "AND" in node:
            return all(self._evaluate_node(child, payload) for child in node["AND"])
            
        if "OR" in node:
            return any(self._evaluate_node(child, payload) for child in node["OR"])
            
        target = node.get("target")
        operator = node.get("operator")
        value = node.get("value")
        
        if not target or not operator or value is None:
            return False
            
        actual_value = self._resolve_target(payload, target)
        if actual_value is None:
            return False
            
        if operator not in self.operators:
            logger.warning(f"Unsupported operator: {operator}")
            return False
            
        try:
            # Type casting for comparison
            if isinstance(value, (int, float)) and isinstance(actual_value, str):
                actual_value = float(actual_value)
            
            return self.operators[operator](actual_value, value)
        except Exception as e:
            logger.error(f"Rule evaluation error: {e}")
            return False

    def evaluate(self, condition_json: Dict[str, Any], payload: Dict[str, Any]) -> bool:
        """
        Evaluates a complete rule condition JSON against the provided payload.
        """
        if not condition_json:
            return False
            
        try:
            return self._evaluate_node(condition_json, payload)
        except Exception as e:
            logger.error(f"Failed to evaluate rule: {e}")
            return False
