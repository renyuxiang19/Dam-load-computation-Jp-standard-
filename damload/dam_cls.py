import numpy as np
from damload import dyn_wat_prs as wat
from damload import buoyancy as buo
from scipy import interpolate
import matplotlib.pyplot as plt
import matplotlib as mpl


class Dam:
    """
    ダムの載荷を計算する。
    """

    def __init__(self, x: list, y: list, length: float, depth_up: float, loc_drain=None, k=1.5, depth_down=0.0):
        """
        堤体の断面形状を決めるパラメーターを設定する。
        座標の零点は堤体の上流端。
        ｘ と ｙ は上流側の堤体表面を決める点の座標
        :param depth_up: ダム直上流部における水位から基礎地盤までの水深。
        :param depth_down: ダム直下流部における水位から基礎地盤までの水深。
        :param x: 水平方向 (上流端を0にする)
        :param y: 鉛直方向, 高さ (上流端を0にする)
        :param length: 堤体の上流端から下流端までの水平距離。
        :param loc_drain: 堤体の上流端から排水孔までの水平距離。
        :param k: 堤体の設計震度。
        :return: None
        """
        self.buoyancy = None
        self.water_pressure = None
        self.w0 = 9.8  # 水の単位体積重量（KN/m3）
        self.x = np.array(x)
        self.y = np.array(y)
        self.length = length
        self.loc_drain = loc_drain
        self.dep = depth_up
        self.dep_down = depth_down
        self.__slope = interpolate.interp1d(x=self.y, y=self.x)
        self.k = k
        pass

    def cal_dyn_water(self, num=100, plot=False, write=False):
        """
        モジュールを呼び出し動水圧を計算する。
        :param num:　計算する点の数。
        :param plot:　計算結果を描き出すか否か。
        :param write:　計算結果を書き出すか否か。
        :return:
        """
        h = np.linspace(self.dep, self.y[0], num)
        x = self.__slope(h)
        slant = np.arctan(np.diff(x) / np.diff(h))  # 傾斜角度
        slant = np.append(slant, slant[-1])
        cm_val = wat.zanger_cm(slant)
        depth = self.dep - h
        self.water_pressure = np.array([depth, wat.zanger(cm=cm_val, dep=depth, h=self.dep, k=self.k, w=self.w0)])
        if plot:
            self.plot_dyn_wat()
        if write:
            np.savetxt("Dynamic_water_pressure.csv", self.water_pressure.T, fmt='%.4e', delimiter=",",
                       header="depth, pressure", comments="")
        return self

    def plot_dyn_wat(self):
        mpl.use('agg')
        fig, ax = plt.subplots(figsize=(5, 8), layout='tight')
        ax.plot(self.water_pressure[1], self.water_pressure[0])
        ax.invert_yaxis()
        ax.invert_xaxis()
        ax.set_xlabel('Dynamic_water_pressure(KN/m2)')
        ax.set_ylabel('Depth(m)')
        fig.savefig("Dynamic_water_pressure.png")
        return self

    def cal_buoyancy(self, num=100, plot=False, write=False):
        """
        モジュールを呼び出し揚圧力を計算する。
        :param num: 計算する点の数。
        :param plot: 計算結果を描き出すか否か。
        :param write: 計算結果を書き出すか否か。
        :return:
        """
        x = np.linspace(0, self.length, num)
        buoyancy_val = buo.buoyancy(hu=self.dep, hd=self.dep_down,
                                    length=self.length, loc_drain=self.loc_drain, w=self.w0)(x)
        self.buoyancy = np.array([x, buoyancy_val])
        if plot:
            self.plot_buoyancy()
        if write:
            np.savetxt("Buoyancy.csv", self.buoyancy.T, fmt='%.4e', delimiter=",", header="distance, pressure",
                       comments="")
        return self

    def plot_buoyancy(self):
        mpl.use('agg')
        fig, ax = plt.subplots(figsize=(12, 4), layout='tight')
        ax.plot(self.buoyancy[0], self.buoyancy[1])
        ax.invert_yaxis()
        ax.set_xlabel('Distance(m)')
        ax.set_ylabel('Buoyancy(KN/m2)')
        fig.savefig("Buoyancy.png")
        return self
