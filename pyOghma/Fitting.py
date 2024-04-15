import os
import glob
import secrets
import json
import numpy as np 
import pandas as pd


class Fitting:

    def __init__(self):
        self.json_name = ''
        self.name = ''
        self.dest_dir = ''
        self.Fit_Config = Fit_Config()
        self.Duplitate = Duplicate()
        self.Vars = Vars()
        self.Rules = Rules()
        self.Fits = Fits()
    
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
        config_dir = os.path.join('*','*','*', self.json_name, file)
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
        with open(os.path.join(self.dest_dir,'sim.json'), "r") as j:
            data = json.load(j)

        data['fits'].update(self.json_format)


        with open(os.path.join(self.dest_dir,'sim.json'), "w") as j:
            j.write(json.dumps(data, indent=4))

        return

class Fit_Config(Fitting):
    
    def __init__(self):
        super(Fitting, self).__init__()
        self.json_name = 'fit_config'
        self.data = self.load_config('default')
        self.set_format()
    
    def set_simplexmul(self, multiplier):
        self.data['fit_simplexmul'] = multiplier
    
    def set_simplex_reset(self, reset):
        self.data['fit_simplex_reset'] = reset

class Duplicate(Fitting):
    
    def __init__(self):
        super(Fitting, self).__init__()
        self.json_name = 'duplicate'
        self.data = {}
        self.data['id'] = 'id' + str(secrets.token_hex(8))
        self.data['segments'] = 0
        self.set_format()
    
    def set_duplications(self, *duplications):
        self.segments = len(duplications)
        self.data['id'] = 'id' + str(secrets.token_hex(8))
        self.data = {'segments': self.segments}
        for idx, duplication in enumerate(duplications): 
            self.data.update({'segment' + str(idx): duplication.data})
        self.set_format()
   

class Dupe:

    def __init__(self, dest_dir, layer):
        self.layer = layer
        self.dest_dir = dest_dir
        self.json_name = 'duplicate'
        self.data = self.load_config('default')
        self.data['id'] = 'id' + str(secrets.token_hex(8))
        with open(os.path.join(self.dest_dir,'sim.json'), "r") as j:
            self.ob = json.load(j)
    
    def find_file(self, file):#pyOghma/Sim_Defaults/Fits/dulicate/default.json
        config_dir = os.path.join('*','Sim_Defaults','Fits', self.json_name, file)
        filename = glob.glob(config_dir)[0]
        self.loaded_filename = str(filename)
        return str(filename)

    def load_config(self, file):
        file = file + '.json'
        with open(self.find_file(file)) as j:
            return json.loads(j.read())
    
        
    def set_duplication(self, src, dest, multiplier='x'):
        json_src = src
        json_dest = dest
        #json_src = self.get_path_from_dict(self.ob, base_name=src)
        #json_dest = self.get_path_from_dict(self.ob, base_name=dest)
        self.data['human_src'] = json_src
        self.data['human_dest'] = json_dest
        self.data['multiplier'] = multiplier
        self.data['json_src'] = json_src
        self.data['json_dest'] = json_dest



class Vars(Fitting):

    def __init__(self):
        super(Fitting, self).__init__()
        self.json_name = 'vars'
        self.data = {}
        self.data['segments'] = 0
        self.set_format()
    
    def set_variables(self, *variables):
        self.segments = len(variables)
        self.data = {'segments': self.segments}
        for idx, var in enumerate(variables): 
            self.data.update({'segment' + str(idx): var.data})
        self.set_format()

    

class Variable:

    def __init__(self, dest_dir):
        self.dest_dir = dest_dir
        self.json_name = 'vars'
        self.data = self.load_config('default')
        self.data['id'] = 'id' + str(secrets.token_hex(8))
        with open(os.path.join(self.dest_dir,'sim.json'), "r") as j:
            self.ob = json.load(j)

    def find_file(self, file):
        config_dir = os.path.join('*','Sim_Defaults','Fits', self.json_name, file)
        filename = glob.glob(config_dir)[0]
        self.loaded_filename = str(filename)
        return str(filename)

    def load_config(self, file):
        file = file + '.json'
        with open(self.find_file(file)) as j:
            return json.loads(j.read())
        
    def get_path_from_dict(self, ob, base_path='', base_name='', path=''):
        if ob and base_name in list(ob.keys()):
            path = f"{base_path}{path}/{base_name}"
            return path
        elif not ob:
            pass
        else:
            for key, value in sorted(ob.items()):
                return self.get_path_from_dict(base_path, base_name, value, f'{path}/{key}')
    
    def set_variable(self, state=True, param='', min=0, max=100, log_fit=False):

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

    def __init__(self):
        super(Fitting, self).__init__()
        self.json_name = 'rules'
        self.data = {}
        self.data['segments'] = 0
        self.set_format()
    
    def set_Rules(self, *fitrules):
        self.segments = len(fitrules)
        self.data = {'segments': self.segments}
        for idx, fitrule in enumerate(fitrules): 
            self.data.update({'segment' + str(idx): fitrule.data})
        self.set_format()

