"""
This module provides functionality for managing optical configurations and operations, including 
handling light sources, lasers, and light intensity settings. It supports loading, modifying, 
and saving configurations for simulations involving optical components.
"""

import ujson as json
import os
import secrets
from glob import glob
from importlib import resources


class Optical:
    """
    Main class to handle optical configurations and operations.
    Attributes:
        json_name (str): The name of the JSON configuration.
        name (str): The name of the optical instance.
        Light (Light): Instance of the Light class.
        LightSources (LightSources): Instance of the LightSources class.
        LightSource (LightSource): Instance of the LightSource class.
        LightIntensity (LightIntensity): Instance of the LightIntensity class.
        Lasers (Lasers): Instance of the Lasers class.
        dest_dir (str): The destination directory for saving or loading data.
    """
    def __init__(self) -> None:
        """
        Initialize the Optical class and its subcomponents.
        """
        self.json_name = ''
        self.name = ''

        self.Light = Light()
        self.LightSources = LightSources()
        self.LightSource = LightSource()
        self.LightIntensity = LightIntensity()
        self.Lasers = Lasers()
        self.dest_dir = ''

    def load_config(self, file: str) -> dict:
        """
        Load a configuration file.
        Args:
            file (str): The name of the configuration file.
        Returns:
            dict: The loaded JSON data.
        """
        file = file + '.json'
        with open(self.find_file(file)) as j:
            return json.loads(j.read())

    def find_file(self, file: str) -> str:
        """
        Find a file in the directory structure.
        Args:
            file (str): The name of the file to find.
        Returns:
            str: The path to the found file.
        """
        config_dir = resources.as_file(resources.files("PyOghma.Sim_Defaults.Optical.configs."+self.json_name).joinpath(file)).args[0]
        return config_dir

    def set_format(self) -> None:
        """
        Set the format of the JSON data based on the json_name.
        """
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

    def update(self) -> None:
        """
        Update the JSON file with the current data.
        """
        with open(os.path.join(self.dest_dir,'sim.json'), 'r') as j:
            data = json.load(j)

        data['optical'].update(self.json_format)

        with open(os.path.join(self.dest_dir,'sim.json'), 'w') as j:
            j.write(json.dumps(data, indent=4))

        return


class Light(Optical):
    """
    Class to handle light configurations.
    Inherits from:
        Optical
    Attributes:
        json_name (str): The name of the JSON configuration.
        light (dict): The light configuration data.
    """
    def __init__(self) -> None:
        """
        Initialize the Light class.
        """
        super(Optical, self).__init__()
        self.json_name = 'light'
        self.light = self.load_config('default')
        self.set_format()

    def set_light_Intensity(self, suns: float) -> None:
        """
        Set the light intensity.
        Args:
            suns (float): The light intensity in suns.
        """
        print('Setting light intensity to: ', suns)
        self.light['Psun'] = suns
        return


class LightIntensity(Optical):
    """
    Class to handle light intensity configurations.
    Inherits from:
        Optical
    Attributes:
        json_name (str): The name of the JSON configuration.
        json_sub_heading (str): The subheading for the JSON configuration.
        data (dict): The light intensity configuration data.
    """
    def __init__(self) -> None:
        """
        Initialize the LightIntensity class.
        """
        super(Optical, self).__init__()
        self.json_name = 'light_sources'
        self.json_sub_heading = '0'
        self.data = {}
        self.set_format()

    def set_light_Intensity(self, suns: float) -> None:
        """
        Set the light intensity.
        Args:
            suns (float): The light intensity in suns.
        """
        self.data['Psun'] = suns
        return


class LightSources(Optical):
    """
    Class to handle multiple light sources.
    Inherits from:
        Optical
    Attributes:
        json_name (str): The name of the JSON configuration.
        json_sub_heading (str): The subheading for the JSON configuration.
        segments (int): The number of light sources.
        data (dict): The light sources configuration data.
    """
    def __init__(self, *light_sources: object) -> None:
        """
        Initialize the LightSources class.
        Args:
            *light_sources: Variable-length list of light source objects.
        """
        super(Optical, self).__init__()
        self.json_name = 'light_sources'
        self.json_sub_heading = 'lights'
        self.segments = len(light_sources)
        self.data = {'lights':{'segments': self.segments}}
        for idx, light_source in enumerate(light_sources):
            self.data.update({'segment' + str(idx): light_source.light})
        self.set_format()

    def set_light_Intensity(self, suns: float) -> None:
        """
        Set the light intensity for all light sources.
        Args:
            suns (float): The light intensity in suns.
        """
        self.data['Psun'] = suns
        return

    def add_light_source(self, *light_source: object) -> None:
        """
        Add one or more light sources.
        Args:
            *light_source: Variable-length list of light source objects.
        """
        self.segments = len(light_source)
        self.data['lights']['segments'] = self.segments
        for idx, light_source in enumerate(light_source):
            self.data['lights']['segment'+str(idx)] = light_source.light


