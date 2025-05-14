"""
This module provides functionality for managing thermal configurations and simulations. 
It allows setting temperature, configuring thermal boundaries, defining mesh properties, 
and updating simulation data in JSON format for thermal analysis.
"""

import ujson as json
import os
from glob import glob
from importlib import resources


class Thermal:
    """
    Class to handle thermal configurations and operations.
    Attributes:
        json_name (str): The name of the JSON configuration.
        data (dict): The thermal configuration data.
        dest_dir (str): The destination directory for saving or loading data.
        temperature (float): The set temperature for the thermal configuration.
        json_format (dict): The formatted JSON data for updates.
    """
    def __init__(self) -> None:
        """
        Initialize the Thermal class.
        """
        self.json_name = 'thermal'
        self.data = self.load_config('default')
        self.set_format()
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
        config_dir = resources.as_file(
            resources.files("PyOghma.Sim_Defaults.Thermal.configs." + self.json_name).joinpath(file)).args[0]
        return config_dir

    def set_format(self) -> None:
        """
        Set the format of the JSON data.
        """
        self.json_format = {self.json_name: self.data}

    def update(self) -> None:
        """
        Update the JSON file with the current data.
        """
        with open(os.path.join(self.dest_dir,'sim.json'), 'r') as j:
            data = json.load(j)

        data.update(self.json_format)

        with open(os.path.join(self.dest_dir,'sim.json'), 'w') as j:
            j.write(json.dumps(data, indent=4))

        return

    def set_temperature(self, temperature: float) -> None:
        """
        Set the temperature for the thermal configuration.
        Args:
            temperature (float): The temperature to set.
        """
        self.temperature = temperature
        self.data['set_point'] = self.temperature
        self.data['thermal_boundary']['Ty0'] = self.temperature
        self.data['thermal_boundary']['Ty1'] = self.temperature
        self.data['thermal_boundary']['Tx0'] = self.temperature
        self.data['thermal_boundary']['Tx1'] = self.temperature
        self.data['thermal_boundary']['Tz0'] = self.temperature
        self.data['thermal_boundary']['Tz1'] = self.temperature
    
    def set_mesh(self, start: float, stop: float, points: int) -> None:
        """
        Set the mesh configuration for the thermal simulation.
        Args:
            start (float): The starting value of the mesh.
            stop (float): The stopping value of the mesh.
            points (int): The number of points in the mesh.
        """
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
    """
    Example usage of the Thermal class.
    """
    A = Thermal()
    A.set_temperature(273.0)
    A.update('sim/update.json')
