import os
import secrets
import ujson as json

class Epitaxy:
    """
    Class to handle the epitaxy configuration and data.
    Attributes:
        json_name (str): The name of the JSON configuration.
        name (str): The name of the epitaxy instance.
        dest_dir (str): The destination directory for saving or loading data.
    Methods:
        load_config(file):
            Load the configuration from a JSON file.
        find_file(file):
            Find the JSON file in the specified directory.
        set_format():
            Set the format of the JSON data based on the json_name.
        update():
            Update the JSON file with the current data.
        load_existing():
            Load the existing JSON data from the specified directory.
    """
    def __init__(self):
        """
        Initialize the Epitaxy class.
        Attributes:
            json_name (str): The name of the JSON configuration.
            name (str): The name of the epitaxy instance.
            dest_dir (str): The destination directory for saving or loading data.
        """
        self.json_name = ''
        self.name = ''
        self.dest_dir = ''

    def load_config(self, file):
        """
        Load the configuration from a JSON file.
        Args:
            file (str): The name of the JSON file to load.
        Returns:
            dict: The loaded JSON data.
        """ 
        file = file + '.json'
        with open(self.find_file(file)) as j:
            return json.loads(j.read())

    def find_file(self, file):
        """
        Find the JSON file in the specified directory.
        Args:
            file (str): The name of the JSON file to find.
        Returns:
            str: The path to the found JSON file.
        """
        config_dir = os.path.join('*', 'configs', self.json_name, file)
        filename = glob(config_dir)[0]
        self.loaded_filename = str(filename)
        return str(filename)

    def set_format(self):
        """
        Set the format of the JSON data based on the json_name.
        """
        match self.json_name:
            case 'light':
                self.json_format = {self.json_name: self.light}
            case 'light_sources':
                self.json_format = {self.json_name: {self.json_sub_heading: self.data}}
            case 'lasers':
                self.json_format = {self.json_name: self.data}

    def update(self):
        """
        Update the JSON file with the current data.
        Returns:
            None
        """
        with open(os.path.join(self.dest_dir,'sim.json'), 'w') as j:
            j.write(json.dumps(self.data, indent=4))
        return
    
    def load_existing(self):
        """
        Load the existing JSON data from the specified directory.
        Attributes:
            data (dict): The loaded JSON data.
        """
        with open(os.path.join(self.dest_dir,'sim.json'), 'r') as j:
            self.data = json.load(j)
        
        num_layers = self.data['epitaxy']['segments']
        for idx in range(num_layers):
            setattr(self, self.data['epitaxy']['segment'+str(idx)]['name'].lower().replace(':',''), Layer(self.data['epitaxy']['segment'+str(idx)]))
            #temp.append(getattr(self, self.data['epitaxy']['layer'+str(idx)]['name'].lower().replace(':','')))
        #print(temp)
            


class Layer(Epitaxy):
    """
    Class to handle the layer data and properties.
    Inherits from:
        Epitaxy
    Attributes:
        layer_data (dict): The data for the specific layer.
        name (str): The name of the layer.
        dos (DOS): An instance of the DOS class for managing density of states.
    Methods:
        thickness(dx):
            Set the thickness of the layer.
    """
    def __init__(self, layer):
        """
        Initialize the Layer class.
        Args:
            layer (dict): The layer data.
        Attributes:
            layer_data (dict): The data for the specific layer.
            name (str): The name of the layer.
            dos (DOS): An instance of the DOS class for managing density of states.
        """
        super(Epitaxy, self).__init__()
        self.layer_data = layer
        #print(self.layer_data.keys())
        self.name = self.layer_data['name']
        self.layer_data['id'] = 'id' + str(secrets.token_hex(8))
        self.dos = DOS()
        self.dos.set_dos(self.layer_data)

    
    def thickness(self,dx):
        """
        Set the thickness of the layer.
        Args:
            dx (float): The thickness of the layer.
        """
        self.layer_data['dx'] =  dx



