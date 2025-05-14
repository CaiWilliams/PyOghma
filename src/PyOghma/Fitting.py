"""
This module provides functionality for managing fitting operations, including configurations, 
variables, rules, and datasets. It supports creating, modifying, and saving fitting parameters 
and settings, as well as handling data import and export for simulations.
"""
import os
import glob
import secrets
import json
import numpy as np 
import pandas as pd


class Fitting:
    """
    Main class to handle fitting configurations and operations.
    Attributes:
        json_name (str): The name of the JSON configuration.
        name (str): The name of the fitting instance.
        dest_dir (str): The destination directory for saving or loading data.
        Fit_Config (Fit_Config): Instance of the Fit_Config class.
        Duplitate (Duplicate): Instance of the Duplicate class.
        Vars (Vars): Instance of the Vars class.
        Rules (Rules): Instance of the Rules class.
        Fits (Fits): Instance of the Fits class.
    """
    def __init__(self) -> None:
        """
        Initialize the Fitting class and its subcomponents.
        """
        self.json_name = ''
        self.name = ''
        self.dest_dir = ''
        self.Fit_Config = Fit_Config()
        self.Duplitate = Duplicate()
        self.Vars = Vars()
        self.Rules = Rules()
        self.Fits = Fits()
    
    def propegate_dest_dir(self, dest_dir: str) -> None:
        """
        Propagate the destination directory to all subcomponents.
        Args:
            dest_dir (str): The destination directory.
        """
        self.dest_dir = dest_dir
        self.Fit_Config.dest_dir = dest_dir
        self.Duplitate.dest_dir = dest_dir
        self.Vars.dest_dir = dest_dir
        self.Rules.dest_dir = dest_dir
        self.Fits.dest_dir = dest_dir

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
        config_dir = os.path.join('*','*','*', self.json_name, file)
        filename = glob.glob(config_dir)[0]
        self.loaded_filename = str(filename)
        return str(filename)

    def set_format(self) -> None:
        """
        Set the format of the JSON data based on the json_name.
        """
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

    def update(self) -> None:
        """
        Update the JSON file with the current data.
        """
        with open(os.path.join(self.dest_dir,'sim.json'), "r") as j:
            data = json.load(j)

        data['fits'].update(self.json_format)


        with open(os.path.join(self.dest_dir,'sim.json'), "w") as j:
            j.write(json.dumps(data, indent=4))

        return

class Fit_Config(Fitting):
    """
    Class to handle the fit configuration.
    Inherits from:
        Fitting
    Attributes:
        json_name (str): The name of the JSON configuration.
        data (dict): The fit configuration data.
    """
    def __init__(self) -> None:
        """
        Initialize the Fit_Config class.
        """
        super(Fitting, self).__init__()
        self.json_name = 'fit_config'
        self.data = self.load_config('default')
        self.set_format()
    
    def set_simplexmul(self, multiplier: float) -> None:
        """
        Set the simplex multiplier.
        Args:
            multiplier (float): The simplex multiplier value.
        """
        self.data['fit_simplexmul'] = multiplier
    
    def set_simplex_reset(self, reset: bool) -> None:
        """
        Set the simplex reset value.
        Args:
            reset (bool): Whether to reset the simplex.
        """
        self.data['fit_simplex_reset'] = reset

class Duplicate(Fitting):
    """
    Class to handle duplication configurations.
    Inherits from:
        Fitting
    Attributes:
        json_name (str): The name of the JSON configuration.
        data (dict): The duplication configuration data.
    """
    def __init__(self) -> None:
        """
        Initialize the Duplicate class.
        """
        super(Fitting, self).__init__()
        self.json_name = 'duplicate'
        self.data = {}
        self.data['id'] = 'id' + str(secrets.token_hex(8))
        self.data['segments'] = 0
        self.set_format()
    
    def set_duplications(self, *duplications: object) -> None:
        """
        Set the duplications for the configuration.
        Args:
            *duplications: Variable-length list of duplication objects.
        """
        self.segments = len(duplications)
        self.data['id'] = 'id' + str(secrets.token_hex(8))
        self.data = {'segments': self.segments}
        for idx, duplication in enumerate(duplications): 
            self.data.update({'segment' + str(idx): duplication.data})
        self.set_format()
   

