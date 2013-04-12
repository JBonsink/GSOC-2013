"""
this file describe the netns3 experiment for imalse
"""
from core.ns3.netns3 import NetnsExperiment
from core.ns3.Node import ImalseNetnsNode
import ns3
from util import load_module

from util import get_scenario_option

NODE_NUM = 0

# for test, just select the first node as server, the second node as botmaster, all other nodes
# are clients
class ImalseNetnsExperiment(NetnsExperiment):
    """Base Class for Imalse Experiment
    It is based on the NetnsExperiment
    """
    server_id_set = [0]
    botmaster_id_set = [1]
    client_id_set = [2, 3, 4]
    def __init__(self, *args, **kwargs):
        # super(ImalseExperiment, self).__init__(*args, **kwargs)
        super(ImalseNetnsExperiment, self).__init__(*args, **kwargs)
        self._init()

    def initparser(self, parser):
        super(ImalseNetnsExperiment, self).initparser(parser)

        scenario_ops = get_scenario_option()
        parser.add_option('-s', '--scenario', dest="scenario",
                default='ddos_ping_flooding',
                help='specify the scenario you want to execute. Scenearios availiable are: %s'%(scenario_ops),
                )

    def _init(self): pass
    def setup(self): pass

    @property
    def id_set(self):
        return self.server_id_set + self.botmaster_id_set + self.client_id_set

    def get_node(self, i):
        """get ith nodes"""
        return self.nodes[i]

    @property
    def node_num(self):
        return len(self.nodes)

    def node_run(self, node, *args, **kwargs):
        """run a command on a specific node"""
        node.cmd_set._trigger(*args, **kwargs)

    def _install_cmds(self, srv_addr=None):
        """install different command set to nodes according to their type
        can manually set the server address
        """
        scen = load_module(self.options.scenario)
        botmaster_desc = scen.botmaster_desc
        server_desc = scen.server_desc
        client_desc = scen.client_desc
        # botmaster_desc['srv_addr'] = "10.1.1.1"
        print 'srv_addr, ', srv_addr
        if srv_addr:
            botmaster_desc['srv_addr'] = srv_addr
            server_desc['srv_addr'] = srv_addr
            client_desc['srv_addr'] = srv_addr

        for i in xrange(self.node_num):
            if i in self.botmaster_id_set:
                cmd = scen.BotMaster(botmaster_desc)
            elif i in self.server_id_set:
                cmd = scen.ServerCMD(server_desc)
            elif i in self.client_id_set:
                cmd = scen.ClientCMD(client_desc)
            else:
                continue
            cmd.install(self.get_node(i))

    def _get_server_addr(self):
        """The all the server address"""
        addr_set = []
        for i in self.server_id_set:
            ipv4Addr = self.get_node(i).GetObject(ns3.TypeId.LookupByName("ns3::Ipv4")).GetAddress(1, 0)
            addr_set.append(ipv4Addr)
        return addr_set

    def _get_server_nodes(self):
        return [self.get_node(i) for i in self.server_id_set]

    def _set_server_info(self):
        """Only Set Server information for simulated nodes"""
        server_addr_set = self._get_server_addr()
        server_set = self._get_server_nodes()
        for i in xrange(self.node_num):
            if i in self.server_id_set or self.get_node(i).NODE_TYPE.startswith('real'):
                continue
            self.get_node(i).server_addr_set = server_addr_set
            self.get_node(i).server_set = server_set

    def print_srv_addr(self):
        """print out the address of the server"""
        for i in self.server_id_set:
            ipv4Addr = self.get_node(i).GetObject(ns3.TypeId.LookupByName("ns3::Ipv4")).GetAddress(1, 0)
            print 'The server addr of server [%i ]: '%(i), ipv4Addr

    @staticmethod
    def NodeCreator():
        global NODE_NUM
        NODE_NUM += 1
        name = "n%s" %NODE_NUM
        return ImalseNetnsNode(name, logfile = "/tmp/%s.log" % name)
