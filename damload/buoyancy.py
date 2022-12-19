import numpy as np
from scipy import interpolate


def buoyancy(hu: float, hd: float, length: float, loc_drain=None, w=9.8, offset=1.1):
    """
    揚圧力を計算する。
    :param hu: 上流側の水深(m)
    :param hd: 下流側の水深(m)
    :param length: 堤体の底の長さ(m)
    :param loc_drain: 排水孔から上流側までの距離(m)
    :param w: 水の単位体積重量
    :param offset: 1 より大きい。
    :return: 上流側から求めようとする点まで距離による関数
    """
    pu = hu * w
    pd = hd * w
    if loc_drain is None:
        # 排水孔の効果が及ばない断面
        p_up = pd + 0.3333 * offset * (pu - pd)
        p_down = pd
        dis = np.array([0, length], dtype=float)
        pressure = np.array([p_up, p_down], dtype=float)
    else:
        # 排水孔の効果が及ぶ断面
        p_drain = pd + 0.2 * offset * (pu - pd)
        p_up = pu
        p_down = pd
        dis = np.array([0, loc_drain, length], dtype=float)
        pressure = np.array([p_up, p_drain, p_down], dtype=float)

    f = interpolate.interp1d(x=dis, y=pressure)
    return f
