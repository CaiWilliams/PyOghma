import os
import secrets
import ujson as json

class Epitaxy:
    """
    Handles the epitaxy configuration and data.

    Attributes:
        json_name (str): The name of the JSON configuration.
        name (str): The name of the epitaxy instance.
        dest_dir (str): The destination directory for saving or loading data.

    Methods:
        load_config(file: str) -> dict:
            Loads the configuration from a JSON file.
        find_file(file: str) -> str:
            Finds the JSON file in the specified directory.
        set_format() -> None:
            Sets the format of the JSON data based on the json_name.
        update() -> None:
            Updates the JSON file with the current data.
        load_existing() -> None:
            Loads the existing JSON data from the specified directory.
    """
    def __init__(self):
        """
        Initializes the Epitaxy class.

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
        Loads the configuration from a JSON file.

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
        Finds the JSON file in the specified directory.

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
        Sets the format of the JSON data based on the json_name.

        Returns:
            None
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
        Updates the JSON file with the current data.

        Returns:
            None
        """
        with open(os.path.join(self.dest_dir,'sim.json'), 'w') as j:
            j.write(json.dumps(self.data, indent=4))
        return
    
    def load_existing(self):
        """
        Loads the existing JSON data from the specified directory.

        Attributes:
            data (dict): The loaded JSON data.

        Returns:
            None
        """
        with open(os.path.join(self.dest_dir,'sim.json'), 'r') as j:
            self.data = json.load(j)
        
        num_layers = self.data['epitaxy']['segments']
        for idx in range(num_layers):
            setattr(self, self.data['epitaxy']['segment'+str(idx)]['name'].lower().replace(':',''), Layer(self.data['epitaxy']['segment'+str(idx)]))
            


class Layer(Epitaxy):
    """
    Handles the layer data and properties.

    Inherits:
        Epitaxy

    Attributes:
        layer_data (dict): The data for the specific layer.
        name (str): The name of the layer.
        dos (DOS): An instance of the DOS class for managing density of states.

    Methods:
        thickness(dx: float) -> None:
            Sets the thickness of the layer.
    """
    def __init__(self, layer):
        """
        Initializes the Layer class.

        Args:
            layer (dict): The layer data.

        Attributes:
            layer_data (dict): The data for the specific layer.
            name (str): The name of the layer.
            dos (DOS): An instance of the DOS class for managing density of states.
        """
        super(Epitaxy, self).__init__()
        self.layer_data = layer
        self.name = self.layer_data['name']
        self.layer_data['id'] = 'id' + str(secrets.token_hex(8))
        self.dos = DOS()
        self.dos.set_dos(self.layer_data)

    
    def thickness(self, dx):
        """
        Sets the thickness of the layer.

        Args:
            dx (float): The thickness of the layer.

        Returns:
            None
        """
        self.layer_data['dx'] =  dx



