import platform
import numpy as np
import ujson as json
import scipy.constants as sc
import scipy.interpolate as spi
import matplotlib.pyplot as plt

class Ideality_Factor:
    """
    Class: Ideality_Factor
    This class calculates the ideality factor of a solar cell based on experimental data.
    Attributes:
        system (str): The operating system of the machine ('Linux' or 'Windows').
        data (dict): Parsed experimental data from the input file.
        Voc (list): List of open-circuit voltages extracted from the experimental data.
        GenRate (list): List of generation rates extracted from the experimental data.
        result (float): The calculated ideality factor.
    """
    def __init__(self, exp):
        """
        Initializes the Ideality_Factor class.
        Args:
            exp (str): The file path to the input data file.
        Attributes:
            exp (str): Stores the file path to the input data file.
            system (str): The name of the operating system ('Linux' or 'Windows').
            data (dict): The data loaded from the input file. The file is read using 
                         `mg.open` on Linux and `gzip.open` on Windows.
        Raises:
            FileNotFoundError: If the specified file does not exist.
            json.JSONDecodeError: If the file content is not valid JSON.
        """
        self.exp = exp
        self.system = platform.system()
        if self.system == 'Linux':
            import mgzip as mg
            with mg.open(self.exp, 'r') as f:
                self.data = json.load(f)
        elif self.system == 'Windows':
            import gzip
            with gzip.open(self.exp, 'r') as f:
                self.data = json.load(f)

    def calculate(self, temp=300):
        """
        Calculates the ideality factor (Nid) based on the given data.
        This method computes the ideality factor using the relationship between 
        the logarithm of the generation rate and the open-circuit voltage (Voc). 
        The calculation involves the Boltzmann constant, temperature, and the 
        gradient of the logarithmic generation rate with respect to Voc.
        Args:
            temp (float, optional): The temperature in Kelvin. Defaults to 300 K.
        Attributes:
            Voc (list): A list of open-circuit voltage values extracted from the data.
            GenRate (list): A list of generation rate values extracted from the data.
            result (float): The calculated ideality factor (Nid).
        Raises:
            KeyError: If required keys are missing in the input data structure.
            ValueError: If the data contains invalid or non-numeric values.
        Notes:
            - The method assumes that the input data structure (`self.data`) is 
              properly formatted and contains the necessary keys and values.
            - The Boltzmann constant and elementary charge are retrieved using 
              the `scipy.constants.value` function.
        """
        kb = sc.value('Boltzmann constant in eV/K')
        e = sc.value('elementary charge')
        self.Voc = []
        self.GenRate = []
        for idx,h in enumerate(self.data['experiment']['hashes']):
            self.Voc.append(float(self.data[h]['sim_info']['voc']))
            self.GenRate.append(float(self.data['experiment']['variable']['intensity'][idx]))

        GenRate = np.log(self.GenRate)
        
        plt.show()
        grad = np.mean(np.gradient(GenRate, self.Voc))
        Nid = 1/(kb * temp * grad)

        self.result = Nid

