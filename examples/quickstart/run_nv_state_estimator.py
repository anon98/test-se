# This example will provide a test case running the state estimator.
# The state estimation is performed based on the results using the nv_powerflow implementation

import logging
from pathlib import Path
import numpy as np
from pyvolt import network
from pyvolt import nv_powerflow
from pyvolt import nv_state_estimator
from pyvolt import measurement
import cimpy
import os


logging.basicConfig(filename='run_nv_state_estimator.log', level=logging.INFO, filemode='w')



#python starts as module in subdirectory, 2 folders up to set the new path
this_file_folder =  Path(__file__).parents[2]
p = str(this_file_folder)+"/examples/sample_data/areti"
xml_path = Path(p)


xml_files = [os.path.join(xml_path, "1.xml"),
             os.path.join(xml_path, "2.xml"),
             os.path.join(xml_path, "3.xml")
             ]

# Read cim files and create new network.System object
res = cimpy.cim_import(xml_files, "cgmes_v2_4_15")
system = network.System()
base_apparent_power = 25  # MW
system.load_cim_data(res['topology'], base_apparent_power)

# Execute power flow analysis
results_pf, num_iter_cim = nv_powerflow.solve(system)

# --- State Estimation ---
""" Write here the percent uncertainties of the measurements"""
V_unc = 30
I_unc = 20
Sinj_unc = 0
S_unc = 0
Pmu_mag_unc = 70
Pmu_phase_unc = 0

# Create measurements data structures
"""use all node voltages as measures"""
measurements_set = measurement.MeasurementSet()
for node in results_pf.nodes:
    measurements_set.create_measurement(node.topology_node, measurement.ElemType.Node, measurement.MeasType.Vpmu_mag,
                                        np.absolute(node.voltage_pu), Pmu_mag_unc)
for node in results_pf.nodes:
    measurements_set.create_measurement(node.topology_node, measurement.ElemType.Node, measurement.MeasType.Vpmu_phase,
                                        np.angle(node.voltage_pu), Pmu_phase_unc)
measurements_set.meas_creation()

# Perform state estimation
state_estimation_results = nv_state_estimator.DsseCall(system, measurements_set)

# Print node voltages
print("state_estimation_results.voltages: ")
for node in state_estimation_results.nodes:
    print('{}={}'.format(node.topology_node.uuid, node.voltage))
    
    print(dir(node))
    
for node in state_estimation_results.nodes:
    print('{}={}'.format(node.topology_node.type, node.voltage))