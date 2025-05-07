import numpy as np
import mgzip as mg
import ujson as json
import scipy.constants as sc
import scipy.interpolate as spi
import matplotlib.pyplot as plt

class Ideality_Factor:
    """
    Class to calculate the ideality factor of a diode.
    """

    def __init__(self, exp):
        self.exp = exp
        with mg.open(self.exp, 'r') as f:
            self.data = json.load(f)

    def calculate(self, temp=300):
        kb = sc.value('Boltzmann constant in eV/K')
        self.Voc = []
        self.GenRate = []
        for idx,h in enumerate(self.data['experiment']['hashes']):
            self.Voc.append(float(self.data[h]['sim_info']['voc']))
            self.GenRate.append(float(self.data['experiment']['variable']['intensity'][idx])*1e6)

        GenRate = np.log(self.GenRate)
        
        plt.show()
        grad = np.mean(np.gradient(GenRate, self.Voc))
        Nid = 1/(kb * temp * grad)

        self.result = Nid

class Transport_Resistance:
    """
    Class to calculate the transport resistance of a diode.
    """
    def __init__(self, exp):
        self.exp = exp
        with mg.open(self.exp, 'r') as f:
            self.data = json.load(f)
        PJV = Psudo_JV(self.exp)
        PJV.calculate()
        self.pJV_j = PJV.pJV_j
        self.pJV_v = PJV.pJV_v

    def calculate(self):
        self.TR_Voc = []
        for idx,h in enumerate(self.data['experiment']['hashes']):
            v = self.data[h]['jv']['v']
            j = self.data[h]['jv']['j']
            pj = self.pJV_j[idx,:]
            pv = self.pJV_v[idx,:]
            x = np.linspace(np.min(v), np.max(v), 10000)
            x = np.append(x, 0)
            x = np.sort(x)
            y = spi.pchip_interpolate(v, j, x)
            py = spi.pchip_interpolate(pv, pj, x)
            Vtr = py - y
            DVtr = np.zeros(len(Vtr))
            for i in range(len(Vtr)):
                if i == 0 or i == len(Vtr)-1:
                    DVtr[i] = np.nan
                else:
                    jdx = [i-1, i, i+1]
                    f = np.gradient(Vtr[jdx],x[jdx])
                    DVtr[i] = np.mean(f)
            
            x0 = np.argwhere(x == 0).ravel()
            self.TR_Voc.append(DVtr[x0])


                

class Psudo_JV:
    """
    Class to calculate the pseudo JV of a diode.
    """

    def __init__(self, exp):
        self.exp = exp
        with mg.open(self.exp, 'r') as f:
            self.data = json.load(f)
            json.dump(self.data, open('test.json', 'w'), indent=4)

    def calculate(self):
        self.pJV_j = []
        self.pJV_v = []
        pj = []
        pv = []
        for jv in self.data['experiment']['hashes']:
            #try:
            self.pJV_j.append(np.abs(self.data[jv]['jv']['j'][0]))
            self.pJV_v.append(float(self.data[jv]['sim_info']['voc']))
            # except:
            #     self.pJV_j.append(np.nan)
            #     self.pJV_v.append(np.nan)
        
        idx = np.argwhere(np.isnan(self.pJV_j))
        self.pJV_j = np.delete(self.pJV_j, idx)
        self.pJV_v = np.delete(self.pJV_v, idx)

        self.pJV_j = np.array(self.pJV_j)
        self.pJV_v = np.array(self.pJV_v)

        self.pJV_j = np.tile(self.pJV_j, (len(self.data['experiment']['hashes']),1))
        self.pJV_v = np.tile(self.pJV_v, (len(self.data['experiment']['hashes']),1))

        for idx, jv in enumerate(self.data['experiment']['hashes']):
            self.pJV_j[idx,:] = self.pJV_j[idx,:] + self.data[jv]['jv']['j'][0]
        
        # self.pJV_j = self.pJV_j.T
        # self.pJV_v = self.pJV_v.T
            