import numpy as np
from numpy.typing import NDArray
from scipy import interpolate

# Zanger式の傾斜角度-Cm曲線
expr_slant = np.array([90, 80, 70, 60, 50, 40, 30, 20, 10, 0], dtype=float)
expr_cm = np.array([0.025, 0.125, 0.225, 0.31, 0.4, 0.48, 0.55, 0.62, 0.67, 0.72], dtype=float)
zanger_cm = interpolate.interp1d(x=expr_slant, y=expr_cm)  # 傾斜角度からCmを計算する関数。


def zanger(cm: NDArray, dep: NDArray, h: float, k: float, w=9.8) -> NDArray:
    """
    Zangerの式により動水圧を計算する。
    cm: ダムの上流面の勾配による定数。
    w: 水の単位体積重量（KN/m3）
    dep: 水面から動水圧を求めようとす点までの水深 (m)。
    h: 水面から基礎地盤までの水深 (m)。
    k: 堤体の設計震度。
    :return: Zangerの式による動水圧。
    """
    dep_ratio = dep / h
    dep_ratio = dep_ratio * (2 - dep_ratio)
    dep_ratio = 0.5*(dep_ratio + np.sqrt(dep_ratio))
    c_val = cm * dep_ratio
    pd = c_val * w * k * h
    return pd