class Transport_Resistance:
    """
    A class to calculate transport resistance based on experimental data.
    Attributes:
        exp (str): The path to the experimental data file.
        system (str): The operating system of the platform ('Linux' or 'Windows').
        data (dict): The experimental data loaded from the file.
        pJV_j (numpy.ndarray): Pseudo JV current density data.
        pJV_v (numpy.ndarray): Pseudo JV voltage data.
        TR_Voc (list): List of calculated transport resistance at open-circuit voltage.
    """
    def __init__(self, exp):
        """
        Initializes the Transport_Resistance class.
        Args:
            exp (str): The file path to the experiment data.
        Attributes:
            exp (str): Stores the provided file path to the experiment data.
            system (str): The operating system of the current platform ('Linux' or 'Windows').
            data (dict): The loaded experiment data from the specified file.
            pJV_j (list): The pseudo-JV current density values calculated by the Psudo_JV class.
            pJV_v (list): The pseudo-JV voltage values calculated by the Psudo_JV class.
        Raises:
            OSError: If there is an issue opening or reading the file.
            JSONDecodeError: If the file content is not valid JSON.
        """
        self.exp = exp
        self.system = platform.system()
        if self.system == 'Linux':
            import mgzip as mg
            with mg.open(self.exp, 'r') as f:
                self.data = json.load(f)
        elif self.system == 'Windows':
            import gzip
            with gzip.open(self.exp, 'r') as f:
                self.data = json.load(f)
        PJV = Psudo_JV(self.exp)
        PJV.calculate()
        self.pJV_j = PJV.pJV_j
        self.pJV_v = PJV.pJV_v

    def calculate(self):
        """
        Perform calculations to compute the conductivity at open-circuit voltage (TR_Voc) 
        for experimental data.
        This method processes JV (current-voltage) data and pJV (perturbed JV) data for each 
        experimental hash, interpolates the data using PCHIP (Piecewise Cubic Hermite Interpolating 
        Polynomial), and calculates the derivative of the voltage difference (Vtr) with respect to 
        the perturbed current density (pj). The resulting derivative at zero current density is 
        appended to the TR_Voc list.
        Attributes:
            self.TR_Voc (list): A list to store the calculated TR_Voc values for each experimental hash.
        Raises:
            ValueError: If the input data is not properly formatted or contains inconsistencies.
        Notes:
            - The method assumes that the input data is structured as a dictionary with keys 
              'experiment' and 'hashes', and that JV and pJV data are provided for each hash.
            - The interpolation and derivative calculations rely on numpy and scipy libraries.
        """
        self.TR_Voc = []
        for idx,h in enumerate(self.data['experiment']['hashes']):

            v = self.data[h]['jv']['v']
            j = self.data[h]['jv']['j']

            pj = self.pJV_j[idx,:]
            pv = self.pJV_v[idx,:]

            v = np.asarray(v)
            j = np.asarray(j)

            pj = np.asarray(pj + j[0])
            pv = np.asarray(pv)

            pj1 = np.roll(pj, -1)
            j1 = np.roll(j, -1)

            jdx = np.argwhere(pj != pj1).ravel()
            if len(jdx) > 0:
                pv = pv[jdx]
                pj = pj[jdx]
            
            jdx = np.argwhere(j != j1).ravel()
            if len(jdx) > 0:
                v = v[jdx]
                j = j[jdx]

            fjv = spi.PchipInterpolator(j, v)
            fpjv = spi.PchipInterpolator(pj, pv)
            
            x = np.linspace(np.min(pj), np.max(pj), 1000)
            x = np.append(x, 0)
            x = np.sort(x)

            Vtr = fjv(x) - fpjv(x)

            DVtr = np.zeros(len(Vtr))
            for i in range(len(x)):
                if i == 0:
                    DVtr[i] = np.nan
                elif i == len(x)-1:
                    DVtr[i] = np.nan
                else:
                    kdx = [i-1, i, i+1]
                    f = np.gradient(Vtr[kdx], x[kdx])
                    DVtr[i] = f[1]
            
            x0 = np.argwhere(x == 0).ravel()
            self.TR_Voc.append(DVtr[x0[0]])

class Psudo_JV:
    """
    Class to calculate the pseudo JV of a diode.
    Attributes:
        exp (str): The path to the experimental data file.
        system (str): The operating system of the platform ('Linux' or 'Windows').
        data (dict): The experimental data loaded from the file.
        pJV_j (numpy.ndarray): Pseudo JV current density data.
        pJV_v (numpy.ndarray): Pseudo JV voltage data.
    """
    def __init__(self, exp):
        """
        Initializes the Psudo_JV class.
        Args:
            exp (str): Path to the experiment file.
        Attributes:
            exp (str): Stores the provided file path to the experiment data.
            system (str): The operating system of the current platform ('Linux' or 'Windows').
            data (dict): The loaded experiment data from the specified file.
        Raises:
            OSError: If there is an issue opening or reading the file.
            JSONDecodeError: If the file content is not valid JSON.
        """
        self.exp = exp
        self.system = platform.system()
        if self.system == 'Linux':
            import mgzip as mg
            with mg.open(self.exp, 'r') as f:
                self.data = json.load(f)
        elif self.system == 'Windows':
            import gzip
            with gzip.open(self.exp, 'r') as f:
                self.data = json.load(f)

    def calculate(self):
        """
        Calculate the pseudo JV of the diode.
        This method processes the experimental data to compute pseudo JV current density 
        and voltage values for each experimental hash. The results are stored as numpy arrays.
        Attributes:
            pJV_j (numpy.ndarray): Pseudo JV current density data.
            pJV_v (numpy.ndarray): Pseudo JV voltage data.
        Raises:
            ValueError: If the input data is not properly formatted or contains inconsistencies.
        Notes:
            - The method assumes that the input data is structured as a dictionary with keys 
              'experiment' and 'hashes', and that JV data is provided for each hash.
        """
        self.pJV_j = []
        self.pJV_v = []
        pj = []
        pv = []
        for jv in self.data['experiment']['hashes']:
            self.pJV_j.append(np.abs(self.data[jv]['jv']['j'][0]))
            self.pJV_v.append(float(self.data[jv]['sim_info']['voc']))
        
        idx = np.argwhere(np.isnan(self.pJV_j))
        self.pJV_j = np.delete(self.pJV_j, idx)
        self.pJV_v = np.delete(self.pJV_v, idx)

        self.pJV_j = np.array(self.pJV_j)
        self.pJV_v = np.array(self.pJV_v)

        self.pJV_j = np.tile(self.pJV_j, (len(self.data['experiment']['hashes']),1))
        self.pJV_v = np.tile(self.pJV_v, (len(self.data['experiment']['hashes']),1))

        for idx, jv in enumerate(self.data['experiment']['hashes']):
            self.pJV_j[idx,:] = self.pJV_j[idx,:] + self.data[jv]['jv']['j'][0]
