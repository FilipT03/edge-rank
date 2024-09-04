from cpp_module import *
from utils import merenje
from program import program

'''
This application is Linux only.
External modules used:
    pybind11, invoke, pickle

If the c++ module is not built, run in the terminal at project root:
    invoke all
'''

if __name__ == "__main__":
    program.start()
