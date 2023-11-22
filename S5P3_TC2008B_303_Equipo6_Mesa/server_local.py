# server.py
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from warehouse import Warehouse
from browserUI import server
import logging
import time

# RUN THIS FILE TO OPEN SERVER

# Size of the board:
width = 50
height = 50
num_robots = 20

# Initiate model
Model = Warehouse(width, height, num_robots)

#server.launch(open_browser=True)

class Server(BaseHTTPRequestHandler):

    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        logging.info(f"GET request,\nPath: {str(self.path)}\nHeaders:\n{str(self.headers)}")
        self._set_response()
        self.wfile.write(f"GET request for {self.path}".encode('utf-8'))

    def do_POST(self):
        try:
            # Add a delay to control the rate at which the model progresses
            time.sleep(0.5)  # Adjust the sleep time as needed
            Model.step()
            positions_json = Model.positions_to_json()
            print(f"Sending positions: {positions_json}")
            # Send the JSON response
            self._set_response()
            self.wfile.write(positions_json.encode('utf-8'))
        except Exception as e:
            print(f"Error processing POST request: {e}")
            self.send_error(400, "Bad Request")

def run(server_class=HTTPServer, handler_class=Server, port=8585):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print("Starting httpd...\n")
    
    # Create a thread to run the server
    server_thread = Thread(target=httpd.serve_forever)
    server_thread.daemon = True  # Daemonize thread to make sure it's terminated when the main program exits
    server_thread.start()
    
    try:
        # Keep the main thread alive while the server thread is running
        while True:
            time.sleep(1)  # Add a delay to control the rate at which the main thread checks
    except KeyboardInterrupt:
        pass

    httpd.server_close()
    print("Stopping httpd...\n")

if __name__ == '__main__':
    run()
