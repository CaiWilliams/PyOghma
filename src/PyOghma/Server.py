import os
import glob
import time
import tqdm
import shutil
import secrets
import platform
import multiprocessing as mp


class Server:
    """
    Class to manage and execute simulation jobs on the server.
    Attributes:
        running (bool): Indicates if the server is running.
        stop_work (bool): Flag to stop the server's work.
        start_time (float): The start time of the server.
        cpus (int): Number of CPUs available for processing.
        jobs (list): List of jobs to be executed.
        callback (callable): Callback function for job completion.
        max_job_time (float): Maximum allowed time for a job.
        time_out (bool): Indicates if a job timed out.
        core_name (str): Name of the simulation core executable.
        sim_dir (str): Directory for simulation files.
        operating_system (str): The operating system of the platform.
        dest_dir (str): The destination directory for job files.
    Methods:
        update_cpu_count():
            Update the number of CPUs available for processing.
        clear_jobs():
            Clear the list of jobs.
        add_job(dest_dir, hash='', args=''):
            Add a new job to the server.
        run():
            Execute all jobs on the server.
        generate_job_command(job):
            Generate the command to execute a job.
        worker(job):
            Execute a single job.
        run_command(command):
            Execute a custom command.
        remove_files():
            Remove all files in the simulation directory.
    """
    def __init__(self):
        """
        Initialize the Server class.
        """
        self.running = False
        self.stop_work = False
        self.start_time = 0
        self.update_cpu_count()
        self.clear_jobs()
        self.callback=None
        self.max_job_time=None
        self.time_out=False
        self.core_name = 'oghma_core'
        self.sim_dir = ""
        self.operating_system = platform.system()
        self.dest_dir = ""

    def update_cpu_count(self):
        """
        Update the number of CPUs available for processing.
        """
        self.cpus = mp.cpu_count()
        if self.cpus > 4:
            self.cpus = self.cpus - 2
        return

    def clear_jobs(self):
        """
        Clear the list of jobs.
        """
        self.jobs = []

    def add_job(self, dest_dir, hash='', args=''):
        """
        Add a new job to the server.
        Args:
            dest_dir (str): The destination directory for the job.
            hash (str): The unique hash for the job. Defaults to an empty string.
            args (str): Additional arguments for the job. Defaults to an empty string.
        """
        j = job()
        j.path = self.dest_dir
        j.sim_dir = os.path.join(j.path,'sim.json')
        j.args = args
        j.status = 0
        j.name = hash
        j.hash = hash
        self.jobs.append(j)

    def run(self):
        """
        Execute all jobs on the server.
        """
        self.start_time = time.time()
        self.stop_work = False

        # with mp.Pool(processes=self.cpus) as p:
        #     with tqdm.tqdm(total=len(self.jobs)) as pbar:
        #         for _ in p.imap(self.generate_job_command, self.jobs):
        #             pbar.update()
        for i in range(len(self.jobs)):
            self.generate_job_command(self.jobs[i])
        # for job in self.jobs:
        #     self.worker(job)
        #self.worker(self.jobs[0])
        pbar = tqdm.tqdm(self.jobs)
        with mp.Pool(processes=self.cpus) as p:
            for _ in p.imap_unordered(self.worker, self.jobs):
               pbar.update()
        #self.remove_lock_files()
        #    tqdm.tqdm(p.imap(self.generate_job_command, self.jobs), total=len(self.jobs))
            #tqdm.tqdm(p.imap(self.worker, self.jobs), total=len(self.jobs))

    def generate_job_command(self,job):
        """
        Generate the command to execute a job.
        Args:
            job (job): The job object.
        Returns:
            job: The updated job object with the full command.
        """
        job.key = secrets.token_urlsafe(8)
        match self.operating_system:
            case 'Linux':
                lock = ' --lockfile '+ os.path.join(job.path, 'lock_#'+job.key+'.dat')
                command1 = 'timeout 10s '+ self.core_name + lock
                command_sep = ';'
                command0 = 'cd ' + job.path

                job.full_command = command0 + command_sep + command1 +' 2>&1 >' + ' /dev/null'#+ ' --sim-root-path ' + job.sim_dir'
            case 'Windows':
                lock = ' --lockfile ' + os.path.join(job.path, 'lock_#' + job.key + '.dat')
                #command1 = os.path.join("C:", os.sep, 'Program Files (x86)', 'OghmaNano')
                command1 = os.path.join(self.core_name + '.exe' + lock)
                command_sep = ' & '
                command0 = 'cd ' + job.path
               # command1 = os.path.join(os.getcwd(), 'standard_device') + ' & "oghma_core.exe"' #+ command1 + ""
                #command1 = command1 + lock

                #command1 = self.core_name + '.exe'
                job.full_command = command0 + command_sep + command1 + ' > nul'
            case _:
                print('OS Not Currently Supported!')
        return job
    
    @staticmethod
    def worker(job):
        """
        Execute a single job.
        Args:
            job (job): The job object.
        Returns:
            int: Status of the job execution.
        """
        os.system(job.full_command)
        return 1
    
    def run_command(self, command):
        """
        Execute a custom command.
        Args:
            command (str): The command to execute.
        """
        return 

    def remove_files(self):
        """
        Remove all files in the simulation directory.
        """
        for f in glob.glob(os.path.join(os.getcwd(),'OghmaSims','*'), recursive=True):
            shutil.rmtree(f)
        return

class job:
    """
    Class to represent a single simulation job.
    Attributes:
        name (str): The name of the job.
        path (str): The path to the job directory.
        args (str): Additional arguments for the job.
        start_time (float): The start time of the job.
        cpus (int): Number of CPUs allocated for the job.
        status (int): The status of the job.
    """
    def __init__(self):
        """
        Initialize the job class.
        """
        self.name = ''
        self.path = ''
        self.args = ''
        self.start_time = 0
        self.cpus = 1
        self.status = 0

if __name__ == "__main__":
    dir = os.path.join(os.getcwd(),'standard_device')
    A = Server()
    A.add_job(dest_dir=dir)
    A.run()

