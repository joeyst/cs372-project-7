import json
from netfuncs import *

def get_routers_data(path):
  return read_routers(path)['routers']

def get_src_dest_pairs(path):
  return read_routers(path)['src-dest']

class Router:
  def __init__(ip, conns, conn_weights, interfaces):
    self.ip = ip
    self.conns = conns
    self.conn_weights = conn_weights
    self.interfaces = interfaces
    self.netmasks = netmasks
    self.path = []
    self.path_cost = float('inf')

  def try_conns(router_dict):
    outdated_conns = []
    outdated_conn_weights = []
    outdated_interfaces = []

    for conn, weight, interface in zip(self.conns, self.conn_weights, self.interfaces):
      if self.faster_path(router_dict[conn].path_cost):
        outdated_conns.append(conn)
        outdated_conn_weights.append(weight)
        outdated_interfaces.append(interface)
    
    return zip(outdated_conns, outdated_conn_weights, outdated_interfaces)

  def add_conn(conn_data):
    self._assert_lengths()
    (address, data),  = conn_data.items()
    
    self.conns.append(address)
    self.conn_weights.append(float(data['ad']))
    self.interfaces.append(data['interface'])
    self.netmasks.append(data['netmask'])

  def _assert_lengths():
    assert len(self.conns) == len(self.conn_weights) and len(self.conn_weights) == len(self.interfaces) and len(self.interfaces) == len(self.netmasks)


def display_pairs(pairs):
  print ("   source              dest")
  for source, dest in pairs:
    print("{:18} {:18}".format(source, dest))

def main(argv):
  routers, pairs = get_routers_data(argv[1]), get_src_dest_pairs(argv[1])
  display_pairs(pairs)

if __name__ == "__main__":
    sys.exit(main(sys.argv))