class LightSource:
    """
    Class to handle individual light source configurations.
    Attributes:
        json_name (str): The name of the JSON configuration.
        json_sub_heading (str): The subheading for the JSON configuration.
        light (dict): The light source configuration data.
    """
    def __init__(self) -> None:
        """
        Initialize the LightSource class.
        """
        self.json_name = 'light_sources'
        self.json_sub_heading = 'lights'
        self.light = self.load_config('default')
        self.light['id'] = 'id' + str(secrets.token_hex(8))
        self.light['virtual_spectra']['id'] = 'id' + str(secrets.token_hex(8))

    def load_config(self, file: str) -> dict:
        """
        Load a configuration file.
        Args:
            file (str): The name of the configuration file.
        Returns:
            dict: The loaded JSON data.
        """
        file = file + '.json'
        with open(self.find_file(file)) as j:
            return json.loads(j.read())

    def find_file(self, file: str) -> str:
        """
        Find a file in the directory structure.
        Args:
            file (str): The name of the file to find.
        Returns:
            str: The path to the found file.
        """
        config_dir = resources.as_file(resources.files("PyOghma.Sim_Defaults.Optical.configs."+self.json_name).joinpath(file)).args[0]
        return config_dir

    def set_light_spectra(self, spectra_name: str) -> None:
        """
        Set the light spectra for the light source.
        Args:
            spectra_name (str): The name of the light spectra.
        """
        self.light['virtual_spectra']['light_spectra']['segment0']['light_spectrum'] = spectra_name
        return


class Lasers(Optical):
    """
    Class to handle laser configurations.
    Inherits from:
        Optical
    Attributes:
        json_name (str): The name of the JSON configuration.
        segments (int): The number of lasers.
        data (dict): The laser configuration data.
    """
    def __init__(self, *lasers: object) -> None:
        """
        Initialize the Lasers class.
        Args:
            *lasers: Variable-length list of laser objects.
        """
        super(Optical, self).__init__()
        self.json_name = 'lasers'
        self.segments = len(lasers)
        self.data = {'segments': self.segments}
        for idx, laser in enumerate(lasers):
            self.data.update({'segment' + str(idx): {'name': laser.name, 'icon': laser.icon, 'config': laser.data}})
        self.set_format()


class Laser:
    """
    Class to handle individual laser configurations.
    Attributes:
        json_name (str): The name of the JSON configuration.
        name (str): The name of the laser.
        icon (str): The icon representing the laser.
        data (dict): The laser configuration data.
    """
    def __init__(self) -> None:
        """
        Initialize the Laser class.
        """
        self.json_name = 'lasers'
        self.name = 'Green'
        self.icon = 'laser'
        self.data = self.load_config('default')

    def find_file(self, file: str) -> str:
        """
        Find a file in the directory structure.
        Args:
            file (str): The name of the file to find.
        Returns:
            str: The path to the found file.
        """
        config_dir = os.path.join('*', 'Optical', 'configs', self.json_name, file)
        print(config_dir)
        filename = glob(config_dir)[0]
        self.loaded_filename = str(filename)
        return str(filename)

    def load_config(self, file: str) -> dict:
        """
        Load a configuration file.
        Args:
            file (str): The name of the configuration file.
        Returns:
            dict: The loaded JSON data.
        """
        file = file + '.json'
        with open(self.find_file(file)) as j:
            return json.loads(j.read())


if __name__ == '__main__':
    """
    Main execution block for testing the Optical class and its subcomponents.
    """
    B = LightSource()
    A = LightSources()
    A.set_light_Intensity(100)
    print(A.json_format)
    A.add_light_source(B)
    A.dest_dir ='/media/cai/Active/PycharmProjects/PyOghma/standard_device/'
    A.update()
