
import os
import secrets
from glob import glob

import numpy as np
import ujson as json
from importlib import resources


class Sims:
    def __init__(self):
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

        #self.load_config('default')

    def set_format(self):
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

    def load_config(self, file):
        file = file + '.json'
        with open(self.find_file(file)) as j:
            self.config = json.loads(j.read())
        return


    def find_file(self, file):
        if self.json_name == self.icon.replace("_", "") or self.json_name.replace("_", "") == self.icon:
            config_dir = resources.as_file(resources.files("PyOghma.Sim_Defaults.Sims.configs."+self.json_name).joinpath(file)).args[0]
        else:
            config_dir = resources.as_file(
                resources.files("PyOghma.Sim_Defaults.Sims.configs." + self.json_name + "."+ self.name.lower().replace("\n", "_")).joinpath(file)).args[0]
        #config_dir = os.path.join('PyOghma','Sim_Defaults', 'Optical', 'configs', self.json_name, file)
        return config_dir

    def update(self):
        with open(os.path.join(self.dest_dir,'sim.json'), 'r') as j:
            data = json.load(j)

        data['sims'].update(self.json_format)

        with open(os.path.join(self.dest_dir,'sim.json'), 'w') as j:
            j.write(json.dumps(data, indent=4))

        return

    def change_experiment(self, exp_name):
        exp_name = str(exp_name).lower()
        file = 'default.json'
        exp = {'simmode': 'segment0@'+exp_name}
        with open(os.path.join(self.dest_dir,'sim.json'),'r') as j:
            data = json.load(j)

        data['sim'].update(exp)

        with open(os.path.join(self.dest_dir,'sim.json'), 'w') as j:
            j.write(json.dumps(data, indent=4))


class JV(Sims):
    def __init__(self):
        super(Sims, self).__init__()
        self.name = "JV\ncurve"
        self.icon = "jv"
        self.json_name = "jv"
        self.segment_number = 0
        self.segments_number = 1
        self.id = "id" + str(secrets.token_hex(8))

        self.load_config('default')
        self.set_format()

    def set_voltage_range(self, start: float = 0, stop: float = 1, step: float = 0.02):
        self.config['config']['Vstart'] = start
        self.config['config']['Vstop'] = stop
        self.config['config']['Vstep'] = step
        return self

    def set_jv_properties(self, **kwargs):
        for key, value in kwargs.items():
            self.config['config']['jv_' + str(key)] = value
        return self

    def set_dump_proprperties(self, **kwargs):
        for key, value in kwargs.items():
            self.config['config']['dump_' + str(key)] = value
        return self


class SunsVoc(Sims):
    def __init__(self):
        super(Sims, self).__init__()
        self.name = "Suns\ncurve"
        self.json_name = "suns_voc"
        self.icon = "sunsvoc"
        self.segment_number = 0
        self.segments_number = 1
        self.id = "id" + str(secrets.token_hex(8))

        self.load_config('default')
        self.set_format()

    def set_sun_range(self, start, stop, mul):
        self.config['config']['sun_voc_single_point'] = "False"
        self.config['config']['sun_voc_Psun_start'] = start
        self.config['config']['sun_voc_Psun_stop'] = stop
        self.config['config']['sun_voc_mul'] = mul
        return self

    def set_single_point(self, set=True):
        self.config['config']['sun_voc_single_point'] = str(set)
        return self
    def set_dump_properties(self, **kwargs):
        for key, value in kwargs.items():
            self.config['config']['dump_' + str(key)] = value
        return self


class SunsJsc(Sims):
    def __init__(self):
        super(Sims, self).__init__()
        self.name = "Suns\nJsc"
        self.icon = "sunsjsc"
        self.json_name = "suns_jsc"
        self.segment_number = 0
        self.segments_number = 1
        self.id = "id" + str(secrets.token_hex(8))

        self.load_config('default')
        self.set_format()

    def set_sun_range(self, start, stop, dp, dpmul):
        self.config['config']['sunstart'] = start
        self.config['config']['sunstop'] = stop
        self.config['config']['sundp'] = dp
        self.config['config']['sundpmul'] = dpmul
        return self


class TimeDomainMesh:
    def __init__(self, *segments):
        self.segments_number = len(segments)
        self.load_mesh('mesh')
        for idx, segment in enumerate(segments):
            self.mesh['mesh'].update({"segment" + str(idx): segment.segment})

    def load_mesh(self, file):
        file = file + '.json'
        with open(self.find_file(file)) as j:
            self.mesh = json.loads(j.read())
        return

    def find_file(self, file):
        config_dir = resources.as_file(
            resources.files("PyOghma.Sim_Defaults.Sims.configs.time_domain").joinpath(file)).args[0]

        return config_dir

    def set_loop(self, loop=False, loop_times=0, loop_reset_time=False):
        self.mesh['time_loop'] = loop
        self.mesh['time_loop_times'] = loop_times
        self.mesh['time_loop_reset_time'] = loop_reset_time
        return


