

from glob import glob
import ujson as json
import numpy as np
import difflib
import secrets
import copy
import os

from importlib import resources


class ml:
    def __init__(self):
        self.name = ""
        self.icon = "ml"
        self.ml_random = ml_random()
        self.ml_patch = ml_patch()
        self.duplicate = duplicate()
        self.ml_sim = ml_sim()
        self.ml_config = ml_config()
        self.ml_networks = ml_networks()
        return

    def propegate_dest_dir(self, dest_dir):
        self.dest_dir = dest_dir
        self.ml_random.dest_dir = dest_dir
        self.ml_patch.dest_dir = dest_dir
        self.duplicate.dest_dir = dest_dir
        self.ml_config.dest_dir = dest_dir
        self.ml_sim.dest_dir = dest_dir

    def load_config(self, file):
        file = file + '.json'
        with open(self.find_file(file)) as j:
            return json.loads(j.read())

    def find_file(self, file):
        config_dir = resources.as_file(
            resources.files("PyOghma.Sim_Defaults.Ml.configs" + self.json_name).joinpath(file)).args[0]
        return config_dir

    def set_format(self):
        match self.json_name:
            case 'ml_random':
                self.json_format = {self.json_name: self.data}
            case 'ml_patch':
                self.json_format = {self.json_name: self.data}
            case 'duplicate':
                self.json_format = {self.json_name: self.data}
            case 'ml_sims':
                self.json_format = {self.json_name: self.data}
            case 'ml_config':
                self.json_format = {self.json_name: self.data}
            case 'ml_networks':
                self.json_format = {self.json_name: self.data}
            case _:
                self.json_format = {self.json_name: self.data}

    def update(self):
        with open(os.path.join(self.dest_dir, 'sim.json'), "r") as j:
            data = json.load(j)

        data['ml']['segment0'].update(self.json_format)

        with open(os.path.join(self.dest_dir, 'sim.json'), "w") as j:
            j.write(json.dumps(data, indent=4))

        return


class ml_random(ml):
    def __init__(self):
        super(ml, self).__init__()
        self.json_name = 'ml_random'
        self.data = {}
        self.data['segments'] = 0
        self.set_format()

    def set_inputs(self, *inputs):
        self.segments = len(inputs)
        self.data['id'] = 'id' + str(secrets.token_hex(8))
        self.data = {'segments': self.segments}
        for idx, duplication in enumerate(inputs):
            self.data.update({'segment' + str(idx): duplication.data})
        self.set_format()


class ml_input:
    def __init__(self, dest_dir):
        self.dest_dir = dest_dir
        self.json_name = 'ml_random'
        self.data = self.load_config('default')

    def find_file(self, file):
        config_dir = os.path.join(os.getcwd(), 'pyOghma','Sim_Defaults', 'Ml', self.json_name, file)
        filename = glob(config_dir)[0]
        self.loaded_filename = str(filename)
        return str(filename)

    def load_config(self, file):
        file = file + '.json'
        with open(self.find_file(file)) as j:
            return json.loads(j.read())

    def set_input(self, state=True, param='', param_min=-1, param_max=1):
        if state:
            self.data['random_var_enabled'] = "True"
        else:
            self.data['random_var_enabled'] = "False"

        self.data['min'] = param_min
        self.data['max'] = param_max

        if param_max / param_min >= 100:
            self.data['random_distribution'] = 'log'
        else:
            self.data['random_distribution'] = 'linear'

        self.data['json_var'] = param
        self.data['human_var'] = ''


class ml_patch(ml):
    def __init__(self):
        super(ml, self).__init__()
        self.json_name = 'ml_patch'
        self.data = {}
        self.data['segments'] = 0
        self.set_format()


class duplicate(ml):
    def __init__(self):
        super(ml, self).__init__()
        self.json_name = 'duplicate'
        self.data = {}
        self.data['id'] = 'id' + str(secrets.token_hex(8))
        self.data['segments'] = 0
        self.set_format()


