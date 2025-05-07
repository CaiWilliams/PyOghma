import PyOghma as og
#from pyOghma.ML import ml_input

B = og.OghmaNano()
B.dest_dir ='/media/cai/Active/PycharmProjects/PyOghma/standard_device/'
B.propagate_dest_dir()

# dest = '/home/cai/PycharmProjects/PyOghma/ml_example2/'
# B.ML.propegate_dest_dir(dest)
# A1 = ml_input(dest)
# A1.set_input(state=True, param='5', param_max=10, param_min=1)
# A2 = ml_input(dest)
# A2.set_input(state=True, param='6', param_max=20, param_min=2)
# A3 = ml_input(dest)
# A3.set_input(state=True, param='7', param_max=30, param_min=3)
# B.ML.ml_random.set_inputs(A1, A2, A3)
# B.ML.ml_random.update()
B.Optical.LightSources.set_light_Intensity(1000)
A = og.Optical.LightSource()
B.Optical.LightSources.add_light_source(A)
B.Optical.LightSources.update()