class TimeDomainSegment:
    def __init__(self):
        self.load_segment('segment')

    def load_segment(self, file):
        file = file + '.json'
        with open(self.find_file(file)) as j:
            self.segment = json.loads(j.read())
        return

    def find_file(self, file):#
        config_dir = resources.as_file(
            resources.files("PyOghma.Sim_Defaults.Sims.configs.time_domain").joinpath(file)).args[0]
        return config_dir

    def set_time(self, length, dt):
        self.segment['len'] = length
        self.segment['dt'] = dt
        return

    def set_volgate(self, start, stop, mul):
        self.segment['voltage_start'] = start
        self.segment['voltage_stop'] = stop
        self.segment['mul'] = mul
        return

    def set_sun(self, start, stop):
        self.segment['sun_start'] = start
        self.segment['sun_stop'] = stop
        return

    def set_laser(self, start, stop):
        self.segment['laser_start'] = start
        self.segment['laser_stop'] = stop
        return


class CELIV(Sims):

    def __init__(self):
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

    def set_dump_proprperties(self, **kwargs):
        for key, value in kwargs.items():
            self.config['config']['dump_' + str(key)] = value
        return self


class PhotoCELIV(Sims):
    def __init__(self):
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

    def set_dump_proprperties(self, **kwargs):
        for key, value in kwargs.items():
            self.config['config']['dump_' + str(key)] = value
        return self


class TPC(Sims):
    def __init__(self):
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

    def set_dump_proprperties(self, **kwargs):
        for key, value in kwargs.items():
            self.config['config']['dump_' + str(key)] = value
        return self


class TPV(Sims):
    def __init__(self):
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

    def set_dump_proprperties(self, **kwargs):
        for key, value in kwargs.items():
            self.config['config']['dump_' + str(key)] = value
        return self


class FrequencyDomainMesh:
    def __init__(self, start, stop, steps, space):
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

    def linear(self):
        frequecies = np.linspace(self.start, self.stop, self.steps)
        for idx, freq in enumerate(frequecies):
            self.mesh["mesh"].update({"segment" + str(idx): FrequencyDomainSegment(freq).segment})
        return

    def logarithmic(self):
        frequecies = np.logspace(self.start, self.stop, self.steps)
        for idx, freq in enumerate(frequecies):
            self.mesh["mesh"].update({"segment" + str(idx): FrequencyDomainSegment(freq).segment})
        return

    def geometric(self):
        frequecies = np.geomspace(self.start, self.stop, self.steps)
        for idx, freq in enumerate(frequecies):
            self.mesh["mesh"].update({"segment" + str(idx): FrequencyDomainSegment(freq).segment})
        return


class FrequencyDomainSegment:
    def __init__(self, frequency):
        self.load_segment('segment')
        self.set_frequency(frequency)

    def set_frequency(self, frequency):
        self.segment['start'] = frequency
        self.segment['stop'] = frequency
        self.segment['points'] = 1.0
        self.segment['mul'] = 1.0
        return

    def load_segment(self, file):
        file = file + '.json'
        with open(self.find_file(file)) as j:
            self.segment = json.loads(j.read())
        return

    def find_file(self, file):
        config_dir = resources.as_file(
            resources.files("PyOghma.Sim_Defaults.Sims.configs.fx_domain").joinpath(file)).args[0]
        return str(config_dir)


class IMPS(Sims):
    def __init__(self):
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

    def set_dump_proprperties(self, **kwargs):
        for key, value in kwargs.items():
            self.config['config']['dump_' + str(key)] = value
        return self


class IMVS(Sims):
    def __init__(self):
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

    def set_dump_proprperties(self, **kwargs):
        for key, value in kwargs.items():
            self.config['config']['dump_' + str(key)] = value
        return self


class IS(Sims):
    def __init__(self):
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

    def set_dump_proprperties(self, **kwargs):
        for key, value in kwargs.items():
            self.config['config']['dump_' + str(key)] = value
        return self


class CV(Sims):
    def __init__(self):
        super(Sims, self).__init__()
        self.name = "Capacitance\nVoltage"
        self.icon = "cv"
        self.json_name = "cv"
        self.segment_number = 0
        self.segments_number = 1
        self.id = "id" + str(secrets.token_hex(8))

        self.load_config('default')
        self.set_format()

    def set_voltage_range(self, start, stop, step, frequency):
        self.config['config']['cv_start_voltage'] = start
        self.config['config']['cv_stop_voltage'] = stop
        self.config['config']['cv_dv_step'] = step
        self.config['config']['cv_fx'] = frequency
        return


class CE(Sims):
    def __init__(self):
        super(Sims, self).__init__()
        self.name = "Charge\nExtraction"
        self.icon = "ce"
        self.json_name = "ce"
        self.segment_number = 0
        self.segments_number = 1
        self.id = "id" + str(secrets.token_hex(8))

        self.load_config('default')
        self.set_format()

    def set_sun_properties(self, start, stop, steps, on_time, off_time):
        self.config['config']['ce_start_sun'] = start
        self.config['config']['ce_stop_sun'] = stop
        self.config['config']['ce_number_of_simulations'] = steps
        self.config['config']['ce_on_time'] = on_time
        self.config['config']['ce_off_time'] = off_time
        return


class PL_SS(Sims):
    def __init__(self):
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
    def __init__(self):
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
    #A = EQE()
    A = A.Sim()
    # A = FrequencyDomainMesh(0,3,4,'log')
    # A = celiv()
    # A.update('sim/update.json')
    # A = SunsVoc()
    # A = A.set_sun_range(0.2, 5, 1.1)
    # A.update(self.dest_dir='sim/update.json')
