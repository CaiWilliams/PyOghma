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
    """
    Main class to manage simulations and configurations for OghmaNano.
    Attributes:
        results_dir (str): Directory to store simulation results.
        Optical (Optical): Instance of the Optical class.
        Sims (Sims): Instance of the Sims class.
        Thermal (Thermal): Instance of the Thermal class.
        Server (Server): Instance of the Server class.
        Epitaxy (Epitaxy): Instance of the Epitaxy class.
        ML (ml): Instance of the ml class.
        dimensions (int): Number of dimensions for variable configurations.
        variables (dict): Dictionary of variables for simulations.
        points (int): Number of points in the variable space.
        hashes (list): List of unique hashes for simulations.
    Methods:
        check_results():
            Check and create the results directory based on the operating system.
        set_experiment_name(experiment_name):
            Set the name of the experiment.
        set_source_simulation(source_simulation):
            Set the source directory for the simulation.
        set_dest_dir(dest_dir):
            Set the destination directory for the simulation.
        propagate_dest_dir():
            Propagate the destination directory to all subcomponents.
        set_variables(iter_used='product', **kwargs):
            Set the variables for the simulation.
        gen_hashes(points):
            Generate unique hashes for the given number of points.
        clone(dest_dir):
            Clone the source simulation to the destination directory.
        load(dest_dir):
            Load an existing simulation from the destination directory.
        add_job(hash=''):
            Add a job to the server for execution.
        clean_up():
            Remove the results directory and its contents.
        run_jobs():
            Execute all jobs on the server.
    """
    def __init__(self):
        """
        Initialize the OghmaNano class and its subcomponents.
        """
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
        """
        Check and create the results directory based on the operating system.
        Returns:
            str: Path to the results directory.
        """
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
        """
        Set the name of the experiment.
        Args:
            experiment_name (str): The name of the experiment.
        """
        self.experiment_name = experiment_name

    def set_source_simulation(self, source_simulation):
        """
        Set the source directory for the simulation.
        Args:
            source_simulation (str): The name of the source simulation directory.
        """
        self.src_dir = os.path.join(os.getcwd(),source_simulation)
        return
    
    def set_dest_dir(self, dest_dir):
        """
        Set the destination directory for the simulation.
        Args:
            dest_dir (str): The destination directory.
        """
        self.dest_dir = dest_dir
        self.propagate_dest_dir()

    def propagate_dest_dir(self):
        """
        Propagate the destination directory to all subcomponents.
        """
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
        """
        Set the variables for the simulation.
        Args:
            iter_used (str): The iterator type ('product' or 'zip').
            **kwargs: Variable-length keyword arguments representing variables.
        """
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
        """
        Generate unique hashes for the given number of points.
        Args:
            points (int): The number of points to generate hashes for.
        """
        self.hashes = [secrets.token_urlsafe(8) for i in range(points)]
    
    def clone(self, dest_dir):
        """
        Clone the source simulation to the destination directory.
        Args:
            dest_dir (str): The name of the destination directory.
        """
        dest = os.path.join(os.getcwd(),self.results_dir,dest_dir)
        self.dest_dir = dest
        self.propagate_dest_dir()
        shutil.copytree(self.src_dir, dest)
        return

    def load(self, dest_dir):
        """
        Load an existing simulation from the destination directory.
        Args:
            dest_dir (str): The name of the destination directory.
        """
        dest = os.path.join(os.getcwd(),self.results_dir,dest_dir)
        self.dest_dir = dest
        self.propagate_dest_dir()

    def add_job(self, hash=''):
        """
        Add a job to the server for execution.
        Args:
            hash (str): The unique hash for the job. Defaults to an empty string.
        """
        self.Server.add_job(os.path.join(os.getcwd(), self.results_dir, self.dest_dir,'sim.json'), hash, args="")
        return
    
    def clean_up(self):
        """
        Remove the results directory and its contents.
        """
        shutil.rmtree(os.path.join(os.getcwd(),self.results_dir))

    def run_jobs(self):
        """
        Execute all jobs on the server.
        """
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

