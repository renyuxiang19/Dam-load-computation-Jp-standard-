import damload

kamitsu = damload.Dam(name="Kamitsu", x=[0.0, 4.9, 4.9], y=[0.0, 20.0, 63.5], length=56.0, depth_up=58.5,
                      depth_down=0, depth_mud=25.0, loc_drain=None, k=0.14)
kamitsu.cal_load(load_names=["Static", "Mud"], num=100, offset=120.0, unit_converter=1000.0)
kamitsu.cal_load(load_names=["Buoyancy"], num=10, offset=-28.0, unit_converter=1000.0)
