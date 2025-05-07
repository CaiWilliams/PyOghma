import ujson as json
import os
import secrets
from glob import glob
from importlib import resources


class Optical:
    def __init__(self):
        self.json_name = ''
        self.name = ''

        self.Light = Light()
        self.LightSources = LightSources()
        self.LightSource = LightSource()
        self.LightIntensity = LightIntensity()
        self.Lasers = Lasers()
        self.dest_dir = ''

    def load_config(self, file):
        file = file + '.json'
        with open(self.find_file(file)) as j:
            return json.loads(j.read())

    def find_file(self, file):
        config_dir = resources.as_file(resources.files("PyOghma.Sim_Defaults.Optical.configs."+self.json_name).joinpath(file)).args[0]
        #config_dir = os.path.join('PyOghma','Sim_Defaults', 'Optical', 'configs', self.json_name, file)
        return config_dir

    def set_format(self):
        match self.json_name:
            case 'light':
                self.json_format = {self.json_name: self.light}
            case 'light_sources':
                match self.json_sub_heading:
                    case 'lights':
                        self.json_format = {self.json_name: self.data}
                    case '0':
                        self.json_format = {self.json_name: self.data}
            case 'lasers':
                self.json_format = {self.json_name: self.data}

    def update(self):
        with open(os.path.join(self.dest_dir,'sim.json'), 'r') as j:
            data = json.load(j)

        data['optical'].update(self.json_format)

        with open(os.path.join(self.dest_dir,'sim.json'), 'w') as j:
            j.write(json.dumps(data, indent=4))

        return


class Light(Optical):
    def __init__(self):
        super(Optical, self).__init__()
        self.json_name = 'light'
        self.light = self.load_config('default')
        self.set_format()

    def set_light_Intensity(self, suns):
        print('Setting light intensity to: ', suns)
        self.light['Psun'] = suns
        return


class LightIntensity(Optical):
    def __init__(self):
        super(Optical, self).__init__()
        self.json_name = 'light_sources'
        self.json_sub_heading = '0'
        self.data = {}
        self.set_format()

    def set_light_Intensity(self, suns):
        self.data['Psun'] = suns
        return

class LightSources(Optical):

    def __init__(self, *light_sources):
        super(Optical, self).__init__()
        self.json_name = 'light_sources'
        self.json_sub_heading = 'lights'
        self.segments = len(light_sources)
        self.data = {'lights':{'segments': self.segments}}
        for idx, light_source in enumerate(light_sources):
            self.data.update({'segment' + str(idx): light_source.light})
        self.set_format()

    def set_light_Intensity(self, suns):
        self.data['Psun'] = suns
        return

    def add_light_source(self, *light_source):
        self.segments = len(light_source)
        self.data['lights']['segments'] = self.segments
        for idx, light_source in enumerate(light_source):
            self.data['lights']['segment'+str(idx)] = light_source.light # {'segment' + str(idx): light_source.light})



class LightSource:

    def __init__(self):
        self.json_name = 'light_sources'
        self.json_sub_heading = 'lights'
        self.light = self.load_config('default')
        self.light['id'] = 'id' + str(secrets.token_hex(8))
        self.light['virtual_spectra']['id'] = 'id' + str(secrets.token_hex(8))

    def load_config(self, file):
        file = file + '.json'
        with open(self.find_file(file)) as j:
            return json.loads(j.read())

    def find_file(self, file):
        config_dir = resources.as_file(resources.files("PyOghma.Sim_Defaults.Optical.configs."+self.json_name).joinpath(file)).args[0]
        #config_dir = os.path.join('PyOghma','Sim_Defaults', 'Optical', 'configs', self.json_name, file)
        return config_dir
    # def find_file(self, file):
    #     config_dir = os.path.join('*', 'configs', self.json_name, file)
    #     filename = glob(config_dir)[0]
    #     self.loaded_filename = str(filename)
    #     return str(filename)

    # def load_config(self, file):
    #     file = file + '.json'
    #     with open(self.find_file(file)) as j:
    #         return json.loads(j.read())

    def set_light_spectra(self, spectra_name):
        self.light['virtual_spectra']['light_spectra']['segment0']['light_spectrum'] = spectra_name
        return


class Lasers(Optical):
    def __init__(self, *lasers):
        super(Optical, self).__init__()
        self.json_name = 'lasers'
        self.segments = len(lasers)
        self.data = {'segments': self.segments}
        for idx, laser in enumerate(lasers):
            self.data.update({'segment' + str(idx): {'name': laser.name, 'icon': laser.icon, 'config': laser.data}})
        self.set_format()


class Laser:
    def __init__(self):
        self.json_name = 'lasers'
        self.name = 'Green'
        self.icon = 'laser'
        self.data = self.load_config('default')

    def find_file(self, file):
        config_dir = os.path.join('*', 'Optical', 'configs', self.json_name, file)
        print(config_dir)
        filename = glob(config_dir)[0]
        self.loaded_filename = str(filename)
        return str(filename)

    def load_config(self, file):
        file = file + '.json'
        with open(self.find_file(file)) as j:
            return json.loads(j.read())


if __name__ == '__main__':
    B = LightSource()
    A = LightSources()
    A.set_light_Intensity(100)
    print(A.json_format)
    A.add_light_source(B)
    A.dest_dir ='/media/cai/Active/PycharmProjects/PyOghma/standard_device/'
    A.update()
    # A = Laser()
    # B = Lasers(A)
    # print(B.json_format)
    # B.update('sim/update.json')
    # A = LightSource()
    # A.set_light_spectra('AM1.5G')
    # B = LightSources(A)
    # print(B.json_format)
    # B.update('sim/update.json')
    # A = Light()
    # A.set_light_Intensity(0.5)
    # print(A.light)
    # A.update('sim/update.json')
