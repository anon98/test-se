import logging
from pathlib import Path
from pyvolt import network, nv_powerflow
import numpy as np
import cimpy
import os

logging.basicConfig(filename='run_nv_powerflow.log', level=logging.INFO, filemode='w')

# Set up paths and read CIM files
this_file_folder = Path(__file__).parents[2]
p = str(this_file_folder) + "/examples/sample_data/areti"
xml_path = Path(p)

xml_files = [os.path.join(xml_path, "1.xml"),
             os.path.join(xml_path, "2.xml"),
             os.path.join(xml_path, "3.xml")]

# Read CIM files and create new network.System object
res = cimpy.cim_import(xml_files, "cgmes_v2_4_15")
system = network.System()
base_apparent_power = 25  # MW
system.load_cim_data(res['topology'], base_apparent_power)

# Execute power flow analysis
results_pf, num_iter = nv_powerflow.solve(system)

# Print results
print("Powerflow converged in " + str(num_iter) + " iterations.\n")
print("Results: \n")
voltages = []
for node in results_pf.nodes:
    print('{}={}'.format(node.topology_node.uuid, node.voltage_pu))
    voltages.append(node.voltage_pu)

# Define the case_10_nodes function to populate the ppc structure
def case_nodes(results_pf, system):

    ppc = {"version": '2'}

    ##-----  Power Flow Data  -----##
    ## system MVA base

    ppc["baseMVA"] = 1
    
    VMAX = 21
    VMIN = 19
    
    ppc["VMAX"] = VMAX
    ppc["VMIN"] = VMIN

    baseKV = 20
    
    ## bus data
    # bus_i type Pd Qd Gs Bs area Vm Va baseKV zone Vmax Vmin
    ppc["bus"] = []
    for i, node in enumerate(results_pf.nodes):
        voltage_pu = node.voltage_pu
        voltage_magnitude = abs(voltage_pu)
        voltage_angle = np.angle(voltage_pu)
        
        ppc["bus"].append([
            i + 1,               # bus number
            1,                   # bus type (PQ bus = 1, assume all are PQ)
            node.power.real,     # Pd, real power demand (MW)
            node.power.imag,     # Qd, reactive power demand (MVAr)
            0.0,                 # Gs, shunt conductance (MW)
            0.0,                 # Bs, shunt susceptance (MVAr)
            1,                   # area number
            voltage_magnitude,   # Vm, voltage magnitude (p.u.)
            voltage_angle,       # Va, voltage angle (radians)
            baseKV,              # baseKV
            1,                   # zone
            VMAX,                # Vmax
            VMIN                 # Vmin
        ])
    ppc["bus"] = np.array(ppc["bus"])

    ## generator data
    # bus, Pg, Qg, Qmax, Qmin, Vg, mBase, status, Pmax, Pmin, Pc1, Pc2,
    # Qc1min, Qc1max, Qc2min, ramp_agc, ramp_10, ramp_30, ramp_q, apf
    ppc["gen"] = []
    for i, node in enumerate(results_pf.nodes):
        if node.topology_node.type == "SLACK":
            ppc["gen"].append([
                i + 1,              # bus number
                node.power.real,    # Pg, real power output (MW)
                node.power.imag,    # Qg, reactive power output (MVAr)
                200, -200,          # Qmax, Qmin
                node.voltage_pu.real,  # Vg, voltage magnitude setpoint (p.u.)
                1,                  # mBase, machine base MVA
                1,                  # status, machine status (1 - in service)
                200, -200,          # Pmax, Pmin
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0  # Other generator parameters
            ])
    ppc["gen"] = np.array(ppc["gen"])

    ## branch data
    # fbus, tbus, r, x, base_impedance, rateA, rateB, rateC, ratio, angle, status, angmin, angmax
    ppc["branch"] = []
    for branch in system.branches:
        ppc["branch"].append([
            branch.start_node,   # fbus
            branch.end_node,     # tbus
            branch.r,            # resistance (p.u.)
            branch.x,            # reactance (p.u.)
            branch.base_impedance, # total line charging susceptance (p.u.)
            300, 300, 300,       # MVA rating A, B, C
            0, 0, 1, -360, 360   # ratio, angle, status, angmin, angmax
        ])
    ppc["branch"] = np.array(ppc["branch"])

    ## generator cost data
    # 1 startup shutdown n x1 y1 ... xn yn
    # 2 startup shutdown n c(n-1) ... c0
    ppc["gencost"] = np.array([
        [2, 0, 0, 3, 0.01, 40, 0],
        # Add more generator cost data if needed
    ])

    return ppc

# Generate the ppc data structure using the results from power flow analysis
ppc = case_nodes(results_pf, system)
print(ppc)
