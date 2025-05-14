"""
This module provides functionality for managing simulation configurations and operations. 
It supports various simulation types, including steady-state, time-domain, and frequency-domain 
simulations. The module allows for configuring simulation parameters, updating JSON configurations, 
and handling specific simulation modes such as JV curves, SunsVoc, CELIV, and more.
"""
import os
import secrets
from glob import glob

import numpy as np
import ujson as json
from importlib import resources


class Sims:
    """
    Main class to handle simulation configurations and operations.
    Attributes:
        name (str): The name of the simulation.
        icon (str): The icon representing the simulation.
        json_name (str): The name of the JSON configuration.
        id (str): Unique identifier for the simulation.
        segment_number (int): The current segment number.
        segments_number (int): Total number of segments.
        dest_dir (str): The destination directory for saving or loading data.
        JV (JV): Instance of the JV class.
        SunsVoc (SunsVoc): Instance of the SunsVoc class.
        SunsJsc (SunsJsc): Instance of the SunsJsc class.
        CELIV (CELIV): Instance of the CELIV class.
        PhotoCELIV (PhotoCELIV): Instance of the PhotoCELIV class.
        TPC (TPC): Instance of the TPC class.
        TPV (TPV): Instance of the TPV class.
        IMPS (IMPS): Instance of the IMPS class.
        IMVS (IMVS): Instance of the IMVS class.
        IS (IS): Instance of the IS class.
        CV (CV): Instance of the CV class.
        CE (CE): Instance of the CE class.
        PL_SS (PL_SS): Instance of the PL_SS class.
        EQE (EQE): Instance of the EQE class.
    """
    def __init__(self) -> None:
        """
        Initialize the Sims class and its subcomponents.
        """
        self.name = ""
        self.icon = ""
        self.json_name = ""
        self.id = "id" + str(secrets.token_hex(8))
        self.segment_number = 0
        self.segments_number = 1
        self.dest_dir = ""

        # steady state
        self.JV = JV()
        self.SunsVoc = SunsVoc()
        self.SunsJsc = SunsJsc()

        # time domain
        self.CELIV = CELIV()
        self.PhotoCELIV = PhotoCELIV()
        self.TPC = TPC()
        self.TPV = TPV()

        # frequency domain
        self.IMPS = IMPS()
        self.IMVS = IMVS()
        self.IS = IS()

        # Other
        self.CV = CV()
        self.CE = CE()
        self.PL_SS = PL_SS()
        self.EQE = EQE

    def set_format(self) -> None:
        """
        Set the format of the JSON data based on the json_name.
        """
        match self.json_name:
            case 'time_domain':
                self.json_format = {self.json_name: {"segments": int(self.segments_number),
                                                     "segment" + str(self.segment_number): {"name": self.name,
                                                                                            "icon": self.icon,
                                                                                            "config": self.config[
                                                                                                'config'],
                                                                                            "mesh": self.time.mesh[
                                                                                                'mesh'],
                                                                                            "id": self.id}}}
            case 'fx_domain':
                self.json_format = {self.json_name: {"segments": int(self.segments_number),
                                                     "segment" + str(self.segment_number): {"name": self.name,
                                                                                            "icon": self.icon,
                                                                                            "config": self.config[
                                                                                                'config'],
                                                                                            "mesh": self.fx.mesh[
                                                                                                'mesh'],
                                                                                            "id": self.id}}}
            case _:
                self.json_format = {self.json_name: {"segments": int(self.segments_number),
                                                     "segment" + str(self.segment_number): {"name": self.name,
                                                                                            "icon": self.icon,
                                                                                            "config": self.config[
                                                                                                'config'],
                                                                                            "id": self.id}}}
        return

    def load_config(self, file: str) -> None:
        """
        Load a configuration file.
        Args:
            file (str): The name of the configuration file.
        """
        file = file + '.json'
        with open(self.find_file(file)) as j:
            self.config = json.loads(j.read())
        return

    def find_file(self, file: str) -> str:
        """
        Find a file in the directory structure.
        Args:
            file (str): The name of the file to find.
        Returns:
            str: The path to the found file.
        """
        if self.json_name == self.icon.replace("_", "") or self.json_name.replace("_", "") == self.icon:
            config_dir = resources.as_file(resources.files("PyOghma.Sim_Defaults.Sims.configs."+self.json_name).joinpath(file)).args[0]
        else:
            config_dir = resources.as_file(
                resources.files("PyOghma.Sim_Defaults.Sims.configs." + self.json_name + "."+ self.name.lower().replace("\n", "_")).joinpath(file)).args[0]
        return config_dir

    def update(self) -> None:
        """
        Update the JSON file with the current data.
        """
        with open(os.path.join(self.dest_dir,'sim.json'), 'r') as j:
            data = json.load(j)

        data['sims'].update(self.json_format)

        with open(os.path.join(self.dest_dir,'sim.json'), 'w') as j:
            j.write(json.dumps(data, indent=4))

        return

    def change_experiment(self, exp_name: str) -> None:
        """
        Change the experiment mode in the simulation configuration.
        Args:
            exp_name (str): The name of the experiment mode.
        """
        exp_name = str(exp_name).lower()
        file = 'default.json'
        exp = {'simmode': 'segment0@'+exp_name}
        with open(os.path.join(self.dest_dir,'sim.json'),'r') as j:
            data = json.load(j)

        data['sim'].update(exp)

        with open(os.path.join(self.dest_dir,'sim.json'), 'w') as j:
            j.write(json.dumps(data, indent=4))


