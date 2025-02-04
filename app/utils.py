import os


def get_project_root():
    """Returns the root directory of the project."""
    return os.path.dirname(os.path.abspath(__file__))


def is_port_in_use(port):
    """Checks if a given port is already in use within the Docker container."""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0