class Rule:

    def __init__(self, dest_dir):
        self.dest_dir = dest_dir
        self.json_name = 'rules'
        self.data = self.load_config('default')
        self.data['id'] = 'id' + str(secrets.token_hex(8))
        with open(os.path.join(self.dest_dir,'sim.json'), "r") as j:
            self.ob = json.load(j)

    def find_file(self, file):
        config_dir = os.path.join('*','*','*', self.json_name, file)
        filename = glob.glob(config_dir)[0]
        self.loaded_filename = str(filename)
        return str(filename)

    def load_config(self, file):
        file = file + '.json'
        with open(self.find_file(file)) as j:
            return json.loads(j.read())
        
    def get_path_from_dict(self, ob, base_path='', base_name='', path=''):
        if ob and base_name in list(ob.keys()):
            path = f"{base_path}{path}/{base_name}"
            return path
        elif not ob:
            pass
        else:
            for key, value in sorted(ob.items()):
                return self.get_path_from_dict(base_path, base_name, value, f'{path}/{key}')
    
    def set_rule(self, state=True, param_x = '', param_y = '', funciton = ''):

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

    def __init__(self):
        super(Fitting, self).__init__()
        self.json_name = 'fits'
        self.data = {}
        self.data['data_sets'] = 0
        self.set_format()
    
    def set_datasets(self, *datasets):
        self.segments = len(datasets)
        self.data = {'data_sets': self.segments}
        for idx, dataset in enumerate(datasets): 
            self.data.update({'data_set' + str(idx): dataset.data})
        self.set_format()

class Dataset:

    def __init__(self, dest_dir, config='', import_config='', *fitpathces):
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

    def find_file(self, file):
        config_dir = os.path.join('*','*','*','*', self.json_name, file)
        filename = glob.glob(config_dir)[0]
        self.loaded_filename = str(filename)
        return str(filename)

    def load_config(self, file):
        file = file + '.json'
        with open(self.find_file(file)) as j:
            return json.loads(j.read())
    
    def set_local_duplicate(self):
        self.data['duplicate']['id'] = 'id' + str(secrets.token_hex(8))
        self.data['duplicate']['segments'] = 0


class FitPatch:

    def __init__(self):
        self.json_name = 'fit_patch'
        self.data = self.load_config('default')

    def find_file(self, file):
        config_dir = os.path.join('*','*','*','fits', self.json_name, file)
        filename = glob.glob(config_dir)[0]
        self.loaded_filename = str(filename)
        return str(filename)

    def load_config(self, file):
        file = file + '.json'
        with open(self.find_file(file)) as j:
            return json.loads(j.read())
    
    def set_patch(self, param, val):
        #param = self.get_path_from_dict(base_name=param)
        self.data['json_path'] = param
        self.data['human_path'] = param
        self.data['val'] = val

class Config:

    def __init__(self, dest_dir, fit_against='jv.dat'):
        self.dest_dir = dest_dir
        self.json_name = 'config'
        self.data = self.load_config('default')
        self.data['sim_data'] = fit_against
    
    def find_file(self, file):
        config_dir = os.path.join('*','*','*','*', self.json_name, file)
        filename = glob.glob(config_dir)[0]
        self.loaded_filename = str(filename)
        return str(filename)

    def load_config(self, file):
        file = file + '.json'
        with open(self.find_file(file)) as j:
            return json.loads(j.read())
    
    def set_fit_params(self, **kwargs):
        for kwarg in kwargs:
            if kwarg in self.data:
                self.data[kwarg.key()] = kwarg.value()

class ImportConfig:

    def __init__(self, dest_dir, import_dir='jv.dat', x_data='J (A/cm^2)', y_data = 'V (Voltage)'):
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
    
    #oghma_csv {"title":"Voltage - J","type":"xy","y_label":"Voltage","data_label":"J","y_units":"V","data_units":"A/m2","time ":nan,"Vexternal":nan,"x_len":1,"y_len":7,"z_len":1,"cols":"yd"}*
    def create_inp(self):
        #header = "#oghma_csv{\"title\":" +"\""+ self.data['import_title'] + "\",\"type\":\"xy\"" + ",\"y_label\":"  + "\"" + self.data['import_xlabel'] + "\",\"data_lable\":" + "\""+self.data['import_ylable']
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
    
    def set_import_params(self, **kwargs):
        for kwarg in kwargs:
            if kwarg in self.data:
                self.data[kwarg.key()] = kwarg.value()

    def find_file(self, file):
        config_dir = os.path.join('*','*','*','*', self.json_name, file)
        filename = glob.glob(config_dir)[0]
        self.loaded_filename = str(filename)
        return str(filename)

    def load_config(self, file):
        file = file + '.json'
        with open(self.find_file(file)) as j:
            return json.loads(j.read())


    
if __name__ == "__main__":

    B = Fitting('pm6_y6_default copy')
    B.Fit_Config.set_simplexmul(240)
    B.Fit_Config.update()
    B.Duplitate.update()
    B.Vars.update()
    B.Rules.update()
    B.Fits.update()