class JV(Sims):
    """
    Class to handle JV curve simulations.
    Inherits from:
        Sims
    """
    def __init__(self) -> None:
        """
        Initialize the JV class.
        """
        super(Sims, self).__init__()
        self.name = "JV\ncurve"
        self.icon = "jv"
        self.json_name = "jv"
        self.segment_number = 0
        self.segments_number = 1
        self.id = "id" + str(secrets.token_hex(8))

        self.load_config('default')
        self.set_format()

    def set_voltage_range(self, start: float = 0, stop: float = 1, step: float = 0.02) -> 'JV':
        """
        Set the voltage range for the JV simulation.
        Args:
            start (float): The starting voltage.
            stop (float): The stopping voltage.
            step (float): The voltage step size.
        """
        self.config['config']['Vstart'] = start
        self.config['config']['Vstop'] = stop
        self.config['config']['Vstep'] = step
        return self

    def set_jv_properties(self, **kwargs: dict) -> 'JV':
        """
        Set additional JV properties.
        Args:
            **kwargs: Key-value pairs of JV properties.
        """
        for key, value in kwargs.items():
            self.config['config']['jv_' + str(key)] = value
        return self

    def set_dump_proprperties(self, **kwargs: dict) -> 'JV':
        """
        Set dump properties for the JV simulation.
        Args:
            **kwargs: Key-value pairs of dump properties.
        """
        for key, value in kwargs.items():
            self.config['config']['dump_' + str(key)] = value
        return self


class SunsVoc(Sims):
    """
    Class to handle SunsVoc simulations.
    Inherits from:
        Sims
    """
    def __init__(self) -> None:
        """
        Initialize the SunsVoc class.
        """
        super(Sims, self).__init__()
        self.name = "Suns\ncurve"
        self.json_name = "suns_voc"
        self.icon = "sunsvoc"
        self.segment_number = 0
        self.segments_number = 1
        self.id = "id" + str(secrets.token_hex(8))

        self.load_config('default')
        self.set_format()

    def set_sun_range(self, start: float, stop: float, mul: float) -> 'SunsVoc':
        """
        Set the sun intensity range for the simulation.
        Args:
            start (float): The starting sun intensity.
            stop (float): The stopping sun intensity.
            mul (float): The multiplication factor for the intensity.
        """
        self.config['config']['sun_voc_single_point'] = "False"
        self.config['config']['sun_voc_Psun_start'] = start
        self.config['config']['sun_voc_Psun_stop'] = stop
        self.config['config']['sun_voc_mul'] = mul
        return self

    def set_single_point(self, set: bool = True) -> 'SunsVoc':
        """
        Enable or disable single-point simulation.
        Args:
            set (bool): Whether to enable single-point simulation.
        """
        self.config['config']['sun_voc_single_point'] = str(set)
        return self

    def set_dump_properties(self, **kwargs: dict) -> 'SunsVoc':
        """
        Set dump properties for the SunsVoc simulation.
        Args:
            **kwargs: Key-value pairs of dump properties.
        """
        for key, value in kwargs.items():
            self.config['config']['dump_' + str(key)] = value
        return self