class DOS:
    """
    Handles the density of states (DOS) data and properties.

    Attributes:
        dos_name (str): The name of the DOS configuration.
        data (dict): The DOS data for the layer.

    Methods:
        set_dos(layer_data: dict) -> None:
            Sets the DOS data for the layer.
        enable() -> None:
            Enables the DOS.
        disable() -> None:
            Disables the DOS.
        type(type: str) -> None:
            Sets the type of DOS.
        shape(band: str, function: str, a: float = 0, b: float = 0, c: float = 0) -> None:
            Sets the shape of the DOS.
        apply_shape(dos: dict, func: str, a: float, b: float, c: float, state: str = 'True') -> None:
            Applies the shape function to the DOS data.
        mobility(carriers: str, mobility: float) -> None:
            Sets the mobility for the specified carriers.
        free_states_density(carriers: str, density: float) -> None:
            Sets the free states density for the specified carriers.
        trap_density(carriers: str, density: float) -> None:
            Sets the trap density for the specified carriers.
        urbach_energy(carriers: str, energy: float) -> None:
            Sets the Urbach energy for the specified carriers.
        trapping_rate(carriers: str, direction: str, rate: float) -> None:
            Sets the trapping rate for the specified carriers and direction.
        Xi(xi: float) -> None:
            Sets the electron affinity (Xi).
        Eg(eg: float) -> None:
            Sets the bandgap energy (Eg).
        relative_permittivity(er: float) -> None:
            Sets the relative permittivity.
        shape_bands(bands: str) -> None:
            Sets the shape of the bands.
    """
    def __ini__(self):
        """
        Initializes the DOS class.

        Attributes:
            dos_name (str): The name of the DOS configuration.
        """
        self.dos_name = ''
    
    def set_dos(self, layer_data):
        """
        Sets the DOS data for the layer.

        Args:
            layer_data (dict): The layer data.

        Returns:
            None
        """
        self.data = layer_data['shape_dos']

    def enable(self):
        """
        Enables the DOS.

        Returns:
            None
        """
        self.data['enabled'] = 'True'

    def disable(self):
        """
        Disables the DOS.

        Returns:
            None
        """
        self.data['enabled'] = 'False'
    
    def type(self, type):
        """
        Sets the type of DOS.

        Args:
            type (str): The type of DOS.

        Returns:
            None
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
        Sets the shape of the DOS.

        Args:
            band (str): The band type (e.g., 'homo', 'lumo', 'both').
            function (str): The function defining the DOS (e.g., 'exponential', 'gaussian', 'powerlaw', 'lorentzian', 'custom').
            a (float): Function-specific parameter.
            b (float): Function-specific parameter.
            c (float): Function-specific parameter.

        Returns:
            None
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
            func (str): The name of the function to be applied.
            a (float): The first parameter for the function.
            b (float): The second parameter for the function.
            c (float): The third parameter for the function.
            state (str, optional): A string indicating whether the function is enabled. Defaults to 'True'.

        Returns:
            None
        """
        dos['segment0']['function'] = func
        dos['segment0']['function_enable'] = state
        dos['segment0']['function_a'] = a 
        dos['segment0']['function_b'] = b
        dos['segment0']['function_c'] = c

    def mobility(self, carriers, mobility):
        """
        Sets the mobility for the specified carriers.

        Args:
            carriers (str): The type of carriers ('electrons', 'holes', 'both').
            mobility (float): The mobility value.

        Returns:
            None
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
        Sets the free states density for the specified carriers.

        Args:
            carriers (str): The type of carriers ('electrons', 'holes', 'both').
            density (float): The density value.

        Returns:
            None
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
        Sets the trap density for the specified carriers.

        Args:
            carriers (str): The type of carriers ('electrons', 'holes', 'both').
            density (float): The density value.

        Returns:
            None
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
        Sets the Urbach energy for the specified carriers.

        Args:
            carriers (str): The type of carriers ('electrons', 'holes', 'both').
            energy (float): The Urbach energy value.

        Returns:
            None
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

        Returns:
            None
        """
        self.data['srhsigman_e'] = rate

    def te_to_fh(self, rate):
        """
        Set the trap-to-free rate for electrons.

        Args:
            rate (float): The rate value.

        Returns:
            None
        """
        self.data['srhsigmap_e'] = rate

    def th_to_fe(self, rate):
        """
        Set the trap-to-free rate for holes.

        Args:
            rate (float): The rate value.

        Returns:
            None
        """
        self.data['srhsigman_h'] = rate

    def fh_to_th(self, rate):
        """
        Set the free-to-trap rate for holes.

        Args:
            rate (float): The rate value.

        Returns:
            None
        """
        self.data['srhsigmap_h'] = rate
    
    def trapping_rate(self, carriers, direction, rate):
        """
        Sets the trapping rate for the specified carriers and direction.

        Args:
            carriers (str): The type of carriers ('electrons', 'holes', 'both').
            direction (str): The direction of trapping ('free to trap', 'trap to free').
            rate (float): The trapping rate value.

        Returns:
            None
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
        Sets the electron affinity (Xi).

        Args:
            xi (float): The electron affinity value.

        Returns:
            None
        """
        self.data['Xi'] = xi
    
    def Eg(self, eg):
        """
        Sets the bandgap energy (Eg).

        Args:
            eg (float): The bandgap energy value.

        Returns:
            None
        """
        self.data['Eg'] = eg
    
    def relative_permittivity(self, er):
        """
        Sets the relative permittivity.

        Args:
            er (float): The relative permittivity value.

        Returns:
            None
        """
        self.data['epsilonr'] = er
    
    def shape_bands(self, bands):
        """
        Sets the shape of the bands.

        Args:
            bands (str): The band shape configuration.

        Returns:
            None
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