class DOS:
    """
    Class to handle the density of states (DOS) data and properties.
    Attributes:
        dos_name (str): The name of the DOS configuration.
        data (dict): The DOS data for the layer.
    Methods:
        set_dos(layer_data):
            Set the DOS data for the layer.
        enable():
            Enable the DOS.
        disable():
            Disable the DOS.
        type(type):
            Set the type of DOS.
        shape(band, function, a=0, b=0, c=0):
            Set the shape of the DOS.
        apply_shape(dos, func, a, b, c, state='True'):
            Apply the shape function to the DOS data.
        mobility(carriers, mobility):
            Set the mobility for the specified carriers.
        free_states_density(carriers, density):
            Set the free states density for the specified carriers.
        trap_density(carriers, density):
            Set the trap density for the specified carriers.
        urbach_energy(carriers, energy):
            Set the Urbach energy for the specified carriers.
        trapping_rate(carriers, direction, rate):
            Set the trapping rate for the specified carriers and direction.
        Xi(xi):
            Set the electron affinity (Xi).
        Eg(eg):
            Set the bandgap energy (Eg).
        relative_permittivity(er):
            Set the relative permittivity.
        shape_bands(bands):
            Set the shape of the bands.
    """
    def __ini__(self):
        """
        Initialize the DOS class.
        Attributes:
            dos_name (str): The name of the DOS configuration.
        """
        self.dos_name = ''
    
    def set_dos(self, layer_data):
        """
        Set the DOS data for the layer.
        Args:
            layer_data (dict): The layer data.
        """
        self.data = layer_data['shape_dos']

    def enable(self):
        """
        Enable the DOS.
        """
        self.data['enabled'] = 'True'

    def disable(self):
        """
        Disable the DOS.
        """
        self.data['enabled'] = 'False'
    
    def type(self, type):
        """
        Set the type of DOS.
        Args:
            type (str): The type of DOS.
        """
        match type.lower():
            case 'exponential':
                self.data['dostype'] = type.lower()
            case 'complex':
                self.data['dostype'] = type.lower()
            case _:
                print('DOS Type Not Supported!')
    
    def shape(self, band, function, a=0, b=0, c=0):
        """
        Set the shape of the DOS.
        Args:
            band (str): The band type (e.g., 'homo', 'lumo', 'both').
            function(str): The function defining the DOS (e.g, 'exponentional', 'gaussian', 'powerlaw', 'lorentzian', 'custom').
            a (float): Function specific parameter.
            b (float): Function specific parameter.
            c (float): Function specific parameter.
        """
        match function.lower():
            case 'exponential':
                func = 'a*exp((E-Ec)/b)'
                state = 'True'
                self.type('complex')
            case 'gaussian':
                func = 'a*exp(-((c+(E-Ec))/(sqrt(2.0)*b*1.0))^2.0)'
                state = 'True'
                self.type('complex')
            case 'powerlaw':
                func = 'a*exp((E-Ec)/(b+(E-Ec)/c))'
                state = 'True'
                self.type('complex')
            case 'lorentzian':
                func = '((3.14*b)/2.0)*a*(1.0/3.1415926)*(0.5*b/((E-Ec+c)*(E-Ec+c)+(0.5*b)*(0.5*b)))'
                state = 'True'
                self.type('complex')
            case 'disable':
                func = ''
                state = 'False'
                self.type('complex')
            case 'custom':
                func = str(function)
                state = 'True'
                self.type('complex')
            case _:
                print('DOS Function Not Supported!')


        match band.lower():
            case 'homo':
                self.apply_shape(self.data['complex_homo'], func, a, b, c, state)
            case 'lumo':
                self.apply_shape(self.data['complex_lumo'], func, a, b, c, state)
            case  'both':
                self.apply_shape(self.data['complex_homo'], func, a, b, c, state)
                self.apply_shape(self.data['complex_lumo'], func, a, b, c, state)
            case _:
                print('Band Selection Not Supported!')

    def apply_shape(self, dos, func, a, b, c, state='True'):
        """
        Modifies the 'segment0' of the given data structure (dos) by applying a specified function 
        and its parameters, and optionally enabling or disabling the function.
        Args:
            dos (dict): A dictionary representing the data structure to be modified. 
                        It must contain a 'segment0' key.
            func (str): The name of the function to be applied.
            a (float): The first parameter for the function.
            b (float): The second parameter for the function.
            c (float): The third parameter for the function.
            state (str, optional): A string indicating whether the function is enabled. 
                                   Defaults to 'True'.
        Returns:
            None: This method modifies the input dictionary in place.
        """
        dos['segment0']['function'] = func
        dos['segment0']['function_enable'] = state
        dos['segment0']['function_a'] = a 
        dos['segment0']['function_b'] = b
        dos['segment0']['function_c'] = c

    def mobility(self, carriers, mobility):
        """
        Set the mobility for the specified carriers.
        Args:
            carriers (str): The type of carriers ('electrons', 'holes', 'both').
            mobility (float): The mobility value.
        """
        match carriers.lower():
            case 'electrons':
                self.data['mue_y'] = mobility
            case 'holes':
                self.data['muh_y'] = mobility
            case 'both':
                self.data['mue_y'] = mobility
                self.data['muh_y'] = mobility
            case _:
                print('Unsupported Carrier Type!')
    
    def free_states_density(self, carriers, density):
        """
        Set the free states density for the specified carriers.
        Args:
            carriers (str): The type of carriers ('electrons', 'holes', 'both').
            density (float): The density value.
        """
        match carriers.lower():
            case 'electrons':
                self.data['Nc'] = density
            case 'holes':
                self.data['Nv'] = density
            case 'both':
                self.data['Nc'] = density
                self.data['Nv'] = density
            case _:
                print('Unsupported Carrier Type!')
    
    def trap_density(self, carriers, density):
        """
        Set the trap density for the specified carriers.
        Args:
            carriers (str): The type of carriers ('electrons', 'holes', 'both').
            density (float): The density value.
        """
        match self.data['dostype']:
            case 'exponential':
                match carriers.lower():
                    case 'electrons':
                        self.data['Ntrape'] = density
                    case 'holes':
                        self.data['Ntraph'] = density
                    case 'both':
                        self.data['Ntrape'] = density
                        self.data['Ntraph'] = density
                    case _:
                        print('Carriers Selected Not Supported By Exponential DOS!')
            case 'complex':
                match carriers.lower():
                    case _:
                        print('Feature Has Not Been Developed!')
            case _:
                print('Feature Not Developed For DOS Shape!')
    
    def urbach_energy(self, carriers, energy):
        """
        Set the Urbach energy for the specified carriers.
        Args:
            carriers (str): The type of carriers ('electrons', 'holes', 'both').
            energy (float): The Urbach energy value.
        """
        match carriers.lower():
            case 'electrons':
                self.data['Etrape'] = energy
            case 'holes':
                self.data['Etraph'] = energy
            case 'both':
                self.data['Etrape'] = energy
                self.data['Etraph'] = energy
            case _:
                print('Unsupported Carrier Type!')
    
    def fe_to_te(self, rate):
        """
        Set the free-to-trap rate for electrons.
        Args:
            rate (float): The rate value.
        """
        self.data['srhsigman_e'] = rate

    def te_to_fh(self, rate):
        """
        Set the trap-to-free rate for electrons.
        Args:
            rate (float): The rate value.
        """
        self.data['srhsigmap_e'] = rate

    def th_to_fe(self, rate):
        """
        Set the trap-to-free rate for holes.
        Args:
            rate (float): The rate value.
        """
        self.data['srhsigman_h'] = rate

    def fh_to_th(self, rate):
        """
        Set the free-to-trap rate for holes.
        Args:
            rate (float): The rate value.
        """
        self.data['srhsigmap_h'] = rate
    
    def trapping_rate(self, carriers, direction, rate):
        """
        Set the trapping rate for the specified carriers and direction.
        Args:
            carriers (str): The type of carriers ('electrons', 'holes', 'both').
            direction (str): The direction of trapping ('free to trap', 'trap to free').
            rate (float): The trapping rate value.
        """
        match carriers.lower():
            case 'electrons':
                match direction.lower():
                    case 'free to trap':
                        self.fe_to_te(rate)
                    case 'trap to free':
                        self.te_to_fh(rate)
                    case _:
                        print('Direction Not Supported!')
            case 'holes':
                match direction.lower():
                    case 'free to trap':
                        self.fh_to_th(rate)
                    case 'trap to free':
                        self.th_to_fe(rate)
                    case _:
                        print('Direction Not Supported!')
            case 'both':
                match direction.lower():
                    case 'free to trap':
                        self.fe_to_te(rate)
                        self.fh_to_th(rate)
                    case 'trap to free':
                        self.te_to_fh(rate)
                        self.th_to_fe(rate)
                    case _:
                        print('Direction Not Supported!')
            case _:
                print('Carriers Not Supported!')
    
    def Xi(self, xi):
        """
        Set the electron affinity (Xi).
        Args:
            xi (float): The electron affinity value.
        """
        self.data['Xi'] = xi
    
    def Eg(self, eg):
        """
        Set the bandgap energy (Eg).
        Args:
            eg (float): The bandgap energy value.
        """
        self.data['Eg'] = eg
    
    def relative_permittivity(self, er):
        """
        Set the relative permittivity.
        Args:
            er (float): The relative permittivity value.
        """
        self.data['epsilonr'] = er
    
    def shape_bands(self, bands):
        """
        Set the shape of the bands.
        Args:
            bands (str): The band shape configuration.
        """
        self.data['srh_bands'] = bands




if __name__ == '__main__':

    A = Epitaxy()
    A.dest_dir = '/media/cai/Big/PycharmProjects/PyOghma/standard_device'
    A.load_existing()
    print(A.ito.layer_data['dx'])
    A.ito.thickness(100)
    A.ito.dos.enable()
    A.ito.dos.mobility('both',1e-24)
    A.update()
