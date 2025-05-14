import PyOghma as po
import matplotlib.pyplot as plt
import mgzip as mg
import shutil
import ujson as json
import numpy as np
import os

# Initialize OghmaNano and Results
Oghma = po.OghmaNano()
Results = po.Results()

# Set source simulation and experiment name
source_simulation = os.path.join(os.getcwd(), "p3htpcbm")
Oghma.set_source_simulation(source_simulation)
experiment_name = 'NewExperiment'
Oghma.set_experiment_name(experiment_name)

# Define parameters
mobility = 1e-5
trap_density = 1e-18
trapping_crosssection = 1e-20
recombination_crosssection = 1e-20
urbach_energy = 40e-3
temperature = 300
intensity = list(np.logspace(np.log10(1e-2), np.log10(1e1), 500))

# Set variables and clone simulations
Oghma.set_variables(iter_used='product', intensity=intensity)
for idx, param in enumerate(Oghma.product):
    experiment_dir = Oghma.hashes[idx]
    Oghma.clone(experiment_dir)

    # Update optical configurations
    Oghma.Optical.LightSources.set_light_Intensity(param[0])
    am15 = po.Optical.LightSource()
    Oghma.Optical.LightSources.add_light_source(am15)
    Oghma.Optical.LightSources.update()

    # Update thermal configurations
    Oghma.Thermal.set_temperature(temperature)
    Oghma.Thermal.update()

    # Update epitaxy configurations
    Oghma.Epitaxy.load_existing()
    Oghma.Epitaxy.pm6y6.dos.mobility('both', mobility)
    Oghma.Epitaxy.pm6y6.dos.trap_density('both', trap_density)
    Oghma.Epitaxy.pm6y6.dos.trapping_rate('both', 'free to trap', trapping_crosssection)
    Oghma.Epitaxy.pm6y6.dos.trapping_rate('both', 'trap to free', recombination_crosssection)
    Oghma.Epitaxy.pm6y6.dos.urbach_energy('both', urbach_energy)
    Oghma.Epitaxy.update()

    # Add job
    Oghma.add_job(experiment_dir)

# Run jobs and save results
Oghma.run_jobs()
Results.load_experiment(Oghma)
Results.create_dict()
Results.save_dict()

# Load experiment data
exp_dir = os.path.join(os.getcwd(), experiment_name + '.exp')
with mg.open(exp_dir, 'r') as f:
    data = json.load(f)

# Calculate transport resistance and plot results
TR = po.Calculate.Transport_Resistance(exp_dir)
TR.calculate()
plt.plot(intensity, TR.TR_Voc)

# Clean up and display plot
shutil.rmtree(Oghma.results_dir)
plt.show()