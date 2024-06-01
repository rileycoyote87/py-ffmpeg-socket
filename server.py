import subprocess
import re
import socket
import threading

# Define the IP address and port for broadcasting
broadcast_host = '192.168.0.177'  # Use '0.0.0.0' to listen on all available interfaces
broadcast_port = 65432

# Define the file path
video_file_path = r'C:\Users\cs-server\Desktop\chapter3.mp4'

def seconds_to_hms_milliseconds(seconds):
	h = int(seconds // 3600)
	m = int((seconds % 3600) // 60)
	s = int(seconds % 60)
	ms = int((seconds - int(seconds)) * 1000)
	return f"{h:02}:{m:02}:{s:02}.{ms:03}"

def broadcast_timecode(host, port):
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    	server_socket.bind((host, port))
    	server_socket.listen()
    	print(f"Server listening on {host}:{port}")

    	while True:
        	conn, addr = server_socket.accept()
        	print(f"Connected by {addr}")

        	try:
            	while True:
                	line = process.stderr.readline()
                	if not line:
                    	break

                	time_match = re.match(r'^\s*([\d\.]+)\s+', line)
                	if time_match:
                    	current_time = float(time_match.group(1))
                    	current_time_hms_ms = seconds_to_hms_milliseconds(current_time)
                    	try:
                        	conn.sendall((current_time_hms_ms + '\n').encode('utf-8'))
                    	except Exception as e:
                        	print(f"Error sending data: {e}")
                        	break
        	finally:
            	conn.close()

# Example usage with raw string to handle backslashes
broadcast_thread = threading.Thread(target=broadcast_timecode, args=(broadcast_host, broadcast_port))
broadcast_thread.start()

# Run ffplay in the main thread
command = ['ffplay', '-hide_banner', '-i', video_file_path, '-v', 'quiet', '-stats', '-loop', '0']
process = subprocess.Popen(command, stderr=subprocess.PIPE, text=True, universal_newlines=True)

try:
	while True:
    	line = process.stderr.readline()
    	if not line:
        	break
except KeyboardInterrupt:
	process.terminate()
	process.wait()
except Exception as e:
	print(f"An error occurred: {e}")
	process.terminate()
	process.wait()

# Wait for the broadcast thread to finish
broadcast_thread.join()