class SunsJsc(Sims):
    """
    Class to handle SunsJsc simulations.
    Inherits from:
        Sims
    """
    def __init__(self) -> None:
        """
        Initialize the SunsJsc class.
        """
        super(Sims, self).__init__()
        self.name = "Suns\nJsc"
        self.icon = "sunsjsc"
        self.json_name = "suns_jsc"
        self.segment_number = 0
        self.segments_number = 1
        self.id = "id" + str(secrets.token_hex(8))

        self.load_config('default')
        self.set_format()

    def set_sun_range(self, start: float, stop: float, dp: float, dpmul: float) -> 'SunsJsc':
        """
        Set the sun intensity range for the simulation.
        Args:
            start (float): The starting sun intensity.
            stop (float): The stopping sun intensity.
            dp (float): The intensity step size.
            dpmul (float): The multiplication factor for the intensity.
        """
        self.config['config']['sunstart'] = start
        self.config['config']['sunstop'] = stop
        self.config['config']['sundp'] = dp
        self.config['config']['sundpmul'] = dpmul
        return self


class TimeDomainMesh:
    """
    Class to handle time domain mesh configurations.
    Attributes:
        segments_number (int): The number of segments in the mesh.
        mesh (dict): The mesh configuration data.
    """
    def __init__(self, *segments: object) -> None:
        """
        Initialize the TimeDomainMesh class.
        Args:
            *segments: Variable-length list of time domain segments.
        """
        self.segments_number = len(segments)
        self.load_mesh('mesh')
        for idx, segment in enumerate(segments):
            self.mesh['mesh'].update({"segment" + str(idx): segment.segment})

    def load_mesh(self, file: str) -> None:
        """
        Load the mesh configuration from a file.
        Args:
            file (str): The name of the configuration file.
        """
        file = file + '.json'
        with open(self.find_file(file)) as j:
            self.mesh = json.loads(j.read())
        return

    def find_file(self, file: str) -> str:
        """
        Find a file in the directory structure.
        Args:
            file (str): The name of the file to find.
        Returns:
            str: The path to the found file.
        """
        config_dir = resources.as_file(
            resources.files("PyOghma.Sim_Defaults.Sims.configs.time_domain").joinpath(file)).args[0]

        return config_dir

    def set_loop(self, loop: bool = False, loop_times: int = 0, loop_reset_time: bool = False) -> 'TimeDomainMesh':
        """
        Set loop properties for the time domain mesh.
        Args:
            loop (bool): Whether to enable looping.
            loop_times (int): The number of loop iterations.
            loop_reset_time (bool): Whether to reset time after each loop.
        """
        self.mesh['time_loop'] = loop
        self.mesh['time_loop_times'] = loop_times
        self.mesh['time_loop_reset_time'] = loop_reset_time
        return


class TimeDomainSegment:
    """
    Class to handle individual time domain segment configurations.
    Attributes:
        segment (dict): The segment configuration data.
    """
    def __init__(self) -> None:
        """
        Initialize the TimeDomainSegment class.
        """
        self.load_segment('segment')

    def load_segment(self, file: str) -> None:
        """
        Load the segment configuration from a file.
        Args:
            file (str): The name of the configuration file.
        """
        file = file + '.json'
        with open(self.find_file(file)) as j:
            self.segment = json.loads(j.read())
        return

    def find_file(self, file: str) -> str:
        """
        Find a file in the directory structure.
        Args:
            file (str): The name of the file to find.
        Returns:
            str: The path to the found file.
        """
        config_dir = resources.as_file(
            resources.files("PyOghma.Sim_Defaults.Sims.configs.time_domain").joinpath(file)).args[0]
        return config_dir

    def set_time(self, length: float, dt: float) -> 'TimeDomainSegment':
        """
        Set the time properties for the segment.
        Args:
            length (float): The length of the time segment.
            dt (float): The time step size.
        """
        self.segment['len'] = length
        self.segment['dt'] = dt
        return

    def set_volgate(self, start: float, stop: float, mul: float) -> 'TimeDomainSegment':
        """
        Set the voltage properties for the segment.
        Args:
            start (float): The starting voltage.
            stop (float): The stopping voltage.
            mul (float): The multiplication factor for the voltage.
        """
        self.segment['voltage_start'] = start
        self.segment['voltage_stop'] = stop
        self.segment['mul'] = mul
        return

    def set_sun(self, start: float, stop: float) -> 'TimeDomainSegment':
        """
        Set the sun properties for the segment.
        Args:
            start (float): The starting sun intensity.
            stop (float): The stopping sun intensity.
        """
        self.segment['sun_start'] = start
        self.segment['sun_stop'] = stop
        return

    def set_laser(self, start: float, stop: float) -> 'TimeDomainSegment':
        """
        Set the laser properties for the segment.
        Args:
            start (float): The starting laser intensity.
            stop (float): The stopping laser intensity.
        """
        self.segment['laser_start'] = start
        self.segment['laser_stop'] = stop
        return


