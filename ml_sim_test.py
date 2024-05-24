from pyOghma import OghmaNano
from pyOghma.ML import ml_sim_output_vector, ml_sim_output_vector_import_cofig, ml_sim_patch

B = OghmaNano.OghmaNano()
dest = '/home/cai/PycharmProjects/PyOghma/ml_example2/'
B.ML.propegate_dest_dir(dest)

import_conf = ml_sim_output_vector_import_cofig(dest)
import_conf.set_import_cofig()


A1 = ml_sim_output_vector(dest)
A1.set_output_vector(state=True, file_name='jv.csv', vector_start=-0.3, vector_end=3, vector_step=0.25,
                     import_config=import_conf)

P1 = ml_sim_patch(dest)
P1.set_patch(state=True, param='optical.light.Psun', param_val=1)


A2 = ml_sim_output_vector(dest)
A2.set_output_vector(state=True, file_name='jv.csv', vector_start=-0.2, vector_end=2, vector_step=0.25,
                     import_config=import_conf)
P2 = ml_sim_patch(dest)
P2.set_patch(state=True, param='optical.light.Psun', param_val=2)

A3 = ml_sim_output_vector(dest)
A3.set_output_vector(state=True, file_name='jv.csv', vector_start=-0.1, vector_end=1, vector_step=0.25,
                     import_config=import_conf)

P3 = ml_sim_patch(dest)
P3.set_patch(state=True, param='optical.light.Psun', param_val=3)


Sims = [[[P1], [A1]], [[P2], [A2]], [[P3], [A3]]]

B.ML.ml_sim.set_sim(Sims)#patches, out_vecs)
B.ML.ml_sim.update()
