
"""
The setup file for the server.

Right now it only have one function that initializes the database.
"""

from server import init_db

if __name__ == '__main__':
    init_db()