class CELIV(Sims):
    """
    Class to handle CELIV simulations.
    Inherits from:
        Sims
    """
    def __init__(self) -> None:
        """
        Initialize the CELIV class.
        """
        super(Sims, self).__init__()
        self.name = "celiv"
        self.icon = "celiv"
        self.json_name = "time_domain"
        self.segment_number = 0
        self.segments_number = 7
        self.id = "id" + str(secrets.token_hex(8))

        self.load_config('default')

        segment0 = TimeDomainSegment()
        segment1 = TimeDomainSegment()
        segment2 = TimeDomainSegment()
        segment3 = TimeDomainSegment()

        self.time = TimeDomainMesh(segment0, segment1, segment2, segment3)

        self.set_format()

    def set_dump_proprperties(self, **kwargs: dict) -> 'CELIV':
        """
        Set dump properties for the CELIV simulation.
        Args:
            **kwargs: Key-value pairs of dump properties.
        """
        for key, value in kwargs.items():
            self.config['config']['dump_' + str(key)] = value
        return self


class PhotoCELIV(Sims):
    """
    Class to handle PhotoCELIV simulations.
    Inherits from:
        Sims
    """
    def __init__(self) -> None:
        """
        Initialize the PhotoCELIV class.
        """
        super(Sims, self).__init__()
        self.name = "PHOTO\nceliv"
        self.icon = "photo_celiv"
        self.json_name = "time_domain"
        self.segment_number = 1
        self.segments_number = 7
        self.id = "id" + str(secrets.token_hex(8))

        self.load_config('default')

        segment0 = TimeDomainSegment()
        segment1 = TimeDomainSegment()
        segment2 = TimeDomainSegment()
        segment3 = TimeDomainSegment()

        self.time = TimeDomainMesh(segment0, segment1, segment2, segment3)

        self.set_format()

    def set_dump_proprperties(self, **kwargs: dict) -> 'PhotoCELIV':
        """
        Set dump properties for the PhotoCELIV simulation.
        Args:
            **kwargs: Key-value pairs of dump properties.
        """
        for key, value in kwargs.items():
            self.config['config']['dump_' + str(key)] = value
        return self


class TPC(Sims):
    """
    Class to handle TPC simulations.
    Inherits from:
        Sims
    """
    def __init__(self) -> None:
        """
        Initialize the TPC class.
        """
        super(Sims, self).__init__()
        self.name = "TPC"
        self.icon = "tpc"
        self.json_name = "time_domain"
        self.segment_number = 1
        self.segments_number = 7
        self.id = "id" + str(secrets.token_hex(8))

        self.load_config('default')

        segment0 = TimeDomainSegment()
        segment1 = TimeDomainSegment()

        self.time = TimeDomainMesh(segment0, segment1)

        self.set_format()

    def set_dump_proprperties(self, **kwargs: dict) -> 'TPC':
        """
        Set dump properties for the TPC simulation.
        Args:
            **kwargs: Key-value pairs of dump properties.
        """
        for key, value in kwargs.items():
            self.config['config']['dump_' + str(key)] = value
        return self


class TPV(Sims):
    """
    Class to handle TPV simulations.
    Inherits from:
        Sims
    """
    def __init__(self) -> None:
        """
        Initialize the TPV class.
        """
        super(Sims, self).__init__()
        self.name = "TPV"
        self.icon = "tpv"
        self.json_name = "time_domain"
        self.segment_number = 1
        self.segments_number = 7
        self.id = "id" + str(secrets.token_hex(8))

        self.load_config('default')

        segment0 = TimeDomainSegment()

        self.time = TimeDomainMesh(segment0)

        self.set_format()

    def set_dump_proprperties(self, **kwargs: dict) -> 'TPV':
        """
        Set dump properties for the TPV simulation.
        Args:
            **kwargs: Key-value pairs of dump properties.
        """
        for key, value in kwargs.items():
            self.config['config']['dump_' + str(key)] = value
        return self


