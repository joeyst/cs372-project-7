import json
from netfuncs import *

def get_routers_data(path):
  return read_routers(path)['routers']

def get_src_dest_pairs(path):
  return read_routers(path)['src-dest']

class Network:
  def __init__(self, routers_dict):
    self.routers = self.parse_routers_dict(routers_dict)
    self.queue = []

  def parse_routers_dict(self, routers_dict):
    parsed_routers = {}
    for curr, data in routers_dict.items():
      curr_router = Router(curr)
      curr_router.add_conns(data['connections'])
      parsed_routers[curr] = curr_router
    return parsed_routers

  def next(self):
    assert(len(self.queue) != 0)
    q = self.queue.pop(0)

    update_data = self.routers[q].get_update_data(self.routers.deepcopy())
    for i in range(len(update_data['conns'])):
      # keeping for a bit in case code doesn't mutate 
      # temp_router           = self.routers[update_data['conns'][i]].deepcopy()
      # temp_router.path      = update_data['paths'][i]
      # temp_router.path_cost = float(update_data['costs'][i])
      # self.routers[update_data['conns'][i]] = temp_router

      curr_conn = update_data['conns'][i]
      self.routers[curr_conn].path      = update_data['paths'][i]
      self.routers[curr_conn].path_cost = update_data['costs'][i]
      if not curr_conn in self.queue:
        queue.append(curr_conn)

class Router:
  def __init__(self, ip, conns=[], conn_weights=[], interfaces=[], netmasks=[], path_cost=float('inf')):
    self.ip = ip
    self.conns = conns
    self.conn_weights = conn_weights
    self.interfaces = interfaces
    self.netmasks = netmasks
    self.path = []
    self.path_cost = path_cost

  def get_update_data(self, router_dict):
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

  def add_conns(self, conns_data):
    for conn_data in conns_data.items():
      self.add_conn(conn_data)

  def add_conn(self, conn_data):
    self._assert_lengths()
    address, data  = conn_data
    
    self.conns.append(address)
    self.conn_weights.append(float(data['ad']))
    self.interfaces.append(data['interface'])
    self.netmasks.append(data['netmask'])

  def _assert_lengths(self):
    assert len(self.conns) == len(self.conn_weights) and len(self.conn_weights) == len(self.interfaces) and len(self.interfaces) == len(self.netmasks)


def display_pairs(pairs):
  print ("   source              dest")
  for source, dest in pairs:
    print("{:18} {:18}".format(source, dest))

def main(argv):
  routers, pairs = get_routers_data(argv[1]), get_src_dest_pairs(argv[1])
  network = Network(routers)
  display_pairs(pairs)

if __name__ == "__main__":
    sys.exit(main(sys.argv))