class Dupe:
    """
    Class to handle individual duplication operations.
    Attributes:
        layer (str): The layer to duplicate.
        dest_dir (str): The destination directory.
        json_name (str): The name of the JSON configuration.
        data (dict): The duplication data.
    """
    def __init__(self, dest_dir: str, layer: str) -> None:
        """
        Initialize the Dupe class.
        Args:
            dest_dir (str): The destination directory.
            layer (str): The layer to duplicate.
        """
        self.layer = layer
        self.dest_dir = dest_dir
        self.json_name = 'duplicate'
        self.data = self.load_config('default')
        self.data['id'] = 'id' + str(secrets.token_hex(8))
        with open(os.path.join(self.dest_dir,'sim.json'), "r") as j:
            self.ob = json.load(j)
    
    def find_file(self, file: str) -> str:
        """
        Find a file in the directory structure.
        Args:
            file (str): The name of the file to find.
        Returns:
            str: The path to the found file.
        """
        config_dir = os.path.join('*','Sim_Defaults','Fits', self.json_name, file)
        filename = glob.glob(config_dir)[0]
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
    
        
    def set_duplication(self, src: str, dest: str, multiplier: str = 'x') -> None:
        """
        Set the duplication parameters.
        Args:
            src (str): The source path.
            dest (str): The destination path.
            multiplier (str): The duplication multiplier.
        """
        json_src = src
        json_dest = dest
        self.data['human_src'] = json_src
        self.data['human_dest'] = json_dest
        self.data['multiplier'] = multiplier
        self.data['json_src'] = json_src
        self.data['json_dest'] = json_dest



class Vars(Fitting):
    """
    Class to handle variable configurations.
    Inherits from:
        Fitting
    Attributes:
        json_name (str): The name of the JSON configuration.
        data (dict): The variable configuration data.
    """
    def __init__(self) -> None:
        """
        Initialize the Vars class.
        """
        super(Fitting, self).__init__()
        self.json_name = 'vars'
        self.data = {}
        self.data['segments'] = 0
        self.set_format()
    
    def set_variables(self, *variables: object) -> None:
        """
        Set the variables for the configuration.
        Args:
            *variables: Variable-length list of variable objects.
        """
        self.segments = len(variables)
        self.data = {'segments': self.segments}
        for idx, var in enumerate(variables): 
            self.data.update({'segment' + str(idx): var.data})
        self.set_format()

    

class Variable:
    """
    Class to handle individual variable operations.
    Attributes:
        dest_dir (str): The destination directory.
        json_name (str): The name of the JSON configuration.
        data (dict): The variable data.
    """
    def __init__(self, dest_dir: str) -> None:
        """
        Initialize the Variable class.
        Args:
            dest_dir (str): The destination directory.
        """
        self.dest_dir = dest_dir
        self.json_name = 'vars'
        self.data = self.load_config('default')
        self.data['id'] = 'id' + str(secrets.token_hex(8))
        with open(os.path.join(self.dest_dir,'sim.json'), "r") as j:
            self.ob = json.load(j)

    def find_file(self, file: str) -> str:
        """
        Find a file in the directory structure.
        Args:
            file (str): The name of the file to find.
        Returns:
            str: The path to the found file.
        """
        config_dir = os.path.join('*','Sim_Defaults','Fits', self.json_name, file)
        filename = glob.glob(config_dir)[0]
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
        
    def get_path_from_dict(self, ob: dict, base_path: str = '', base_name: str = '', path: str = '') -> str:
        """
        Get the path from a dictionary based on the base name.
        Args:
            ob (dict): The dictionary object.
            base_path (str): The base path.
            base_name (str): The base name to search for.
            path (str): The current path.
        Returns:
            str: The constructed path.
        """
        if ob and base_name in list(ob.keys()):
            path = f"{base_path}{path}/{base_name}"
            return path
        elif not ob:
            pass
        else:
            for key, value in sorted(ob.items()):
                return self.get_path_from_dict(base_path, base_name, value, f'{path}/{key}')
    
    def set_variable(self, state: bool = True, param: str = '', min: float = 0, max: float = 100, log_fit: bool = False) -> None:
        """
        Set the variable parameters.
        Args:
            state (bool): Whether the variable is enabled.
            param (str): The parameter name.
            min (float): The minimum value.
            max (float): The maximum value.
            log_fit (bool): Whether to use logarithmic fitting.
        """
        if state:
            self.data['fit_var_enabled'] = 'True'
        else:
            self.data['fit_var_enabled'] = 'False'
            return
        
        var = param
        
        self.data['human_var'] = var
        self.data['json_var'] = var

        self.data['min'] =  min
        self.data['max'] = max

        if log_fit:
            self.data['log_fit'] = 'True'
        else:
            self.data['log_fit'] = 'False'
        

