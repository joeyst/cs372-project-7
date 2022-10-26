from netfuncs import *
from copy import deepcopy

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
      curr_router = make_router(curr, data['netmask'], data['if_count'], data['if_prefix'])
      curr_router.add_conns(data['connections'], True)
      parsed_routers[curr] = deepcopy(curr_router)
    return parsed_routers

  def dijk(self, start, finish, interface=False, display=True, verbose=False):
    # get start router name, `Router`, and netmask 
    start_subnet_name = self.find_subnet(start)
    start_subnet_router = self.routers[start_subnet_name]
    start_netmask = get_subnet_mask_value(start_subnet_router.netmask)

    # get finish router name, `Router`, and netmask 
    finish_subnet_name = self.find_subnet(finish)
    finish_subnet_router = self.routers[finish_subnet_name]
    finish_netmask = get_subnet_mask_value(finish_subnet_router.netmask)

    # get numeric values of start and finish router masks 
    start_masked = start_netmask & ipv4_to_value(start)
    finish_masked = finish_netmask & ipv4_to_value(finish)

    # if have the same router, return immediately 
    if start_masked == finish_masked:
      temp_router = Router(start, start_subnet_router.netmask, start_subnet_router.if_count, start_subnet_router.if_prefix, [], [], [], [], 0)
      if display:
        print("{:11} {}".format("Sender", start))
        print("{:11} {}".format("Receiver", finish))
        temp_router.display(verbose)
      if interface:
        print("{:11} {}".format("Interface", "Local"))
      return temp_router

    self.reset()
    assert(len(self.queue) == 0)

    if start not in self.routers.keys():
      start_router = self.find_subnet(start)
    else:
      start_router = start

    if finish not in self.routers.keys():
      finish_router = self.find_subnet(finish)
    else:
      finish_router = finish

    self.routers[start_router].path_cost = 0

    self.queue.append(start_router)
    while (len(self.queue) != 0):
      self.next()
      while finish_router in self.queue:
        self.queue.remove(finish_router)

    if start not in self.routers.keys():
      self.routers[finish_router].path = [start_router] + self.routers[finish_router].path

    if finish not in self.routers.keys():
      self.routers[finish_router].path.append(finish)

    if display:
      print("{:11} {}".format("Sender", start))
      print("{:11} {}".format("Receiver", finish))
      self.routers[finish_router].display(verbose)
    if interface:
      print("{:11} {}".format("Interface", self.collect_interfaces(self.routers[finish_router].path, start)))
    print("\n\n\n")

    return self.routers[finish_router]

  def collect_interfaces(self, path, start):
    interfaces = []
    if start.split(".")[-1] == "1":
      index_of_interface = self.routers[start].conns.index(path[0])
      interfaces.append(self.routers[start].interfaces[index_of_interface])
    else:
      interfaces.append((start, "Local"))
    
    for i in range(1, len(path)):
      prev_index = 0
      if path[i].split(".")[-1] == "1":
        index_of_interface = self.routers[path[i - 1]].conns.index(path[i])
        interfaces.append((path[i], self.routers[path[i - 1]].interfaces[index_of_interface]))
      else:
        interfaces.append((path[i], "Local"))
        continue

    return interfaces

  def find_subnet(self, ip):
    for name, router in self.routers.items():
      if router.equal_subnets(ip):
        return name

  def reset(self):
    for name, router in self.routers.items():
      self.routers[name].path = []
      self.routers[name].path_cost = float('inf')

  def next(self):
    assert(len(self.queue) != 0)
    q = self.queue.pop(0)

    update_data = self.routers[q].get_update_data(deepcopy(self.routers))

    for i in range(len(update_data['conns'])):
      curr_conn = update_data['conns'][i]
      self.routers[curr_conn].path      = update_data['paths'][i]
      self.routers[curr_conn].path_cost = update_data['costs'][i]
      if not curr_conn in self.queue:
        self.queue.append(curr_conn)

def make_router(ip, netmask, if_count, if_prefix):
  return deepcopy(Router(ip, netmask, if_count, if_prefix))

class Router:
  def __init__(self, ip, netmask, if_count, if_prefix, conns=[], conn_weights=[], interfaces=[], netmasks=[], path_cost=float('inf')):
    self.ip = ip
    self.netmask = netmask
    self.if_count = if_count
    self.if_prefix = if_prefix
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
      if self.faster_path(router_dict[conn].path_cost, weight):
        update_data['conns'].append(conn)
        update_data['costs'].append(self.path_cost + weight)
        update_data['paths'].append(self.path + [conn])
        update_data['interfaces'].append(self.interfaces)
    
    return update_data

  def display(self, verbose=False): 
    print("{:11} {}".format("Rec Router",     self.ip))
    print("{:11} {}".format("Cost",   self.path_cost))
    print("{:11} {}".format("Subnet", self.subnet()))
    print("{:11} {}".format("Path",   self.path))

    if verbose: 
      print("")
      print("{:11} {}".format("Connections", self.conns))
      print("{:11} {}".format("Weights",     self.conn_weights))

  def subnet(self):
    return value_to_ipv4(ipv4_to_value(self.ip) & get_subnet_mask_value(self.netmask))

  def equal_subnets(self, other_ip):
    return ipv4_to_value(self.subnet()) == (ipv4_to_value(other_ip) & get_subnet_mask_value(self.netmask))

  def faster_path(self, other_cost, weight):
    return(self.path_cost + weight < other_cost)

  def add_conns(self, conns_data, override=False):
    for conn_data in conns_data.items():
      self.add_conn(conn_data, override)

  def add_conn(self, conn_data, override=False):
    self._assert_lengths(override)
    address, data = conn_data
    self.conns.append(address)
    self.conn_weights.append(float(data['ad']))
    self.interfaces.append(data['interface'])
    self.netmasks.append(data['netmask'])

  def _assert_lengths(self, override=False):
    if override == False:
      assert len(self.conns) == len(self.conn_weights) and len(self.conn_weights) == len(self.interfaces) and len(self.interfaces) == len(self.netmasks)

def display_pairs(pairs):
  print ("   source              dest")
  for source, dest in pairs:
    print("{:18} {:18}".format(source, dest))

def find_paths(file_path, display=True, verbose=False):
  routers, pairs = get_routers_data(file_path), get_src_dest_pairs(file_path)
  network = Network(routers)
  for [start, destination] in pairs:
    network.dijk(start, destination, interface=True, display=True, verbose=False)

def main(argv):
  find_paths(argv[1])
 
if __name__ == "__main__":
    sys.exit(main(sys.argv))
