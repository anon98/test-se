import logging
from pathlib import Path
import numpy as np
from pyvolt import network, nv_powerflow, nv_state_estimator, measurement
import cimpy
import os


logging.basicConfig(filename='test_switch_nv_powerflow.log', level=logging.INFO, filemode='w')

this_file_folder = os.path.dirname(os.path.realpath(__file__))
xml_path = os.path.realpath(os.path.join(this_file_folder, "..", "sample_data", "CIGRE-MV-NoTap-WithBreaker"))
xml_files = [os.path.join(xml_path, "20191126T1535Z_YYY_EQ_.xml"),
             os.path.join(xml_path, "20191126T1535Z_XX_YYY_SV_.xml"),
             os.path.join(xml_path, "20191126T1535Z_XX_YYY_TP_.xml")]


# Import CIM files and initialize system
res = cimpy.cim_import(xml_files, "cgmes_v2_4_15")
system = network.System()
base_apparent_power = 25  # Base apparent power in MW
system.load_cim_data(res['topology'], base_apparent_power)

# Execute power flow analysis
results_pf, num_iter_cim = nv_powerflow.solve(system)

# Initialize measurement set with Pinj, Qinj and V mag
measurements_set_power_vmag = measurement.MeasurementSet()
for node in results_pf.nodes:
    node_power_pu = node.power_pu  
    measurements_set_power_vmag.create_measurement(node.topology_node, measurement.ElemType.Node, measurement.MeasType.Sinj_real, np.real(node_power_pu), 0)
    measurements_set_power_vmag.create_measurement(node.topology_node, measurement.ElemType.Node, measurement.MeasType.Sinj_imag, np.imag(node_power_pu), 0)
    measurements_set_power_vmag.create_measurement(node.topology_node, measurement.ElemType.Node, measurement.MeasType.V_mag, np.absolute(node.voltage_pu), 0)
   


measurements_set_power_vmag.meas_creation()


state_estimation_results_power = nv_state_estimator.DsseCall(system, measurements_set_power_vmag)

# Initialize measurement set with Vpmu mag and phase

measurements_set_voltage = measurement.MeasurementSet()
for node in results_pf.nodes:
    measurements_set_voltage.create_measurement(node.topology_node, measurement.ElemType.Node, measurement.MeasType.Vpmu_mag, np.absolute(node.voltage_pu), 0)
    measurements_set_voltage.create_measurement(node.topology_node, measurement.ElemType.Node, measurement.MeasType.Vpmu_phase, np.angle(node.voltage_pu), 0)

measurements_set_voltage.meas_creation()


state_estimation_results_voltage = nv_state_estimator.DsseCall(system, measurements_set_voltage)



print("\nComparison of Node Voltages from Different Measurement Types:")
for power_node, voltage_node in zip(state_estimation_results_power.nodes, state_estimation_results_voltage.nodes):
   
    power_magnitude = np.abs(power_node.voltage)
    voltage_magnitude = np.abs(voltage_node.voltage)
    
    power_phase = np.angle(power_node.voltage)
    voltage_phase = np.angle(voltage_node.voltage)
    

    magnitude_diff = np.abs(power_magnitude - voltage_magnitude)
    phase_diff = np.abs(power_phase - voltage_phase) 

   
    print(f"Node UUID: {power_node.topology_node.uuid}")
    print(f"  Power Measurement Voltage: {power_node.voltage} | Magnitude: {power_magnitude}, Phase: {power_phase}")
    print(f"  Voltage Measurement Voltage: {voltage_node.voltage} | Magnitude: {voltage_magnitude}, Phase: {voltage_phase}")
    print(f"  Magnitude Difference: {magnitude_diff}")
    print(f"  Phase Difference: {np.degrees(phase_diff)} degrees\n")  