class Rules(Fitting):
    """
    Class to handle rule configurations.
    Inherits from:
        Fitting
    Attributes:
        json_name (str): The name of the JSON configuration.
        data (dict): The rule configuration data.
    """
    def __init__(self) -> None:
        """
        Initialize the Rules class.
        """
        super(Fitting, self).__init__()
        self.json_name = 'rules'
        self.data = {}
        self.data['segments'] = 0
        self.set_format()
    
    def set_Rules(self, *fitrules: object) -> None:
        """
        Set the rules for the configuration.
        Args:
            *fitrules: Variable-length list of rule objects.
        """
        self.segments = len(fitrules)
        self.data = {'segments': self.segments}
        for idx, fitrule in enumerate(fitrules): 
            self.data.update({'segment' + str(idx): fitrule.data})
        self.set_format()

class Rule:
    """
    Class to handle individual rule operations.
    Attributes:
        dest_dir (str): The destination directory.
        json_name (str): The name of the JSON configuration.
        data (dict): The rule data.
    """
    def __init__(self, dest_dir: str) -> None:
        """
        Initialize the Rule class.
        Args:
            dest_dir (str): The destination directory.
        """
        self.dest_dir = dest_dir
        self.json_name = 'rules'
        self.data = self.load_config('default')
        self.data['id'] = 'id' + str(secrets.token_hex(8))
        with open(os.path.join(self.dest_dir,'sim.json'), "r") as j:
            self.ob = json.load(j)

    def find_file(self, file: str) -> str:
        """
        Find a file in the directory structure.
        Args:
            file (str): The name of the file to find.
        Returns:
            str: The path to the found file.
        """
        config_dir = os.path.join('*','*','*', self.json_name, file)
        filename = glob.glob(config_dir)[0]
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
        
    def get_path_from_dict(self, ob: dict, base_path: str = '', base_name: str = '', path: str = '') -> str:
        """
        Get the path from a dictionary based on the base name.
        Args:
            ob (dict): The dictionary object.
            base_path (str): The base path.
            base_name (str): The base name to search for.
            path (str): The current path.
        Returns:
            str: The constructed path.
        """
        if ob and base_name in list(ob.keys()):
            path = f"{base_path}{path}/{base_name}"
            return path
        elif not ob:
            pass
        else:
            for key, value in sorted(ob.items()):
                return self.get_path_from_dict(base_path, base_name, value, f'{path}/{key}')
    
    def set_rule(self, state: bool = True, param_x: str = '', param_y: str = '', funciton: str = '') -> None:
        """
        Set the rule parameters.
        Args:
            state (bool): Whether the rule is enabled.
            param_x (str): The x parameter name.
            param_y (str): The y parameter name.
            funciton (str): The function to apply.
        """
        if state:
            self.data['fit_rule_enabled'] = 'True'
        else:
            self.data['fit_rule_enabled'] = 'False'
            return

        x = self.get_path_from_dict(base_name=param_x)
        y = self.get_path_from_dict(base_name=param_y)

        self.data['json_x'] = x
        self.data['json_y'] = y

        self.data['human_x'] = x
        self.data['human_y'] = y

        self.data['function'] = funciton
        

class Fits(Fitting):
    """
    Class to handle fit configurations.
    Inherits from:
        Fitting
    Attributes:
        json_name (str): The name of the JSON configuration.
        data (dict): The fit configuration data.
    """
    def __init__(self) -> None:
        """
        Initialize the Fits class.
        """
        super(Fitting, self).__init__()
        self.json_name = 'fits'
        self.data = {}
        self.data['data_sets'] = 0
        self.set_format()
    
    def set_datasets(self, *datasets: object) -> None:
        """
        Set the datasets for the configuration.
        Args:
            *datasets: Variable-length list of dataset objects.
        """
        self.segments = len(datasets)
        self.data = {'data_sets': self.segments}
        for idx, dataset in enumerate(datasets): 
            self.data.update({'data_set' + str(idx): dataset.data})
        self.set_format()

