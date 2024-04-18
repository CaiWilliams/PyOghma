import os
import secrets
from glob import glob

import numpy as np
import ujson as json
import difflib


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
        self.Fit_Config.dest_dir = dest_dir
        self.Duplitate.dest_dir = dest_dir
        self.Vars.dest_dir = dest_dir
        self.Rules.dest_dir = dest_dir
        self.Fits.dest_dir = dest_dir

    def load_config(self, file):
        file = file + '.json'
        with open(self.find_file(file)) as j:
            return json.loads(j.read())

    def find_file(self, file):
        config_dir = os.path.join('*', '*', '*', self.json_name, file)
        filename = glob.glob(config_dir)[0]
        self.loaded_filename = str(filename)
        return str(filename)

    def set_format(self):
        match self.json_name:
            case 'fit_config':
                self.json_format = {self.json_name: self.data}
            case 'duplicate':
                self.json_format = {self.json_name: self.data}
            case 'vars':
                self.json_format = {self.json_name: self.data}
            case 'fits':
                self.json_format = {self.json_name: self.data}
            case _:
                self.json_format = {self.json_name: self.data}

    def update(self):
        with open(os.path.join(self.dest_dir, 'sim.json'), "r") as j:
            data = json.load(j)

        data['fits'].update(self.json_format)

        with open(os.path.join(self.dest_dir, 'sim.json'), "w") as j:
            j.write(json.dumps(data, indent=4))

        return


class ml_random(ml):
    def __init__(self):
        super(ml, self).__init__()
        self.json_name = 'duplicate'
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


class ML_input:
    def __init__(self, dest_dir):
        self.dest_dir = dest_dir
        self.json_name = 'ml_random'
        self.data = self.load_config('default')

    def find_file(self, file):
        config_dir = os.path.join('*', 'Sim_Defaults', 'Ml', self.json_name, file)
        filename = glob.glob(config_dir)[0]
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
        self.json_name = 'ml_sim'
        self.data = {}
        self.data['segments'] = 0
        self.data['id'] = 'id' + str(secrets.token_hex(8))
        self.set_format()

    def set_sim(self, patches, output_vectors):
        if len(patches) != len(output_vectors):
            raise ValueError("Number of patches does not match the number of output vectors")
        else:
            self.segments = len(patches)
        self.data['id'] = 'id' + str(secrets.token_hex(8))
        self.data = {'segments': self.segments}
        for idx in range(len(patches)):
            segment_data = {}
            segment_data['ml_sim_enabled'] = "True"
            segment_data['sim_name'] = str(secrets.token_hex(8))
            output_vectors[idx].set_name(segment_data['sim_name'])
            segment_data['ml_patch'] = patches[idx]
            segment_data['ml_output_vectors'] = output_vectors[idx]
            self.data.update({'segment' + str(idx): segment_data})
        self.set_format()
        return

class ml_sim_patch:
    def __init__(self, dest_dir):
        self.dest_dir = dest_dir
        self.json_name = 'ml_random'
        self.data = self.load_config('default')

    def find_file(self, file):
        config_dir = os.path.join('*', 'Sim_Defaults', 'Ml', self.json_name, file)
        filename = glob.glob(config_dir)[0]
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
        self.data['human_var'] = ""

        self.data['ml_patch_val'] = param_val

class ml_sim_output_vector:
    def __init__(self, dest_dir):
        self.dest_dir = dest_dir
        self.json_name = 'ml_output_vectors'
        self.data = self.load_config('default')

    def find_file(self, file):
        config_dir = os.path.join('*', 'Sim_Defaults', 'Ml', self.json_name, file)
        filename = glob.glob(config_dir)[0]
        self.loaded_filename = str(filename)
        return str(filename)

    def load_config(self, file):
        file = file + '.json'
        with open(self.find_file(file)) as j:
            return json.loads(j.read())

    def set_output_vector(self, state, file_name, vector_start, vector_end, vector_step, import_cofig):
        if state:
            self.data["ml_oputput_vector_item_enabled"] = "True"
        else:
            self.data["ml_oputput_vector_item_enabled"] = "False"

        self.data["file_name"] = file_name
        self.data["ml_token_name"] = "vec"

        vector = np.arange(vector_start, vector_end+vector_step, vector_step)
        vector_string = ""
        for v in vector:
            vector_string += str(v) + ","

        self.import_cofig = import_cofig
        self.data["import_cofig"] = import_cofig.data

    def set_name(self,name):
        self.import_cofig.set_name(name)
        self.data["import_cofig"] = self.import_cofig


class ml_sim_output_vector_import_cofig:
    def __init__(self, dest_dir):
        self.dest_dir = dest_dir
        self.json_name = 'import_config'
        self.data = self.load_config('default')

    def find_file(self, file):
        config_dir = os.path.join('*', 'Sim_Defaults', 'Ml', self.json_name, file)
        filename = glob.glob(config_dir)[0]
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
