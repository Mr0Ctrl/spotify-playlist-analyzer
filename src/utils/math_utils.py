def mm_to_inches(v: float) -> float:
    return v * 0.03937

def floor_by_steps(n: int, x: float) -> int:
    return int(x - (x % n))