class FrequencyDomainMesh:
    """
    Class to handle frequency domain mesh configurations.
    Attributes:
        start (float): The starting frequency.
        stop (float): The stopping frequency.
        steps (int): The number of steps in the frequency range.
        mesh (dict): The mesh configuration data.
    """
    def __init__(self, start: float, stop: float, steps: int, space: str) -> None:
        """
        Initialize the FrequencyDomainMesh class.
        Args:
            start (float): The starting frequency.
            stop (float): The stopping frequency.
            steps (int): The number of steps in the frequency range.
            space (str): The type of frequency spacing ('lin', 'log', 'geo').
        """
        self.start = start
        self.stop = stop
        self.steps = steps
        self.mesh = {"mesh": {"segments": self.steps}}
        match space:
            case 'lin':
                self.linear()
            case 'log':
                self.logarithmic()
            case 'geo':
                self.geometric()

    def linear(self) -> None:
        """
        Generate a linear frequency mesh.
        """
        frequecies = np.linspace(self.start, self.stop, self.steps)
        for idx, freq in enumerate(frequecies):
            self.mesh["mesh"].update({"segment" + str(idx): FrequencyDomainSegment(freq).segment})
        return

    def logarithmic(self) -> None:
        """
        Generate a logarithmic frequency mesh.
        """
        frequecies = np.logspace(self.start, self.stop, self.steps)
        for idx, freq in enumerate(frequecies):
            self.mesh["mesh"].update({"segment" + str(idx): FrequencyDomainSegment(freq).segment})
        return

    def geometric(self) -> None:
        """
        Generate a geometric frequency mesh.
        """
        frequecies = np.geomspace(self.start, self.stop, self.steps)
        for idx, freq in enumerate(frequecies):
            self.mesh["mesh"].update({"segment" + str(idx): FrequencyDomainSegment(freq).segment})
        return


class FrequencyDomainSegment:
    """
    Class to handle individual frequency domain segment configurations.
    Attributes:
        segment (dict): The segment configuration data.
    """
    def __init__(self, frequency: float) -> None:
        """
        Initialize the FrequencyDomainSegment class.
        Args:
            frequency (float): The frequency for the segment.
        """
        self.load_segment('segment')
        self.set_frequency(frequency)

    def set_frequency(self, frequency: float) -> None:
        """
        Set the frequency properties for the segment.
        Args:
            frequency (float): The frequency for the segment.
        """
        self.segment['start'] = frequency
        self.segment['stop'] = frequency
        self.segment['points'] = 1.0
        self.segment['mul'] = 1.0
        return

    def load_segment(self, file: str) -> None:
        """
        Load the segment configuration from a file.
        Args:
            file (str): The name of the configuration file.
        """
        file = file + '.json'
        with open(self.find_file(file)) as j:
            self.segment = json.loads(j.read())
        return

    def find_file(self, file: str) -> str:
        """
        Find a file in the directory structure.
        Args:
            file (str): The name of the file to find.
        Returns:
            str: The path to the found file.
        """
        config_dir = resources.as_file(
            resources.files("PyOghma.Sim_Defaults.Sims.configs.fx_domain").joinpath(file)).args[0]
        return str(config_dir)


class IMPS(Sims):
    """
    Class to handle IMPS simulations.
    Inherits from:
        Sims
    """
    def __init__(self) -> None:
        """
        Initialize the IMPS class.
        """
        super(Sims, self).__init__()
        self.name = "IMPS"
        self.icon = "spectrum"
        self.json_name = "fx_domain"
        self.segment_number = 0
        self.segments_number = 4
        self.id = "id" + str(secrets.token_hex(8))

        self.load_config('default')

        self.fx = FrequencyDomainMesh(0, 3, 4, 'log')

        self.set_format()

    def set_dump_proprperties(self, **kwargs: dict) -> 'IMPS':
        """
        Set dump properties for the IMPS simulation.
        Args:
            **kwargs: Key-value pairs of dump properties.
        """
        for key, value in kwargs.items():
            self.config['config']['dump_' + str(key)] = value
        return self


class IMVS(Sims):
    """
    Class to handle IMVS simulations.
    Inherits from:
        Sims
    """
    def __init__(self) -> None:
        """
        Initialize the IMVS class.
        """
        super(Sims, self).__init__()
        self.name = "IMVS"
        self.icon = "spectrum"
        self.json_name = "fx_domain"
        self.segment_number = 1
        self.segments_number = 4
        self.id = "id" + str(secrets.token_hex(8))

        self.load_config('default')

        self.fx = FrequencyDomainMesh(0, 3, 4, 'log')

        self.set_format()

    def set_dump_proprperties(self, **kwargs: dict) -> 'IMVS':
        """
        Set dump properties for the IMVS simulation.
        Args:
            **kwargs: Key-value pairs of dump properties.
        """
        for key, value in kwargs.items():
            self.config['config']['dump_' + str(key)] = value
        return self


