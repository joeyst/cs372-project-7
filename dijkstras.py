import json
from netfuncs import *

def get(path):
  return read_routers(path)['routers'], read_routers(path)['src-dest']

def display_pairs(pairs):
  print ("   source              dest")
  for source, dest in pairs:
    print("{:18} {:18}".format(source, dest))

def main(argv):
  routers, pairs = get(argv[1])

  display_pairs(pairs)

if __name__ == "__main__":
    sys.exit(main(sys.argv))