import damload

kamitsu = damload.Dam(name="Kamitsu", x=[0, 4.9, 4.9], y=[0, 20, 63.5], length=56.0, depth_up=58.5, depth_mud=5.0,
                      loc_drain=7.1, k=0.14)
kamitsu.cal_load(load_names=["Dynamic", "Static", "Mud"], offset=80.0, unit_converter=1000.0)
kamitsu.cal_load(load_names=["Buoyancy"], offset=-28.0, unit_converter=1000.0)