class IS(Sims):
    """
    Class to handle IS simulations.
    Inherits from:
        Sims
    """
    def __init__(self) -> None:
        """
        Initialize the IS class.
        """
        super(Sims, self).__init__()
        self.name = "imvs"
        self.icon = "spectrum"
        self.json_name = "fx_domain"
        self.segment_number = 1
        self.segments_number = 4
        self.id = "id" + str(secrets.token_hex(8))

        self.load_config('default')

        self.fx = FrequencyDomainMesh(0, 3, 4, 'log')

        self.set_format()

    def set_dump_proprperties(self, **kwargs: dict) -> 'IS':
        """
        Set dump properties for the IS simulation.
        Args:
            **kwargs: Key-value pairs of dump properties.
        """
        for key, value in kwargs.items():
            self.config['config']['dump_' + str(key)] = value
        return self


class CV(Sims):
    """
    Class to handle CV simulations.
    Inherits from:
        Sims
    """
    def __init__(self) -> None:
        """
        Initialize the CV class.
        """
        super(Sims, self).__init__()
        self.name = "Capacitance\nVoltage"
        self.icon = "cv"
        self.json_name = "cv"
        self.segment_number = 0
        self.segments_number = 1
        self.id = "id" + str(secrets.token_hex(8))

        self.load_config('default')
        self.set_format()

    def set_voltage_range(self, start: float, stop: float, step: float, frequency: float) -> 'CV':
        """
        Set the voltage range and frequency for the CV simulation.
        Args:
            start (float): The starting voltage.
            stop (float): The stopping voltage.
            step (float): The voltage step size.
            frequency (float): The frequency for the simulation.
        """
        self.config['config']['cv_start_voltage'] = start
        self.config['config']['cv_stop_voltage'] = stop
        self.config['config']['cv_dv_step'] = step
        self.config['config']['cv_fx'] = frequency
        return


class CE(Sims):
    """
    Class to handle CE simulations.
    Inherits from:
        Sims
    """
    def __init__(self) -> None:
        """
        Initialize the CE class.
        """
        super(Sims, self).__init__()
        self.name = "Charge\nExtraction"
        self.icon = "ce"
        self.json_name = "ce"
        self.segment_number = 0
        self.segments_number = 1
        self.id = "id" + str(secrets.token_hex(8))

        self.load_config('default')
        self.set_format()

    def set_sun_properties(self, start: float, stop: float, steps: int, on_time: float, off_time: float) -> 'CE':
        """
        Set the sun properties for the CE simulation.
        Args:
            start (float): The starting sun intensity.
            stop (float): The stopping sun intensity.
            steps (int): The number of simulation steps.
            on_time (float): The sun on time.
            off_time (float): The sun off time.
        """
        self.config['config']['ce_start_sun'] = start
        self.config['config']['ce_stop_sun'] = stop
        self.config['config']['ce_number_of_simulations'] = steps
        self.config['config']['ce_on_time'] = on_time
        self.config['config']['ce_off_time'] = off_time
        return


class PL_SS(Sims):
    """
    Class to handle PL_SS simulations.
    Inherits from:
        Sims
    """
    def __init__(self) -> None:
        """
        Initialize the PL_SS class.
        """
        super(Sims, self).__init__()
        self.name = "PL"
        self.icon = "pl"
        self.json_name = "pl"
        self.segment_number = 0
        self.segments_number = 1
        self.id = "id" + str(secrets.token_hex(8))

        self.load_config('default')
        self.set_format()


class EQE(Sims):
    """
    Class to handle EQE simulations.
    Inherits from:
        Sims
    """
    def __init__(self) -> None:
        """
        Initialize the EQE class.
        """
        self.name = "EQE"
        self.icon = "qe"
        self.json_name = "eqe"
        self.segment_number = 0
        self.segments_number = 1
        self.id = "id" + str(secrets.token_hex(8))

        self.load_config('default')

        self.eqe_voltage = self.config['config']['ce_eqe_voltage']
        self.set_format()


if __name__ == '__main__':
    """
    Main execution block for testing the Sims class and its subcomponents.
    """
    # A = EQE()
    A = A.Sim()
    # A = FrequencyDomainMesh(0,3,4,'log')
    # A = celiv()
    # A.update('sim/update.json')
    # A = SunsVoc()
    # A = A.set_sun_range(0.2, 5, 1.1)
    # A.update(self.dest_dir='sim/update.json')
