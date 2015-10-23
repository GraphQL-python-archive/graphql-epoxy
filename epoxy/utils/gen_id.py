_prev_id = 0


def gen_id():
    global _prev_id

    _prev_id += 1
    next_id = _prev_id

    return next_id
