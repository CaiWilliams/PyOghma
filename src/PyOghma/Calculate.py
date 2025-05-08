import platform
import numpy as np
match platform.system():
    case 'Linux':   
        import mgzip as mg
    case 'Windows':
        import gzip
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
        self.system = platform.system()
        if self.system == 'Linux':
            with mg.open(self.exp, 'r') as f:
                self.data = json.load(f)
        elif self.system == 'Windows':
            with gzip.open(self.exp, 'r') as f:
                self.data = json.load(f)


    def calculate(self, temp=300):
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
    Class to calculate the transport resistance of a diode.
    """
    def __init__(self, exp):
        self.exp = exp
        self.system = platform.system()
        if self.system == 'Linux':
            with mg.open(self.exp, 'r') as f:
                self.data = json.load(f)
        elif self.system == 'Windows':
            with gzip.open(self.exp, 'r') as f:
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
    """

    def __init__(self, exp):
        self.exp = exp
        self.system = platform.system()
        if self.system == 'Linux':
            with mg.open(self.exp, 'r') as f:
                self.data = json.load(f)
        elif self.system == 'Windows':
            with gzip.open(self.exp, 'r') as f:
                self.data = json.load(f)


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
            