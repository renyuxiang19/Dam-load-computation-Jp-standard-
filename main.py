import damload
example = damload.Dam(x=[0, 4.9, 4.9], y=[0, 20, 63.5], length=56, depth_up=63.5, loc_drain=None)
example.cal_dyn_water(plot=True, write=True, offset=143.5, multiplier=1000.0)
example.cal_buoyancy(plot=True, write=True, offset=-28.0, multiplier=1000.0)
