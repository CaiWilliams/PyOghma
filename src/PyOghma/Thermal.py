import ujson as json
import os
from glob import glob
from importlib import resources


class Thermal:
    def __init__(self):
        self.json_name = 'thermal'
        self.data = self.load_config('default')
        self.set_format()
        self.dest_dir = ''

    def load_config(self, file):
        file = file + '.json'
        with open(self.find_file(file)) as j:
            return json.loads(j.read())

    def find_file(self, file):
        config_dir = resources.as_file(
            resources.files("PyOghma.Sim_Defaults.Thermal.configs." + self.json_name).joinpath(file)).args[0]
        return config_dir

    def set_format(self):
        self.json_format = {self.json_name: self.data}

    def update(self):
        with open(os.path.join(self.dest_dir,'sim.json'), 'r') as j:
            data = json.load(j)

        data.update(self.json_format)

        with open(os.path.join(self.dest_dir,'sim.json'), 'w') as j:
            j.write(json.dumps(data, indent=4))

        return

    def set_temperature(self, temperature):
        self.temperature = temperature
        self.data['set_point'] = self.temperature
        self.data['thermal_boundary']['Ty0'] = self.temperature
        self.data['thermal_boundary']['Ty1'] = self.temperature
        self.data['thermal_boundary']['Tx0'] = self.temperature
        self.data['thermal_boundary']['Tx1'] = self.temperature
        self.data['thermal_boundary']['Tz0'] = self.temperature
        self.data['thermal_boundary']['Tz1'] = self.temperature
    
    def set_mesh(self, start, stop, points):
        self.data['mesh']['mesh_t']['enabled'] = 'True'
        self.data['mesh']['mesh_t']['auto'] = 'False'
        self.data['mesh']['mesh_t']['segments'] =  1
        segment0 = {}
        segment0['start'] = start
        segment0['stop'] = stop
        segment0['points'] = points
        segment0['mul'] = 1
        segment0['left_right'] = 'left'
        self.data['mesh']['mesh_t']['segment0'] = segment0

if __name__ == '__main__':
    A = Thermal()
    A.set_temperature(273.0)
    A.update('sim/update.json')
