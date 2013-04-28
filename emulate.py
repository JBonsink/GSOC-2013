# !/usr/bin/env python
# !/usr/bin/env pypy

# node_type = 'Server'
import argparse
import core.real
import util as ut

class Emulator:           
    def run_server(scen):
        node = core.real.PhyNode()
        cmd = scen.ServerCMD()
        cmd.install(node)
        node.start()    
    
    def run_client(scen):
        node = core.real.PhyNode()
        ccmd = scen.ClientCMD()
        ccmd.install(node)
        node.start()
    
    def run_botmaster(scen):
        node = core.real.PhyNode()
        ccmd = scen.BotMaster()
        ccmd.install(node)
        node.start()
    
    run_map = {
        'server':run_server,
        'client':run_client,
        'botmaster':run_botmaster,
    }

def parse_arguments():
    parser = argparse.ArgumentParser(description='imalse')
    
    scenario_ops = ut.get_scenario_option()
    parser.add_argument('-s', '--scenario', default='None',
            help='specify the scenario you want to execute. Scenearios availiable are: %s'%(scenario_ops )
            )
    
    parser.add_argument('-r', '--role', default='None',
            help='specify the role you want to emulate, 1.[server], 2.[client], 3.[botmaster]'
            )
    args = parser.parse_args()
    if args.scenario not in scenario_ops:
        parser.print_help()
        exit()
    return args

args = parse_arguments()
scen = ut.load_module(args.scenario)
print scen
Emulator().run_map[args.role](scen)

