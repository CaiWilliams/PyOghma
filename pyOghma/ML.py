import os
import secrets
from glob import glob

import numpy as np
import ujson as json


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

    def set_output_vector(self, state, param, param_val):


class ml_config(ml):
    def __init__(self):
        super(ml, self).__init__()
        self.json_name = 'ml_config'
        self.data = {}
        self.data = self.load_config('default')
        self.set_format()


class ml_networks(ml):
    def __init__(self):
        def __init__(self):
            super(ml, self).__init__()
            self.json_name = 'ml_sim'
            self.data = {}
            self.data['segments'] = 0
            self.data['id'] = 'id' + str(secrets.token_hex(8))
            self.set_format()


if __name__ == '__main__':