class Dataset:
    """
    Class to handle individual dataset operations.
    Attributes:
        dest_dir (str): The destination directory.
        json_name (str): The name of the JSON configuration.
        data (dict): The dataset data.
    """
    def __init__(self, dest_dir: str, config: object = '', import_config: object = '', *fitpathces: object) -> None:
        """
        Initialize the Dataset class.
        Args:
            dest_dir (str): The destination directory.
            config (str): The configuration data.
            import_config (str): The import configuration data.
            *fitpathces: Variable-length list of fit patches.
        """
        self.dest_dir = dest_dir
        self.json_name = 'fits'
        self.data = {}
        self.data['fit_patch'] = {'segments': len(fitpathces)}
        for idx, fitpatch in enumerate(fitpathces): 
            self.data['fit_patch'].update({'segment' + str(idx): fitpatch.data})
        self.data['duplicate'] = {}
        self.data['duplicate']['id'] = 'id' + str(secrets.token_hex(8))
        self.data['duplicate']['segments'] = 0
        self.data['config'] = config.data
        self.data['import_config'] = import_config.data
        self.data['id'] = 'id' + str(secrets.token_hex(8))
        with open(os.path.join(self.dest_dir,'sim.json'), "r") as j:
            self.ob = json.load(j)

    def find_file(self, file: str) -> str:
        """
        Find a file in the directory structure.
        Args:
            file (str): The name of the file to find.
        Returns:
            str: The path to the found file.
        """
        config_dir = os.path.join('*','*','*','*', self.json_name, file)
        filename = glob.glob(config_dir)[0]
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
    
    def set_local_duplicate(self) -> None:
        """
        Set the local duplicate parameters.
        """
        self.data['duplicate']['id'] = 'id' + str(secrets.token_hex(8))
        self.data['duplicate']['segments'] = 0


class FitPatch:
    """
    Class to handle individual fit patch operations.
    Attributes:
        json_name (str): The name of the JSON configuration.
        data (dict): The fit patch data.
    """
    def __init__(self) -> None:
        """
        Initialize the FitPatch class.
        """
        self.json_name = 'fit_patch'
        self.data = self.load_config('default')

    def find_file(self, file: str) -> str:
        """
        Find a file in the directory structure.
        Args:
            file (str): The name of the file to find.
        Returns:
            str: The path to the found file.
        """
        config_dir = os.path.join('*','*','*','fits', self.json_name, file)
        filename = glob.glob(config_dir)[0]
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
    
    def set_patch(self, param: str, val: str) -> None:
        """
        Set the patch parameters.
        Args:
            param (str): The parameter name.
            val (str): The value to set.
        """
        self.data['json_path'] = param
        self.data['human_path'] = param
        self.data['val'] = val

class Config:
    """
    Class to handle configuration operations.
    Attributes:
        dest_dir (str): The destination directory.
        json_name (str): The name of the JSON configuration.
        data (dict): The configuration data.
    """
    def __init__(self, dest_dir: str, fit_against: str = 'jv.dat') -> None:
        """
        Initialize the Config class.
        Args:
            dest_dir (str): The destination directory.
            fit_against (str): The file to fit against.
        """
        self.dest_dir = dest_dir
        self.json_name = 'config'
        self.data = self.load_config('default')
        self.data['sim_data'] = fit_against
    
    def find_file(self, file: str) -> str:
        """
        Find a file in the directory structure.
        Args:
            file (str): The name of the file to find.
        Returns:
            str: The path to the found file.
        """
        config_dir = os.path.join('*','*','*','*', self.json_name, file)
        filename = glob.glob(config_dir)[0]
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
    
    def set_fit_params(self, **kwargs: dict) -> None:
        """
        Set the fit parameters.
        Args:
            **kwargs: Keyword arguments for fit parameters.
        """
        for kwarg in kwargs:
            if kwarg in self.data:
                self.data[kwarg.key()] = kwarg.value()

