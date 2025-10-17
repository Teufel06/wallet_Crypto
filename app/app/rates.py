from __future__ import annotations
import time, threading
from dataclasses import dataclass
from typing import Optional, Callable
import requests

COINGECKO_URL = (
    "https://api.coingecko.com/api/v3/simple/price"
    "?ids=bitcoin,ethereum&vs_currencies=inr,usd"
)

@dataclass
class RateCache:
    btc_inr: Optional[float] = None
    eth_inr: Optional[float] = None
    usd_inr: Optional[float] = None
    updated_ts: Optional[float] = None

_CACHE = RateCache()

def get_all_rates(timeout: int = 8) -> RateCache:
    try:
        r = requests.get(COINGECKO_URL, timeout=timeout)
        r.raise_for_status()
        data = r.json()
        btc_inr = float(data["bitcoin"]["inr"])
        eth_inr = float(data["ethereum"]["inr"])
        btc_usd = float(data["bitcoin"]["usd"])
        usd_inr = btc_inr / btc_usd if btc_usd > 0 else None

        if btc_inr > 0: _CACHE.btc_inr = btc_inr
        if eth_inr > 0: _CACHE.eth_inr = eth_inr
        if usd_inr and usd_inr > 0: _CACHE.usd_inr = usd_inr
        _CACHE.updated_ts = time.time()
    except Exception:
        pass
    return _CACHE

def start_rate_poller(callback: Callable[[RateCache], None], interval_sec: int = 90):
    def _loop():
        while True:
            cache = get_all_rates()
            try:
                callback(cache)
            except Exception:
                pass
            time.sleep(interval_sec)
    t = threading.Thread(target=_loop, daemon=True)
    t.start()
    return t
