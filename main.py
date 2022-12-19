import damload

example = damload.Dam(x=[0, 10, 20], y=[0, 20, 50], length=50.0, depth_up=40.0, loc_drain=20.0)
example.cal_dyn_water(plot=True, write=True)
example.cal_buoyancy(plot=True, write=True)
