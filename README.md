# Wallet ALU GUI (Full Project)

Multi-file Python project that includes:

- IEEE-754 single-precision ALU simulator (with Sign/Exponent/Mantissa breakdown)
- GUI (Tkinter) with two tabs: ALU Simulator and Wallet
- Wallet supports INR, BTC, ETH, USD with partial conversions both ways
- Live rates via CoinGecko (BTC, ETH) with derived USD→INR; graceful polling

## Install & Run
```bash
pip install -r requirements.txt
python main.py
