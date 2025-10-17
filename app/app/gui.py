from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox
from .alu_sim import alu, f2bits, hex32
from .wallet_core import Wallet
from .rates import get_all_rates, start_rate_poller, RateCache

PAD = 10

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Odil's Multi-Currency Wallet — IEEE-754 ALU")
        self.geometry("980x640")
        self.minsize(940, 580)

        self.wallet = Wallet()
        self.rates = get_all_rates()

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=PAD, pady=PAD)

        self.frame_alu = ttk.Frame(nb, padding=PAD)
        self.frame_wallet = ttk.Frame(nb, padding=PAD)
        nb.add(self.frame_alu, text="ALU Simulator")
        nb.add(self.frame_wallet, text="Wallet (BTC / ETH / USD)")

        self._build_alu_tab()
        self._build_wallet_tab()
        start_rate_poller(self._update_rates, interval_sec=90)

    # ---------- ALU TAB ----------
    def _build_alu_tab(self):
        f = self.frame_alu
        ttk.Label(f, text="IEEE-754 Floating-Point ALU Simulator",
                  font=("Segoe UI", 14, "bold")).pack(anchor="w")
        ttk.Label(f, text="Enter arithmetic (e.g. 10.5 + 20.25, 30 * 4, 50 / 3):")\
            .pack(anchor="w", pady=(10, 2))
        self.expr_entry = ttk.Entry(f, width=56, font=("Consolas", 11))
        self.expr_entry.pack(anchor="w", pady=(0, 10))
        self.expr_entry.insert(0, "10.5 + 20.25")
        ttk.Button(f, text="Run ALU Operation", command=self._run_alu).pack(anchor="w")
        ttk.Separator(f, orient="horizontal").pack(fill="x", pady=(10, 10))
        self.out_text = tk.Text(f, height=18, font=("Consolas", 10))
        self.out_text.pack(fill="both", expand=True)
        self._log_alu("Enter expression and press Run.\n\n")

    def _log_alu(self, s: str):
        self.out_text.insert("end", s)
        self.out_text.see("end")

    def _run_alu(self):
        expr = self.expr_entry.get().strip()
        try:
            if "+" in expr:
                parts = expr.split("+"); op="add"; sym="+"
            elif "-" in expr:
                parts = expr.split("-"); op="sub"; sym="-"
            elif "*" in expr:
                parts = expr.split("*"); op="mul"; sym="*"
            elif "/" in expr:
                parts = expr.split("/"); op="div"; sym="/"
            else:
                raise ValueError("Expression must contain +, -, * or /")
            if len(parts)!=2: raise ValueError("Only two operands supported")
            a=float(parts[0].strip()); b=float(parts[1].strip())
            y,ybits=alu(a,b,op)
            sign=(ybits>>31)&1; exp=(ybits>>23)&0xFF; mant=ybits&0x7FFFFF
            self._log_alu(f"{a} {sym} {b} = {y:.8f} bits={hex32(ybits)}\n"
                          f"   Sign:{sign} Exponent:{exp:08b} (dec {exp}->bias {exp-127:+d}) "
                          f"Mantissa:{mant:023b}\n\n")
        except Exception as e:
            self._log_alu(f"Error:{e}\n")

    # ---------- WALLET TAB ----------
    def _build_wallet_tab(self):
        f=self.frame_wallet
        ttk.Label(f,text="Your Wallet",font=("Segoe UI",14,"bold")).pack(anchor="w")
        self.rate_label=ttk.Label(f,text="Fetching live rates...",font=("Segoe UI",10))
        self.rate_label.pack(anchor="w",pady=(0,PAD))
        ttk.Label(f,text="Amount (INR or Currency units):").pack(anchor="w")
        self.amount_entry=ttk.Entry(f,width=22);self.amount_entry.pack(anchor="w",pady=(0,PAD))
        ttk.Button(f,text="Deposit INR",command=self._deposit_inr).pack(anchor="w")
        ttk.Button(f,text="Withdraw INR",command=self._withdraw_inr).pack(anchor="w",pady=(5,5))
        ttk.Separator(f,orient="horizontal").pack(fill="x",pady=PAD)
        ttk.Label(f,text="Convert Between INR and Currencies:").pack(anchor="w")
        self.currency_choice=tk.StringVar(value="BTC")
        ttk.Combobox(f,textvariable=self.currency_choice,values=["BTC","ETH","USD"],
                     state="readonly",width=6).pack(anchor="w")
        ttk.Button(f,text="Convert INR → Currency",command=self._convert_inr_to_cur).pack(anchor="w",pady=(5,2))
        ttk.Button(f,text="Convert Currency → INR",command=self._convert_cur_to_inr).pack(anchor="w",pady=(2,5))
        ttk.Separator(f,orient="horizontal").pack(fill="x",pady=PAD)
        self.status=tk.Text(f,height=12,font=("Consolas",10))
        self.status.pack(fill="both",expand=True)
        self._update_balance_display()

    def _update_rates(self,cache:RateCache):
        self.rates=cache
        if not cache.btc_inr:
            self.rate_label.config(text="Rate fetch failed (offline).")
            return
        self.rate_label.config(text=(f"Rates (₹ per unit): BTC={cache.btc_inr:,.2f} | "
                                     f"ETH={cache.eth_inr:,.2f} | USD={cache.usd_inr:,.2f}"))

    def _get_amt(self): val=self.amount_entry.get().strip(); return float(val) if val else 0.0
    def _rate_for(self,cur:str): return {"BTC":self.rates.btc_inr,"ETH":self.rates.eth_inr,"USD":self.rates.usd_inr}.get(cur,0.0) or 0.0

    def _deposit_inr(self):
        try:self.wallet.deposit_inr(self._get_amt());self._update_balance_display()
        except Exception as e:messagebox.showerror("Deposit Error",str(e))
    def _withdraw_inr(self):
        try:self.wallet.withdraw_inr(self._get_amt());self._update_balance_display()
        except Exception as e:messagebox.showerror("Withdraw Error",str(e))
    def _convert_inr_to_cur(self):
        try:amt=self._get_amt();cur=self.currency_choice.get();rate=self._rate_for(cur)
        if rate<=0:raise ValueError("Rate unavailable");self.wallet.inr_to_currency(cur,amt,rate);self._update_balance_display()
        except Exception as e:messagebox.showerror("Convert Error",str(e))
    def _convert_cur_to_inr(self):
        try:amt=self._get_amt();cur=self.currency_choice.get();rate=self._rate_for(cur)
        if rate<=0:raise ValueError("Rate unavailable");self.wallet.currency_to_inr(cur,amt,rate);self._update_balance_display()
        except Exception as e:messagebox.showerror("Convert Error",str(e))
    def _update_balance_display(self):
        w=self.wallet
        self.status.delete("1.0","end")
        self.status.insert("end",f"INR: ₹{w.inr:,.2f}\nBTC: {w.btc:.8f}\nETH: {w.eth:.8f}\nUSD: {w.usd:.2f}\n")

def run_app(): App().mainloop()