class ImportConfig:
    """
    Class to handle import configuration operations.
    Attributes:
        dest_dir (str): The destination directory.
        json_name (str): The name of the JSON configuration.
        data (dict): The import configuration data.
    """
    def __init__(self, dest_dir: str, import_dir: str = 'jv.dat', x_data: str = 'J (A/cm^2)', y_data: str = 'V (Voltage)') -> None:
        """
        Initialize the ImportConfig class.
        Args:
            dest_dir (str): The destination directory.
            import_dir (str): The import directory.
            x_data (str): The x data label.
            y_data (str): The y data label.
        """
        self.dest_dir = dest_dir
        self.json_name = 'import_config'
        self.data = self.load_config('default')
        self.data['import_file_path'] = import_dir
        self.data['import_x_combo_pos'] = self.get_combo_pos(x_data)[0]
        self.data['import_data_combo_pos'] = self.get_combo_pos(y_data)[0]
        self.data['import_xlable'] = self.get_combo_pos(x_data)[1]
        self.data['import_data_label'] = self.get_combo_pos(y_data)[1]
        self.data['import_title'] = self.data['import_xlable'] + ' - ' + self.data['import_data_label']
        self.data['id'] = 'id' + str(secrets.token_hex(8))
        self.data['data_file'] = 'fit_data#' + str(secrets.token_hex(8)) + '.inp'
        self.create_inp()

    def get_combo_pos(self, x: str) -> tuple:
        """
        Get the combo position for a given label.
        Args:
            x (str): The label to search for.
        Returns:
            tuple: The index and label.
        """
        x = x.lower().strip().replace(' ','')
        list_o = ['Wavelength (nm)', 'Wavelength (um)', 'Wavelength (cm)', 'Wavelenght (m)', 'Photonenergy (eV)', 'J (mA/cm2)', 'J (A/cm2)', 'J (A/m2)', 'IMPS Re(Z) (Am2/W)', 
                'IMPS Im(Z) (Am2/W)', 'IMVS Re(Z) (Vm2/W)', 'IMVS Im(Z) (Vm2/W)', 'Amps (A)', 'Amps - no convert (A)', 'Voltage (V)', '-Voltage (V)', 'Voltage (mV)', 'Frequency (Hz)',
                'Angular frequency (Rads)', 'Resistance (Ohms)', 'Refactive index (au)', 'Absorption (m-1)', 'Absorption (cm-1)', 'Attenuation coefficient (au)', 'Time (s)', 'Suns (Suns)',
                'Intensity (um-1.Wm-2)', 'Intensity (nm-1.wm-2)', 'Charge density (m-3)', 'Capacitance (F cm-2)', 'Suns (percent)', 'Charge (C)', 'mA (mA)', 'Reflectance (au)']
        list = [i.lower().strip().replace(' ','') for i in list_o]
        match = difflib.get_close_matches(x, list)[0]
        idx = list.index(match)
        return idx, list_o[idx]
    
    def create_inp(self) -> None:
        """
        Create the input file for import.
        """
        oghma_csv = {}
        oghma_csv["title"] = self.data['import_title']
        oghma_csv["type"] = "xy"
        oghma_csv["y_label"] = self.data['import_xlable']
        oghma_csv["data_label"] = self.data['import_data_label']
        oghma_csv["y_units"] = self.data['import_xlable']
        oghma_csv["data_units"] = self.data['import_data_label']
        oghma_csv["time"] = np.nan
        oghma_csv["Vexternal"] = np.nan
        data = pd.read_csv(self.data['import_file_path'],sep=' ', index_col=None, header=None)
        data_raw = data.to_numpy()
        data_shape = np.shape(data_raw)
        oghma_csv["x_len"] = data_shape[1]-1
        oghma_csv["y_len"] = data_shape[0]
        oghma_csv["cols"] = "yd"
        dir = os.path.join(self.dest_dir, self.data['data_file'])
        head = '#oghma_csv'+ str(oghma_csv).replace('\'','"') +"*\n"

        with open(dir,'w') as f:
            f.write(head)
            data.to_csv(f, sep='\t', header=False, index=False)
    
    def set_import_params(self, **kwargs: dict) -> None:
        """
        Set the import parameters.
        Args:
            **kwargs: Keyword arguments for import parameters.
        """
        for kwarg in kwargs:
            if kwarg in self.data:
                self.data[kwarg.key()] = kwarg.value()

    def find_file(self, file: str) -> str:
        """
        Find a file in the directory structure.
        Args:
            file (str): The name of the file to find.
        Returns:
            str: The path to the found file.
        """
        config_dir = os.path.join('*','*','*','*', self.json_name, file)
        filename = glob.glob(config_dir)[0]
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


    
if __name__ == "__main__":
    """
    Main execution block for testing the Fitting class and its subcomponents.
    """
    B = Fitting('pm6_y6_default copy')
    B.Fit_Config.set_simplexmul(240)
    B.Fit_Config.update()
    B.Duplitate.update()
    B.Vars.update()
    B.Rules.update()
    B.Fits.update()
