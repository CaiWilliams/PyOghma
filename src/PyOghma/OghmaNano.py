import os
import shutil
import secrets
import itertools

import numpy as np
import platform

from .Optical import Optical
from .Sims import Sims
from .Thermal import Thermal
from .Server import Server
from .Epitaxy import Epitaxy
from .ML import ml


class OghmaNano:
    def __init__(self):
        self.results_dir = self.check_results()
        self.Optical = Optical()
        self.Sims = Sims()
        self.Thermal = Thermal()
        self.Server = Server()
        self.Epitaxy = Epitaxy()
        self.ML = ml()
        self.dimensions = None
        self.variables = None
        self.points = None
        self.hashes = None


    def check_results(self):
        match platform.system():
            case 'Linux':
                results_dir = os.path.join(os.sep,'dev','shm','OghmaSims')
            case 'Windows':
                results_dir = os.path.join(os.getcwd(),'OghmaSims')
            case _:
                raise Exception('Operating System not supported')

        try:
            os.mkdir(results_dir)
            return results_dir
        except:
            return results_dir
        
    def set_experiment_name(self, experiment_name):
        self.experiment_name = experiment_name

    def set_source_simulation(self, source_simulation):
        self.src_dir = os.path.join(os.getcwd(),source_simulation)
        return
    
    def set_dest_dir(self, dest_dir):
        self.dest_dir = dest_dir
        self.propagate_dest_dir()

    def propagate_dest_dir(self):
        self.Epitaxy.dest_dir = self.dest_dir
        self.Optical.dest_dir = self.dest_dir
        self.Optical.Light.dest_dir = self.dest_dir
        self.Optical.LightSources.dest_dir = self.dest_dir
        
        self.Sims.dest_dir = self.dest_dir
        self.Sims.SunsVoc.dest_dir = self.dest_dir
        self.Sims.JV.dest_dir = self.dest_dir

        self.Thermal.dest_dir = self.dest_dir
        self.Server.dest_dir = self.dest_dir

        # self.Fitting.dest_dir = self.dest_dir
        # self.Fitting.Fit_Config.dest_dir = self.dest_dir
        # self.Fitting.Duplitate.dest_dir = self.dest_dir
        # self.Fitting.Vars.dest_dir = self.dest_dir
        # self.Fitting.Rules.dest_dir = self.dest_dir
        # self.Fitting.Fits.dest_dir = self.dest_dir
    
    def set_variables(self, iter_used='product', **kwargs):
        self.dimensions = len(kwargs)
        self.variables = kwargs
        for key, value in self.variables.items():
            if type(value) != list:
                self.variables[key] = value.tolist()
        match iter_used:
            case 'product':
                self.product = itertools.product(*self.variables.values())
                self.points = len(list(itertools.product(*self.variables.values())))
                self.hashes = [secrets.token_urlsafe(8) for i in range(self.points)]
            case 'zip':
                self.product = list(itertools.zip_longest(*self.variables.values()))
                self.points = len(list(self.product))
                self.hashes = [secrets.token_urlsafe(8) for i in range(self.points)]
            case _:
                print('Iterator has not been implemented')

    def gen_hashes(self, points):
        self.hashes = [secrets.token_urlsafe(8) for i in range(points)]
    
    def clone(self, dest_dir):
        dest = os.path.join(os.getcwd(),self.results_dir,dest_dir)
        self.dest_dir = dest
        self.propagate_dest_dir()
        shutil.copytree(self.src_dir, dest)
        return

    def load(self, dest_dir):
        dest = os.path.join(os.getcwd(),self.results_dir,dest_dir)
        self.dest_dir = dest
        self.propagate_dest_dir()

    def add_job(self, hash=''):
        self.Server.add_job(os.path.join(os.getcwd(), self.results_dir, self.dest_dir,'sim.json'), hash, args="")
        return
    
    def clean_up(self):
        shutil.rmtree(os.path.join(os.getcwd(),self.results_dir))

    def run_jobs(self):
        self.Server.run()
        return

if __name__ == "__main__":
     A = OghmaNano()
     A.set_source_simulation('pm')

     T = np.arange(250,351,1)
     L = np.geomspace(0.01,2,29,endpoint=True)


     R = np.zeros(shape=(len(T),len(L)))
     T_m = np.zeros(shape=(len(T),len(L)))
     L_m = np.zeros(shape=(len(T),len(L)))
     print(R)
     for idx,x in enumerate(T):
         for jdx,y in enumerate(L):
             exp_dir = 'Test_X' + str(idx) + '_Y' + str(jdx)
             exp_res = os.path.join(os.getcwd(), A.results_dir, exp_dir, 'sim_info.dat')
             R[idx,jdx] = A.Results.read_sim_info(exp_res,'voc')
             T_m[idx,jdx] = x
             L_m[idx,jdx] = y
     plt.pcolormesh(T_m,L_m,R)
     plt.colorbar()
     plt.yscale('log')
     plt.show()