class ml_sim(ml):
    def __init__(self):
        super(ml, self).__init__()
        self.json_name = 'ml_sims'
        self.data = {}
        self.data['segments'] = 0
        self.data['id'] = 'id' + str(secrets.token_hex(8))
        self.set_format()

    def set_sim(self, Sims):
        self.data['id'] = 'id' + str(secrets.token_hex(8))
        self.data = {'segments': len(Sims)}
        sim_names = [str(secrets.token_hex(8)) for i in range(len(Sims))]
        for idx in range(len(Sims)):
            segment_data = {}
            segment_data['ml_sim_enabled'] = "True"
            segment_data['sim_name'] = sim_names[idx]

            patch = {'segments': len(Sims[idx][0])}
            for jdx in range(len(Sims[idx][0])):

                P = copy.deepcopy(Sims[idx][0][jdx])
                patch_segment_data = P.data
                patch.update({'segment' + str(jdx): patch_segment_data})
            segment_data['ml_patch'] = patch

            output_vector = {'segments': len(Sims[idx][1])}
            for jdx in range(len(Sims[idx][1])):
                OV = copy.deepcopy(Sims[idx][1][jdx])
                OV.set_name(sim_names[idx])
                output_segment_data = OV.data
                output_vector.update({'segment' + str(jdx): output_segment_data})

            segment_data['ml_output_vectors'] = output_vector
            segment_data['id'] = 'id' + str(secrets.token_hex(8))
            self.data.update({'segment' + str(idx): segment_data})

        self.set_format()
        return


class ml_sim_patch:
    def __init__(self, dest_dir):
        self.dest_dir = dest_dir
        self.json_name = 'ml_patch'
        self.data = self.load_config('default')

    def find_file(self, file):
        config_dir = os.path.join('*', 'Sim_Defaults', 'Ml','ml_sims', self.json_name, file)
        filename = glob(config_dir)[0]
        self.loaded_filename = str(filename)
        return str(filename)

    def load_config(self, file):
        file = file + '.json'
        with open(self.find_file(file)) as j:
            return json.loads(j.read())

    def set_patch(self, state, param, param_val):
        if state:
            self.data['ml_patch_enabled'] = "True"
        else:
            self.data['ml_patch_enabled'] = "False"

        self.data['json_var'] = param
        self.data['human_var'] = param

        self.data['ml_patch_val'] = "{:.5f}".format(param_val)


class ml_sim_output_vector:
    def __init__(self, dest_dir):
        self.dest_dir = dest_dir
        self.json_name = 'ml_output_vectors'
        self.data = self.load_config('default')

    def find_file(self, file):
        config_dir = os.path.join('*', 'Sim_Defaults', 'Ml','ml_sims', self.json_name, file)
        filename = glob(config_dir)[0]
        self.loaded_filename = str(filename)
        return str(filename)

    def load_config(self, file):
        file = file + '.json'
        with open(self.find_file(file)) as j:
            return json.loads(j.read())

    def set_output_vector(self, state, file_name, vector_start, vector_end, vector_step, import_config):
        import_config = copy.deepcopy(import_config)
        if state:
            self.data["ml_output_vector_item_enabled"] = "True"
        else:
            self.data["ml_output_vector_item_enabled"] = "False"

        self.data["file_name"] = file_name
        self.data["ml_token_name"] = "vec"

        vector = np.arange(vector_start, vector_end+vector_step, vector_step)
        vector_string = ""
        for v in vector:
            vector_string += "{:.6f}".format(v) + ","
        vector_string = vector_string[:-1]
        self.data["vectors"] = vector_string

        #self.import_config = import_config
        self.data["import_config"] = import_config.data
        self.data["id"] = "id" + str(secrets.token_hex(8))

    def set_name(self, name):
        self.data["import_config"]['import_file_path'] = os.path.join(self.dest_dir, 'train',name,self.data['file_name'])
        self.data["import_config"]['data_file'] = name + '_' + self.data['ml_token_name']+'.csv'
        #self.import_config.set_name(self.data['file_name'],name)
        #self.data["import_config"]["data_file"] = name +'_'+  self.data['ml_token_name'] + '.csv'#self.import_cofig.data


