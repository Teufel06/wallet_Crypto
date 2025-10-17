from __future__ import annotations
from dataclasses import dataclass
from .alu_sim import alu

@dataclass
class Wallet:
    inr: float = 0.0
    btc: float = 0.0
    eth: float = 0.0
    usd: float = 0.0

    def deposit_inr(self, amt: float):
        self.inr, _ = alu(self.inr, amt, "add")

    def withdraw_inr(self, amt: float):
        self.inr, _ = alu(self.inr, amt, "sub")

    def inr_to_currency(self, currency: str, amount_inr: float, rate_inr_per_unit: float):
        if amount_inr <= 0 or amount_inr > self.inr:
            raise ValueError("Invalid INR amount.")
        if rate_inr_per_unit <= 0:
            raise ValueError("Invalid rate.")
        units, _ = alu(amount_inr, 1.0 / rate_inr_per_unit, "mul")
        self.inr, _ = alu(self.inr, amount_inr, "sub")
        if currency == "BTC": self.btc, _ = alu(self.btc, units, "add")
        elif currency == "ETH": self.eth, _ = alu(self.eth, units, "add")
        elif currency == "USD": self.usd, _ = alu(self.usd, units, "add")
        else: raise ValueError("Unsupported currency.")

    def currency_to_inr(self, currency: str, amount_units: float, rate_inr_per_unit: float):
        if amount_units <= 0:
            raise ValueError("Invalid currency amount.")
        if rate_inr_per_unit <= 0:
            raise ValueError("Invalid rate.")
        inr_val, _ = alu(amount_units, rate_inr_per_unit, "mul")
        if currency == "BTC":
            if amount_units > self.btc: raise ValueError("Insufficient BTC.")
            self.btc, _ = alu(self.btc, amount_units, "sub")
        elif currency == "ETH":
            if amount_units > self.eth: raise ValueError("Insufficient ETH.")
            self.eth, _ = alu(self.eth, amount_units, "sub")
        elif currency == "USD":
            if amount_units > self.usd: raise ValueError("Insufficient USD.")
            self.usd, _ = alu(self.usd, amount_units, "sub")
        else: raise ValueError("Unsupported currency.")
        self.inr, _ = alu(self.inr, inr_val, "add")
