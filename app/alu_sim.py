import struct

def f2bits(x: float) -> int:
    return struct.unpack(">I", struct.pack(">f", float(x)))[0]

def bits2f(u: int) -> float:
    return struct.unpack(">f", struct.pack(">I", int(u) & 0xFFFFFFFF))[0]

def hex32(u: int) -> str:
    return f"0x{(int(u) & 0xFFFFFFFF):08X}"

def alu(a: float, b: float, op: str):
    a = float(a); b = float(b)
    if op == "add":
        y = a + b
    elif op == "sub":
        y = a - b
    elif op == "mul":
        y = a * b
    elif op == "div":
        y = a / b
    else:
        raise ValueError("op must be add/sub/mul/div")
    return float(y), f2bits(y)
