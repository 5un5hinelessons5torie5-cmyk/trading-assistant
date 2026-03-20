from ..models.symbol import Symbol
from typing import Dict, Any, List, Optional

import time

def get_symbol_status(symbol_info: Symbol, market_tick: Dict[str, Any], session_info: Dict[str, Any]) -> str:
    # 1. Broker availability
    if not symbol_info.broker:
        return "blocked"

    # 2. Tick freshness (within 60 seconds)
    tick_time = market_tick.get("time", 0)
    current_time = time.time()
    if tick_time > 0 and (current_time - tick_time) > 60:
        return "blocked"

    # 3. Spread sanity
    if "bid" in market_tick and "ask" in market_tick:
        spread = market_tick["ask"] - market_tick["bid"]
        if symbol_info.spread_sanity_threshold > 0 and spread > symbol_info.spread_sanity_threshold:
            return "blocked"

    # 4. Session state
    if not session_info.get("is_open", True):
        return "blocked"

    # 5. Asset group rules (e.g., crypto research-only)
    if symbol_info.asset_group == "crypto" and symbol_info.status == "research_only":
        return "research_only"

    return symbol_info.status

def get_blocked_reason(symbol_info: Symbol, market_tick: Dict[str, Any], session_info: Dict[str, Any]) -> Optional[str]:
    if not symbol_info.broker:
        return "No broker assigned"

    tick_time = market_tick.get("time", 0)
    current_time = time.time()
    if tick_time > 0 and (current_time - tick_time) > 60:
        return f"Tick stale: {int(current_time - tick_time)}s old"

    if "bid" in market_tick and "ask" in market_tick:
        spread = market_tick["ask"] - market_tick["bid"]
        if symbol_info.spread_sanity_threshold > 0 and spread > symbol_info.spread_sanity_threshold:
            return f"Spread too high: {spread:.5f} > {symbol_info.spread_sanity_threshold:.5f}"

    if not session_info.get("is_open", True):
        return "Market session closed"

    if symbol_info.asset_group == "crypto" and symbol_info.status == "research_only":
        return "Asset group restricted to research"

    return symbol_info.blocked_reason
