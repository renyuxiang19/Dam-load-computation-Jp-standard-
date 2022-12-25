import numpy as np
from numpy.typing import NDArray
from scipy import interpolate


def cal_slant(x: NDArray, y: NDArray) -> NDArray:
    """傾斜角度を計算する"""
    diff_y = np.diff(y)
    diff_y[diff_y == 0] = 1e-18
    slant = np.arctan(np.diff(x) / diff_y)
    slant = np.append(slant, slant[-1])
    slant = np.rad2deg(slant)
    return slant


# Zanger式の傾斜角度-Cm曲線
expr_slant = np.array([90, 80, 70, 60, 50, 40, 30, 20, 10, 0], dtype=float)
expr_cm = np.array([0.025, 0.125, 0.225, 0.31, 0.4, 0.48, 0.55, 0.62, 0.67, 0.72], dtype=float)
zanger_cm = interpolate.interp1d(x=expr_slant, y=expr_cm)  # 傾斜角度からCmを計算する関数。


def zanger(cm: NDArray, dep: NDArray, h: float, k: float, w=9.8) -> NDArray:
    """
    Zangerの式により動水圧を計算する。
    cm: ダムの上流面の勾配による定数。
    w: 水の単位体積重量(KN/m3)
    dep: 水面から動水圧を求めようとす点までの水深 (m)。
    h: 水面から基礎地盤までの水深 (m)。
    k: 堤体の設計震度。
    :return: Zangerの式による動水圧。
    """
    dep_ratio = dep / h
    dep_ratio = dep_ratio * (2 - dep_ratio)
    dep_ratio = 0.5 * (dep_ratio + np.sqrt(dep_ratio))
    c_val = cm * dep_ratio
    pd = c_val * w * k * h
    return pd


def dyn_w(x, y, h, k, w=9.8):
    slant = cal_slant(x, y)
    cm_val = zanger_cm(slant)
    depth = h - y
    prs = zanger(cm=cm_val, dep=depth, h=h, k=k, w=w)
    return prs


def stat_w(y, h, w=9.8):
    """
    静水圧を計算する.
    :param y: 計算する点のｙ座標
    :param h: 水深
    :param w: 水の単位体積重量(KN/m3)
    :return:　静水圧(KN/m2)
    """
    depth = h - y
    prs = depth * w
    return prs


def mud(x, y, h, w=12.0, ce=0.5):
    """
    泥圧を計算する。
    :param ce: 泥圧係数(0.4~0.6)
    :param x:　計算する点のｘ座標
    :param y:　計算する点のｙ座標
    :param h:　泥の深さ
    :param w:　泥土の水中単位体積重量(KN/m3)
    :return: 接触面に対して垂直に作用する泥圧(KN/m2)
    """
    depth = h - y
    slant = cal_slant(x, y)
    slant = np.deg2rad(slant)
    pv = w * depth * np.sin(slant)
    ph = ce * w * depth * np.cos(slant)
    p = np.sqrt(pv**2 + ph**2)
    return p
