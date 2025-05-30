import os
import socket
import time
import importlib
import datetime

# Define the IP address and port of Machine A
machine_a_ip = '192.168.0.177'
machine_a_port = 65432

# Define the buffer in milliseconds
buffer_milliseconds = 50  # 50 milliseconds

# Define a dictionary to store the trigger flags for each target timecode
trigger_flags = {}

# Define a variable to store the last triggered timecode
last_triggered_timecode = None

def remove_colons(timecode):
    return timecode.replace(":", "")

def within_buffer(received_timecode, target_timecode, buffer_milliseconds):
    received_timecode_int = int(remove_colons(received_timecode))
    target_timecode_int = int(remove_colons(target_timecode))
    return abs(received_timecode_int - target_timecode_int) <= buffer_milliseconds

def load_timecodes(filename):
    with open(filename, 'r') as file:
        timecodes = []
        for line in file:
            parts = line.strip().split(',')
            if len(parts) == 2:
                timecodes.append({'timecode': parts[0], 'action': parts[1]})
                # Initialize trigger flags for each target timecode
                trigger_flags[parts[0]] = False
            else:
                timecodes.append({'timecode': parts[0], 'action': ''})
                trigger_flags[parts[0]] = False
    return timecodes

def execute_action(action):
    try:
        eval(action)
    except Exception as e:
        print(f"Error executing action: {e}")

def reset_trigger_flags():
    # Reset all trigger flags
    for key in trigger_flags:
        trigger_flags[key] = False

def read_timecode_over_network(host, port):
    # Load the list of target timecodes and actions from the file
    target_timecodes = load_timecodes('timecodes.txt')

    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.settimeout(5)  # Set a timeout for connection attempts
                client_socket.connect((host, port))
                print(f"Connected to server at {host}:{port}")

                while True:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    received_data = data.decode('utf-8').strip().split('\n')

                    for received_timecode in received_data:
                        # Check if any of the received timecodes are within the buffer range of any target timecode
                        for target in target_timecodes:
                            if within_buffer(received_timecode, target['timecode'], buffer_milliseconds):
                                # Check if the trigger flag for this timecode is not set
                                if not trigger_flags[target['timecode']]:
                                    # Get the current time with microseconds
                                    current_time = datetime.datetime.now().strftime("%H:%M:%S:%f")[:-3]

                                    print(f"Timecode triggered: {received_timecode} - Current time: {current_time}")
                                    if target['action']:
                                        execute_action(target['action'])
                                    # Set the trigger flag for this timecode
                                    trigger_flags[target['timecode']] = True

                        # Reset trigger flags within the buffer window around 00:00:00:000
                        if within_buffer(received_timecode, "00:00:00:000", buffer_milliseconds * 4):
                            reset_trigger_flags()

        except KeyboardInterrupt:
            print("Interrupted by user")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Retrying connection...")
            time.sleep(5)  # Wait for 5 seconds before retrying connection

# Dynamically import custom functions
custom_functions = importlib.import_module('custom_functions')
all_names = dir(custom_functions)
function_names = [name for name in all_names if callable(getattr(custom_functions, name))]
for name in function_names:
    globals()[name] = getattr(custom_functions, name)

# Example usage
read_timecode_over_network(machine_a_ip, machine_a_port)
