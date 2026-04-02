import numpy as np

def prepare_input(duration, src_bytes, dst_bytes):
    return np.array([[duration, src_bytes, dst_bytes]])