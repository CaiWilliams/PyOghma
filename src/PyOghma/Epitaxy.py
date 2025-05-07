import os
import secrets
import ujson as json

class Epitaxy:
    def __init__(self):
        self.json_name = ''
        self.name = ''


        self.dest_dir = ''

    def load_config(self, file):
        file = file + '.json'
        with open(self.find_file(file)) as j:
            return json.loads(j.read())

    def find_file(self, file):
        config_dir = os.path.join('*', 'configs', self.json_name, file)
        filename = glob(config_dir)[0]
        self.loaded_filename = str(filename)
        return str(filename)

    def set_format(self):
        match self.json_name:
            case 'light':
                self.json_format = {self.json_name: self.light}
            case 'light_sources':
                self.json_format = {self.json_name: {self.json_sub_heading: self.data}}
            case 'lasers':
                self.json_format = {self.json_name: self.data}

    def update(self):
        with open(os.path.join(self.dest_dir,'sim.json'), 'w') as j:
            j.write(json.dumps(self.data, indent=4))
        return
    
    def load_existing(self):
        with open(os.path.join(self.dest_dir,'sim.json'), 'r') as j:
            self.data = json.load(j)
        
        num_layers = self.data['epitaxy']['segments']
        for idx in range(num_layers):
            setattr(self, self.data['epitaxy']['segment'+str(idx)]['name'].lower().replace(':',''), Layer(self.data['epitaxy']['segment'+str(idx)]))
            #temp.append(getattr(self, self.data['epitaxy']['layer'+str(idx)]['name'].lower().replace(':','')))
        #print(temp)
            


class Layer(Epitaxy):
    def __init__(self, layer):
        super(Epitaxy, self).__init__()
        self.layer_data = layer
        #print(self.layer_data.keys())
        self.name = self.layer_data['name']
        self.layer_data['id'] = 'id' + str(secrets.token_hex(8))
        self.dos = DOS()
        self.dos.set_dos(self.layer_data)

    
    def thickness(self,dx):
        self.layer_data['dx'] =  dx



class DOS:
    def __ini__(self):
        self.dos_name = ''
    
    def set_dos(self, layer_data):
        self.data = layer_data['shape_dos']

    def enable(self):
        self.data['enabled'] = 'True'

    def disable(self):
        self.data['enabled'] = 'False'
    
    def type(self, type):
        match type.lower():
            case 'exponential':
                self.data['dostype'] = type.lower()
            case 'complex':
                self.data['dostype'] = type.lower()
            case _:
                print('DOS Type Not Supported!')
    
    def shape(self, band, function, a=0, b=0, c=0):
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
        dos['segment0']['function'] = func
        dos['segment0']['function_enable'] = state
        dos['segment0']['function_a'] = a 
        dos['segment0']['function_b'] = b
        dos['segment0']['function_c'] = c

    def mobility(self, carriers, mobility):
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
        self.data['srhsigman_e'] = rate

    def te_to_fh(self, rate):
        self.data['srhsigmap_e'] = rate

    def th_to_fe(self, rate):
        self.data['srhsigman_h'] = rate

    def fh_to_th(self, rate):
        self.data['srhsigmap_h'] = rate
    
    def trapping_rate(self, carriers, direction, rate):

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
        self.data['Xi'] = xi
    
    def Eg(self, eg):
        self.data['Eg'] = eg
    
    def relative_permittivity(self, er):
        self.data['epsilonr'] = er
    
    def shape_bands(self, bands):
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
