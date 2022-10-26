import json
from netfuncs import *

def get_routers_data(path):
  return read_routers(path)['routers']

def get_src_dest_pairs(path):
  return read_routers(path)['src-dest']

class Network:
  def __init__(routers_dict):
    self.routers = self.parse_routers_dict(routers_dict)
    self.queue = []

  def parse_routers_dict(routers_dict):
    routers = {}
    for curr, data in routers_dict.items():
      curr_router = Router(curr)
      curr_router.add_conns(data['connections'])
      routers[curr] = curr_router
    return routers

class Router:
  def __init__(ip, conns=[], conn_weights=[], interfaces=[], path_cost=float('inf')):
    self.ip = ip
    self.conns = conns
    self.conn_weights = conn_weights
    self.interfaces = interfaces
    self.netmasks = netmasks
    self.path = []
    self.path_cost = path_cost

  def get_update_data(router_dict):
    update_data = {
      'conns': [],
      'costs': [],
      'paths': [],
      'interfaces': []
    }

    for conn, weight, interface in zip(self.conns, self.conn_weights, self.interfaces):
      if self.faster_path(router_dict[conn].path_cost):
        update_data['conns'].append(conn)
        update_data['costs'].append(self.path_cost + weight)
        update_data['paths'].append(self.path + [conn])
        update_data['interfaces'].append(self.interfaces)
    
    return update_data

  def add_conns(conns_data):
    for conn_data in conns_data.items():
      self.add_conn(conn_data)

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