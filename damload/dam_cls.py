import numpy as np
from damload import side_prs as sp
from damload import buoyancy as buo
from scipy import interpolate
import matplotlib.pyplot as plt
import matplotlib as mpl
from typing import List

mpl.rcParams.update(mpl.rcParamsDefault)  # Reset RC
font = {'family': 'Yu Mincho',
        'size': 18}
mpl.rc('font', **font)


class Dam:
    """
    ダムの載荷を計算する。
    """

    def __init__(self, name, x: list, y: list, length: float, depth_up: float, depth_mud: float, loc_drain=None, k=0.14,
                 depth_down=0.0, w0=9.8, w_mud=10.0, ce=0.5):
        """
        堤体の断面形状等のパラメーターを設定する。
        座標の零点は堤体の上流端。
        ｘ と ｙ は上流側の堤体表面を決める点の座標。
        :param name: ダムの名前。
        :param depth_up: ダム直上流部における水位から基礎地盤までの水深。
        :param depth_down: ダム直下流部における水位から基礎地盤までの水深。
        :param depth_mud: 泥の深さ
        :param x: 水平方向 (上流端を0にする)
        :param y: 鉛直方向, 高さ (上流端を0にする)
        :param length: 堤体の上流端から下流端までの水平距離。
        :param loc_drain: 堤体の上流端から排水孔までの水平距離。
        :param k: 堤体の設計震度。
        :param w0: 水の単位体積重量（KN/m3）。
        :param w_mud: 泥土の水中単位体積重量(KN/m3)。
        :param ce: 泥圧係数(0.4~0.6)
        :return: None
        """
        self.mud = None
        self.sta_wat = None
        self.dyn_wat = None
        self.buoyancy = None
        self.water_pressure = None
        self.name = name
        self.w0 = w0
        self.w_mud = w_mud
        self.ce = ce
        self.x = np.array(x)
        self.y = np.array(y)
        self.length = length
        self.loc_drain = loc_drain
        self.dep_up = depth_up
        self.dep_down = depth_down
        self.dep_mud = depth_mud
        self.__slope = interpolate.interp1d(x=self.y, y=self.x)  # ダムと水の接触面での点のｘ座標をｙ座標から計算する。
        self.k = k

    def cal_load(self, load_names: List[str], num=100, offset=0.0, unit_converter=1.0, plot=True, write=True):
        """
        モジュールを呼び出し載荷を計算する。
        :param load_names: 計算したい載荷を指定する文字列のリスト、'Dynamic', 'Static', 'Mud' , 'Buoyancy' から選択する。
        :param num: 計算する点の数。
        :param offset: 結果を書き出すとき、実際のモデルにあうため、結果の第一列（座標）を補正する値。
        :param unit_converter: 結果を書き出すとき、単位換算のための乗数。
        :param plot: 計算結果を描き出すか否か。
        :param write: 計算結果を書き出すか否か。
        :return:
        """
        for i in load_names:
            if i == "Dynamic":
                self.__cal_dyn_water(num=num, offset=offset, unit_converter=unit_converter, plot=plot, write=write)
            elif i == "Static":
                self.__cal_static_wat(num=num, offset=offset, unit_converter=unit_converter, plot=plot, write=write)
            elif i == "Mud":
                self.__cal_mud(num=num, offset=offset, unit_converter=unit_converter, plot=plot, write=write)
            elif i == "Buoyancy":
                self.__cal_buoyancy(num=num, offset=offset, unit_converter=unit_converter, plot=plot, write=write)
            else:
                raise ValueError(
                    "'load_names' should be a str list which contains 'Dynamic', 'Static', 'Mud' or 'Buoyancy'.")

        # if "Static" and "Mud" in load_names:
        #     self.__side_syn(num=num, offset=offset, unit_converter=unit_converter, plot=plot, write=write)
        return self

    def __cal_dyn_water(self, num=100, offset=0.0, unit_converter=1.0, plot=True, write=True):
        """
        モジュールを呼び出し動水圧を計算する。
        """
        load_name = "Dynamic_Water_Pressure"
        x, y = self.__gen_side_sample(h=self.dep_up, num=num)
        pres = sp.dyn_w(x=x, y=y, h=self.dep_up, k=self.k, w=self.w0)
        self.dyn_wat = np.array([y, pres], dtype=float)
        if plot:
            _plot_side_load(pres=pres, y=y, h=self.dep_up, load_name=load_name, name=self.name)
        if write:
            _write_side_load(pres=pres, y=y, load_name=load_name, offset=offset, unit_conv=unit_converter,
                             name=self.name)
        return self

    def __cal_buoyancy(self, num=100, offset=0.0, unit_converter=1.0, plot=True, write=True):
        """
        モジュールを呼び出し揚圧力を計算する。
        """
        x = np.linspace(0, self.length, num)
        buoyancy_val = buo.buoyancy(hu=self.dep_up, hd=self.dep_down,
                                    length=self.length, loc_drain=self.loc_drain, w=self.w0)(x)
        self.buoyancy = np.array([x, buoyancy_val], dtype=float)
        if plot:
            self.__plot_buoyancy()
        if write:
            dat_out = self.buoyancy.copy()
            dat_out[0, :] = dat_out[0, :] + offset
            dat_out[1, :] = dat_out[1, :] * unit_converter
            np.savetxt(f"{self.name}_Buoyancy.csv", dat_out.T, fmt='%.5e', delimiter=",", header="Distance, Buoyancy",
                       comments="")
        return self

    def __plot_buoyancy(self):
        mpl.use('agg')
        fig, ax = plt.subplots(figsize=(8, 3), layout='tight')
        ax.plot(self.buoyancy[0], self.buoyancy[1])
        ax.invert_yaxis()
        ax.set_xlabel('Distance(m)')
        ax.set_ylabel('Buoyancy(KN/m2)')
        ax.set_title("Buoyancy")
        fig.savefig(f"{self.name}_Buoyancy.png", dpi=500)
        return self

    def __cal_static_wat(self, num=10, offset=0.0, unit_converter=1.0, plot=True, write=True):
        """
        モジュールを呼び出し静水圧を計算する。
        """
        load_name = "Static_Water_Pressure"
        _, y = self.__gen_side_sample(h=self.dep_up, num=num)
        p = sp.stat_w(y, self.dep_up)
        self.sta_wat = np.array([y, p], dtype=float)
        if plot:
            _plot_side_load(p, y, self.dep_up, load_name, name=self.name)
        if write:
            _write_side_load(pres=p, y=y, load_name=load_name, offset=offset, unit_conv=unit_converter, name=self.name)
        return self

    def __cal_mud(self, num=10, offset=0.0, unit_converter=1.0, plot=True, write=True):
        """
        モジュールを呼び出し泥圧を計算する。
        """
        load_name = ["Mud_Pressure_v", "Mud_Pressure_h"]
        x, y = self.__gen_side_sample(h=self.dep_mud, num=num)
        pres_v, pres_h = sp.mud(x, y, h=self.dep_mud, w=self.w_mud, ce=self.ce, mesh_size=1.0)
        pres_v = -pres_v
        self.mud = np.array([y, pres_v, pres_h], dtype=float)
        if plot:
            _plot_side_load(pres_v, y, self.dep_mud, load_name[0], name=self.name)
            _plot_side_load(pres_h, y, self.dep_mud, load_name[1], name=self.name)
        if write:
            _write_side_load(pres=pres_v, y=y, load_name=load_name[0], offset=offset, unit_conv=unit_converter,
                             name=self.name)
            _write_side_load(pres=pres_h, y=y, load_name=load_name[1], offset=offset, unit_conv=unit_converter,
                             name=self.name)
        return self

    def __gen_side_sample(self, h: float, num: int):
        """
        水や泥との接触面にサンプルの座標を生成させる。
        :param h: 水や泥の表面から地盤までの深さ
        :param num: サンプルの数
        :return: x, y 座標
        """
        y = np.linspace(self.y[0], h, num)
        x = self.__slope(y)
        return x, y

    def __side_syn(self, num=10, offset=0.0, unit_converter=1.0, plot=True, write=True):
        """水と泥の静的荷重を合成して出力します。"""
        load_name = "Water_and_Mud"

        _, y = self.__gen_side_sample(h=self.dep_up, num=num)
        wat_trend = interpolate.interp1d(x=self.sta_wat[0], y=self.sta_wat[1])
        mud_trend = interpolate.interp1d(x=self.mud[0], y=self.mud[1], bounds_error=False,
                                         fill_value=(self.mud[1][0], self.mud[1][-1]))
        p = wat_trend(y) + mud_trend(y)
        if plot:
            _plot_side_load(p, y, self.dep_up, load_name, name=self.name)
        if write:
            _write_side_load(pres=p, y=y, load_name=load_name, offset=offset, unit_conv=unit_converter, name=self.name)
        pass


# -----

def _plot_side_load(pres, y, h, load_name, name):
    mpl.use('agg')
    depth = h - y
    fig, ax = plt.subplots(figsize=(4.5, 6), layout='tight')
    ax.plot(pres, depth)
    ax.invert_yaxis()
    ax.invert_xaxis()
    ax.set_xlabel(f'{load_name} (KN/m2)')
    ax.set_ylabel('Depth (m)')
    fig.savefig(f"{name}_{load_name}.png", dpi=500)
    pass


def _write_side_load(pres, y, load_name, offset, unit_conv, name):
    dat_out = np.array([y, pres])
    dat_out[0, :] = dat_out[0, :] + offset
    dat_out[1, :] = dat_out[1, :] * unit_conv
    dat_out = dat_out.T
    dat_out = dat_out[dat_out[:, 0].argsort()]
    np.savetxt(f"{name}_{load_name}.csv", dat_out, fmt='%.5e', delimiter=",",
               header="Height, Pressure", comments="")
    pass
