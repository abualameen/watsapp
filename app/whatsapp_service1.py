import subprocess
import os
import requests
from app.utils import get_project_root, is_port_in_use
import logging

logging.basicConfig(level=logging.DEBUG)

class WhatsAppService1:
    def __init__(self):
        self.node_server = None
        self.base_url = "http://localhost:3000"  # Docker exposes this internally

    def start(self):
        """Starts the Node.js server for WhatsApp-web.js integration."""
        if is_port_in_use(3000):
            print("Port 3000 is already in use. Please stop the conflicting process or check Docker configuration.")
            return

        node_path = os.path.join(get_project_root(), "whatsapp_server.js")
        if not os.path.exists(node_path):
            raise FileNotFoundError(f"{node_path} not found. Ensure whatsapp_server.js exists in the container.")

        try:
            self.node_server = subprocess.Popen(
                ["node", "whatsapp_server.js"],
                cwd=get_project_root(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print("Node.js server started successfully.")
        except FileNotFoundError:
            raise RuntimeError("Node.js is not installed or not found in the Docker image.")
        except Exception as e:
            raise RuntimeError(f"Error starting the WhatsApp service: {str(e)}")

    def stop(self):
        """Stops the Node.js server if running."""
        if self.node_server:
            self.node_server.terminate()
            print("Node.js server stopped.")
        else:
            print("No Node.js server is currently running.")

    def send_message(self, user_id, contact, message):
        """Sends a message via the Node.js server."""
        try:
            url = f"{self.base_url}/send-message"
            payload = {
                "userId": user_id,
                "to": contact,
                "text": message
            }
            logging.debug(f"payload: {payload}")
            response = requests.post(url, json=payload)
            logging.debug(f"rpo: {response}")
            response.raise_for_status()  # Raises an error for HTTP issues
            return response.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Error sending message: {str(e)}")