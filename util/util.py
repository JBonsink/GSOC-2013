import settings
import sys
import os
from inspect import getmembers

def abstract_method():
    """ This should be called when an abstract method is called that should have been
    implemented by a subclass. It should not be called in situations where no implementation
    (i.e. a 'pass' behavior) is acceptable. """
    raise NotImplementedError('Method not implemented!')

class DataEndException(Exception):
    pass

def load_module(scenario):
    __import__('scenario.%s'%(scenario))
    scen = sys.modules['scenario.%s'%(scenario)]
    return scen

def get_scenario_option(scen_dir = settings.ROOT+'/scenario/'):
    return [f_name for f_name in os.listdir(scen_dir) if not \
            ( f_name.lower().endswith('py') or f_name.lower().startswith('.') or f_name.lower().endswith('pyc'))
            ]

def get_experiment_option(scen_dir = settings.ROOT+'/experiments/'):
    return [f_name[:-3] for f_name in os.listdir(scen_dir) if f_name.endswith('Experiment.py') ]

def print_members(cls):
    """for debug, print the member function of a class"""
    v = getmembers(cls)
    for vl in v:
        print vl[0]