class ml_sim_output_vector_import_cofig:
    def __init__(self, dest_dir):
        self.dest_dir = dest_dir
        self.json_name = 'import_config'
        self.data = self.load_config('default')

    def find_file(self, file):
        config_dir = os.path.join('*', 'Sim_Defaults', 'Ml', 'ml_sims','ml_output_vectors',self.json_name, file)
        filename = glob(config_dir)[0]
        self.loaded_filename = str(filename)
        return str(filename)

    def load_config(self, file):
        file = file + '.json'
        with open(self.find_file(file)) as j:
            return json.loads(j.read())

    def set_import_cofig(self, import_dir='jv.dat', x_data='J (A/cm^2)', y_data = 'V (Voltage)', import_area=0.104, x_spin=0, data_spin=1):
        self.data['import_file_path'] = ''
        self.data['import_x_combo_pos'] = self.get_combo_pos(x_data)[0]
        self.data['import_data_combo_pos'] = self.get_combo_pos(y_data)[0]
        self.data['import_x_spin'] = x_spin
        self.data['import_data_spin'] = data_spin
        self.data['import_title'] = self.get_combo_pos(x_data)[1] + ' - ' + self.get_combo_pos(y_data)[1]
        self.data['import_xlable'] = self.get_combo_pos(x_data)[1]
        self.data['import_data_label'] = self.get_combo_pos(y_data)[1]
        self.data['import_area'] = import_area
        self.data['import_data_invert'] = "False"
        self.data['import_x_invert'] = "False"
        self.data['data_file'] = ''
        self.data['id'] = 'id' + str(secrets.token_hex(8))

    def set_name(self, file_name, sim_name):
        self.data['import_file_path'] = self.dest_dir + '/' + file_name
        self.data['data_file'] = sim_name + '_vec.csv'

    def get_combo_pos(self, x):
        x = x.lower().strip().replace(' ','')
        list_o = ['Wavelength (nm)', 'Wavelength (um)', 'Wavelength (cm)', 'Wavelenght (m)', 'Photonenergy (eV)', 'J (mA/cm2)', 'J (A/cm2)', 'J (A/m2)', 'IMPS Re(Z) (Am2/W)',
                'IMPS Im(Z) (Am2/W)', 'IMVS Re(Z) (Vm2/W)', 'IMVS Im(Z) (Vm2/W)', 'Amps (A)', 'Amps - no convert (A)', 'Voltage (V)', '-Voltage (V)', 'Voltage (mV)', 'Frequency (Hz)',
                'Angular frequency (Rads)', 'Resistance (Ohms)', 'Refactive index (au)', 'Absorption (m-1)', 'Absorption (cm-1)', 'Attenuation coefficient (au)', 'Time (s)', 'Suns (Suns)',
                'Intensity (um-1.Wm-2)', 'Intensity (nm-1.wm-2)', 'Charge density (m-3)', 'Capacitance (F cm-2)', 'Suns (percent)', 'Charge (C)', 'mA (mA)', 'Reflectance (au)']
        list = [i.lower().strip().replace(' ','') for i in list_o]
        match = difflib.get_close_matches(x, list)[0]
        idx = list.index(match)
        return idx, list_o[idx]


class ml_config(ml):
    def __init__(self):
        super(ml, self).__init__()
        self.json_name = 'ml_config'
        self.data = {}
        self.data = self.load_config('default')
        self.set_format()

    def set_config(self, num_archives, sim_per_archive):
        self.data['ml_number_of_archives'] = num_archives
        self.data['ml_sims_per_archive'] = sim_per_archive

    def find_file(self, file):
        config_dir = resources.as_file(
            resources.files("PyOghma.Sim_Defaults.Ml." + self.json_name).joinpath(file)).args[0]
        return config_dir


class ml_networks(ml):
    def __init__(self):
        super(ml, self).__init__()
        self.json_name = 'ml_sim'
        self.data = {}
        self.data['segments'] = 0
        self.data['id'] = 'id' + str(secrets.token_hex(8))
        self.set_format()


class ml_network:
    def __init__(self, name, state, inputs, outputs):
        self.data = {}
        self.data["icon"] = "neural_network"
        self.data["name"] = name
        if state:
            self.data["enabled"] = "True"
        else:
            self.data["enabled"] = "False"
        self.data["ml_network_inputs"] = inputs.data
        self.data["ml_network_outputs"] = outputs.data
        self.data['id'] = 'id' + str(secrets.token_hex(8))


class ml_network_input:
    def __init__(self, *ml_output_vectors):
        self.data = {}
        self.data["none"] = "none"
        self.segments = len(ml_output_vectors)
        for idx,vector in enumerate():
            segment_data = {}
            segment_data["ml_input_vector"] = vector.data["file_name"]
            self.data['segment'+str(idx)] = segment_data


class ml_network_output:
    def __init__(self, ml_output_vectors, params):
        self.data = {}
        self.data["none"] = "none"
        self.segments = len(ml_output_vectors)
        for idx,vector in enumerate(ml_output_vectors):
            segment_data = {}
            segment_data["ml_output_vector"] = vector.data["file_name"] + params[idx]
            self.data['segment'+str(idx)] = segment_data


if __name__ == '__main__':
    A = ml()
    dest = '/home/cai/PycharmProjects/PyOghma/ml_example2/'
    A.propegate_dest_dir(dest)
    A1 = ml_input(dest)
    A1.set_input(state=True, param='1', param_max=10, param_min=1)
    A2 = ml_input(dest)
    A2.set_input(state=True, param='2', param_max=20, param_min=2)
    A3 = ml_input(dest)
    A3.set_input(state=True, param='3', param_max=30, param_min=3)
    A.ml_random.set_inputs(A1, A2, A3)
    A.ml_random.update()