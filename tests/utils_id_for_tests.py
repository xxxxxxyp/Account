def gen_id_simple(prefix: str = "id") -> str:
    # deterministic simple id for tests
    import time
    return f"{prefix}_test_{int(time.time() * 1000) % 100000}"