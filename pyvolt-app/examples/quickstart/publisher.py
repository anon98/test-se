import logging
from pathlib import Path
import numpy as np
from pyvolt import network, nv_powerflow, nv_state_estimator, measurement
import cimpy
import os
import json
import time
import random
import paho.mqtt.client as mqtt  # Import MQTT client

# MQTT Configuration
MQTT_BROKER = os.getenv("MQTT_BROKER", "mosquitto")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "state_estimation/results")

# Set up logging
logging.basicConfig(
    filename="test_switch_nv_state_estimator.log",
    level=logging.INFO,
    filemode="w",
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Import CIM files and create network.System object
this_file_folder = os.path.dirname(os.path.realpath(__file__))
xml_path = os.path.realpath(os.path.join(this_file_folder, "..", "sample_data", "CIGRE-MV-NoTap-WithBreaker"))
xml_files = [
    os.path.join(xml_path, "20191126T1535Z_YYY_EQ_.xml"),
    os.path.join(xml_path, "20191126T1535Z_XX_YYY_SV_.xml"),
    os.path.join(xml_path, "20191126T1535Z_XX_YYY_TP_.xml"),
]

# Read CIM files
res = cimpy.cim_import(xml_files, "cgmes_v2_4_15")
system = network.System()
base_apparent_power = 25  # MW
system.load_cim_data(res["topology"], base_apparent_power)

# Retry logic for MQTT connection
def connect_mqtt():
    client = mqtt.Client()
    while True:
        try:
            client.connect(MQTT_BROKER, MQTT_PORT)
            logging.info("Connected to MQTT broker.")
            return client
        except Exception as e:
            logging.error(f"MQTT connection failed: {e}, retrying in 5 seconds...")
            time.sleep(5)

# Initialize MQTT client
client = connect_mqtt()

while True:
    try:
        # Random uncertainties
        Pmu_mag_unc = random.uniform(0.65, 0.75)
        Pmu_phase_unc = random.uniform(-5, 5)

        # Power flow
        results_pf, _ = nv_powerflow.solve(system)

        # Measurements
        measurements_set = measurement.MeasurementSet()
        for node in results_pf.nodes:
            measurements_set.create_measurement(
                node.topology_node,
                measurement.ElemType.Node,
                measurement.MeasType.Vpmu_mag,
                np.absolute(node.voltage_pu),
                Pmu_mag_unc,
            )
            measurements_set.create_measurement(
                node.topology_node,
                measurement.ElemType.Node,
                measurement.MeasType.Vpmu_phase,
                np.angle(node.voltage_pu),
                Pmu_phase_unc,
            )
        measurements_set.meas_creation()

        # State estimation
        state_estimation_results = nv_state_estimator.DsseCall(system, measurements_set)

        # Prepare results for publishing
        result_data = [
            {"node": str(node.topology_node.uuid), "voltage": str(node.voltage)}
            for node in state_estimation_results.nodes
        ]

        # Publish results
        client.publish(MQTT_TOPIC, json.dumps(result_data))
        logging.info("State estimation results published.")
        print("State estimation results published.")

        # Wait for the next iteration
        time.sleep(10)

    except Exception as e:
        logging.error(f"Error in state estimation loop: {e}")
        time.sleep(5)  # Retry after a short delay
