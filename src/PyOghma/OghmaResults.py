"""
This module provides functionality for managing and processing simulation and experiment results. 
It includes methods for loading experiments, finding and saving results, handling job data, and 
converting results into various formats such as IGOR files. The module also supports creating 
experiment dictionaries and extracting specific parameters from simulation data.
"""

import os
import glob
import secrets

import shutil
import datetime
import itertools
import platform
match platform.system():
    case 'Linux':
        import mgzip
    case 'Windows':
        import gzip
import ujson as json
import numpy as np
import pandas as pd

class Results:
    """
    Class to handle the results of simulations and experiments.
    Attributes:
        dest_dir (str): The destination directory for results.
        system (str): The operating system of the platform.
        experiment (object): The experiment object containing simulation details.
        src_dir (str): The source directory of the experiment.
        src_json (dict): The JSON data of the source simulation.
        jobs (list): List of jobs associated with the experiment.
        exp_dict (dict): Dictionary to store experiment results.
        rjl (list): List of indices of jobs to be removed.
        product (list): Cartesian product of variable values.
    """
    def __init__(self):
        """
        Initialize the Results class.
        """
        self.dest_dir = ""
        self.system = platform.system()
        
    def load_experiment(self, A):
        """
        Load the experiment details.
        Args:
            A (object): The experiment object.
        """
        self.experiment = A
        self.src_dir = A.src_dir
        with open(os.path.join(self.src_dir,'sim.json'), 'r') as j:
            self.src_json = json.load(j)
        self.jobs = A.Server.jobs

    def find_results(self):
        """
        Find all result files for the jobs.
        """
        for j in self.jobs:
            self.find_sim_info(j)
            self.find_snapshot(j)
            self.find_sim(j)
            self.find_jv(j)
    

    def find_snapshot(self, j):
        """
        Check if snapshots exist for a job.
        Args:
            j (object): The job object.
        """
        j.snapshots = False
        test = os.path.join(j.path,'snapshots')
        if os.path.isdir(test):
            j.snapshots = True


    def find_sim_info(self, j):
        """
        Check if simulation info exists for a job.
        Args:
            j (object): The job object.
        """
        j.sim_info = False
        test = os.path.join(j.path,'sim_info.dat')
        if os.path.isfile(test):
            j.sim_info = True
    

    def find_sim(self, j):
        """
        Check if simulation JSON exists for a job.
        Args:
            j (object): The job object.
        """
        j.sim = False
        test = os.path.join(j.path, 'sim.json')
        if os.path.isfile(test):
            j.sim = True

    def find_jv(self, j):
        """
        Check if JV data exists for a job.
        Args:
            j (object): The job object.
        """
        j.jv = False
        test = os.path.join(j.path,'jv.csv')
        if os.path.isfile(test):
            j.jv = True


    def save_results_ml(self, light):
        """
        Save results for machine learning experiments.
        Args:
            light (object): The light configuration for the experiment.
        Returns:
            str: The name of the saved experiment file.
        """
        self.exp_dict = {}
        self.exp_dict['light'] = list(light.values)
        self.exp_dict['experiment'] = {}
        exp = self.exp_dict['experiment']
        self.write_exp_data(exp)

        self.find_results()
        self.rjl = []
        for j in self.jobs:
            self.exp_dict[j.hash] = {}
            if j.sim_info:
                try:
                    self.write_sim_info_to_job(j)
                except:
                    self.exp_dict[j.hash]['sim_info'] = 'NaN'
        experiment_name = self.exp_dict['experiment']['name'] + '_' + secrets.token_hex(8)
        with open(experiment_name + '.json', 'wt+') as j:
            json.dump(self.exp_dict, j, indent=4)
            j.close()
        return experiment_name
    
    def create_dict(self):
        """
        Create a dictionary of experiment results.
        """
        self.exp_dict = {}
        self.exp_dict['experiment'] = {}
        exp = self.exp_dict['experiment']
        self.find_results()
        self.rjl = []
        for j in self.jobs:
            if j.sim_info:
                self.write_job(j)
            else:
                self.remove_job_list(j)
        self.remove_jobs()
        self.write_exp_data(exp)
        return
    
    def save_dict(self):
        """
        Save the experiment dictionary to a file.
        """
        match self.system:
            case 'Linux':
                with mgzip.open(self.exp_dict['experiment']['name'] + '.exp', 'wt+') as j:
                    json.dump(self.exp_dict, j, indent=4)
                    j.close()
            case 'Windows':
                with gzip.open(self.exp_dict['experiment']['name'] + '.exp', 'wt+') as j:
                    json.dump(self.exp_dict, j, indent=4)
                    j.close()
        return
    
    def load_dict(self, dict_name):
        """
        Load an experiment dictionary from a file.
        Args:
            dict_name (str): The name of the dictionary file.
        """
        match self.system:
            case 'Linux':
                with mgzip.open(os.path.join(os.getcwd(), dict_name), "r") as j:
                    data = json.load(j)
            case 'Windows':
                with gzip.open(os.path.join(os.getcwd(), dict_name), "r") as j:
                    data = json.load(j)
        self.exp_dict = data

    def write_exp_data(self, exp):
        """
        Write experiment metadata to the dictionary.
        Args:
            exp (dict): The experiment dictionary.
        """
        exp['name'] = self.experiment.experiment_name
        if self.experiment.dimensions != None:
            exp['dimensions'] = self.experiment.dimensions
        
        if self.experiment.variables != None:
            exp['variable'] = self.experiment.variables
        
        if self.experiment.points != None:
            exp['points'] = self.experiment.points

        if self.experiment.hashes != None:
            exp['hashes'] = self.experiment.hashes
    
    def variables(self):
        """
        Get the variables from the experiment dictionary.
        Returns:
            dict: The variables of the experiment.
        """
        return self.exp_dict['experiment']['variable']
    
    def hashes(self):
        """
        Get the hashes from the experiment dictionary.
        Returns:
            list: The hashes of the experiment.
        """
        return self.exp_dict['experiment']['hashes']

    def remove_job_list(self,j):
        """
        Mark a job for removal.
        Args:
            j (object): The job object.
        """
        idx = self.experiment.hashes.index(j.hash)
        self.rjl.append(idx)

    def remove_jobs(self):
        """
        Remove marked jobs from the experiment.
        """
        shutil.rmtree(self.experiment.dest_dir)


    def write_job(self, j):
        """
        Write job results to the experiment dictionary.
        Args:
            j (object): The job object.
        """
        self.exp_dict[j.hash] = {}
        job = self.exp_dict[j.hash]

        if j.sim:
            self.write_sim_to_job(j)
        else:
            pass
        
        if j.sim_info:
            self.write_sim_info_to_job(j)
        else:
            pass

        if j.jv:
            self.write_jv_to_job(j)
        else:
            pass
        
    def write_sim_to_job(self, j):
        """
        Write simulation JSON to the job dictionary.
        Args:
            j (object): The job object.
        """
        with open(os.path.join(j.path,'sim.json'), 'r') as r:
            sim = json.load(r)
        results = sim
        self.exp_dict[j.hash]['sim'] = results

    def write_sim_info_to_job(self, j):
        """
        Write simulation info to the job dictionary.
        Args:
            j (object): The job object.
        """
        with open(os.path.join(j.path,'sim_info.dat'), 'r') as r:
            sim = json.load(r)
        self.exp_dict[j.hash]['sim_info'] = sim

    def write_jv_to_job(self, j):
        """
        Write JV data to the job dictionary.
        Args:
            j (object): The job object.
        """
        with open(os.path.join(j.path,'jv.csv'), 'r') as r:
            jv = pd.read_csv(r, comment='#', delimiter=' ', header=None)
            v_jv = list(jv[0].to_numpy())
            j_jv = list(jv[1].to_numpy())
        self.exp_dict[j.hash]['jv'] = {}
        self.exp_dict[j.hash]['jv']['j'] = j_jv
        self.exp_dict[j.hash]['jv']['v'] = v_jv


    
    def convert_exp_file_to_igor(self, exp_dict_dir='', param=''):
        """
        Convert experiment results to IGOR format.
        Args:
            exp_dict_dir (str): The directory of the experiment dictionary.
            param (str): The parameter to convert.
        """
        keys = self.exp_dict['experiment']['variable'].keys()
        values = self.exp_dict['experiment']['variable'].values()
        Zeroth_key = list(keys)[0]
        Zeroth_values =list(values)[0]
        x = Zeroth_values
        list_values = list(values)[1:]
        product = list(itertools.product(*values))
        product_miZ = list(itertools.product(*list_values))
        for prod in product_miZ:
            idx = [self.match_conditions(prod, p) for p in product]
            idx = [i for i, x in enumerate(idx) if x]
            y = [self.exp_dict[self.exp_dict['experiment']['hashes'][i]]['sim_info'][param] for i in idx]
            self.save_as_igor_file(list(keys), param, product[idx[-1]], x, y)
    
    @staticmethod
    def match_conditions(prod, product):
        """
        Check if the conditions of two products match.
        Args:
            prod (tuple): The first product.
            product (tuple): The second product.
        Returns:
            bool: True if the conditions match, False otherwise.
        """
        if prod[:] == product[1:]:
            return True
        return False
    
    @staticmethod
    def save_as_igor_file(keys, param, last_prod, x, y):
        """
        Save experiment results as an IGOR file.
        Args:
            keys (list): The variable keys.
            param (str): The parameter name.
            last_prod (tuple): The last product values.
            x (list): The x-axis values.
            y (list): The y-axis values.
        """
        header = '##columns='+str(keys[0])+' '+ str(param) + ';\n' 
        data = pd.DataFrame()
        data[0] = x
        data[1] = y
        ctime = datetime.datetime.now()
        strtime = ctime.strftime("%Y%m%d%H")
        file_name = strtime + "_"
        for i in range(1,len(keys)):
            file_name +=  str(last_prod[i]) + str(keys[i]) + '_'
        file_name += 'exp.dat'
        with open(file_name, 'w') as fp:
            fp.write(header)
            data.to_csv(fp, sep=' ',index=False, header=None, lineterminator='\n')

    def read_sim_info(self, param):
        """
        Read a specific parameter from the simulation info.
        Args:
            param (str): The parameter name.
        Returns:
            object: The value of the parameter.
        """
        with open(os.path.join(self.dest_dir,'sim_info.dat'), 'r') as r:
            data = json.load()
        return data[param]
    
    def create_product(self):
        """
        Create a Cartesian product of variable values.
        """
        keys = self.exp_dict['experiment']['variable'].keys()
        values = self.exp_dict['experiment']['variable'].values()
        Zeroth_key = list(keys)[0]
        Zeroth_values =list(values)[0]
        x = Zeroth_values
        list_values = list(values)[1:]
        self.product = list(itertools.product(*values))
    
    def load_results(self, file, param, idx):
        """
        Load specific results from the experiment dictionary.
        Args:
            file (str): The file type ('sim_info', etc.).
            param (str): The parameter name.
            idx (int): The index of the result.
        Returns:
            object: The value of the parameter.
        """
        hash = self.exp_dict['experiment']['hashes'][idx]
        match file.lower():
            case 'sim_info':
                return self.exp_dict[hash]['sim_info'][param]



