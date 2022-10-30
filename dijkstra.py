import sys
import json
import math  # If you want to use math.inf for infinity

def ipv4_to_value(ipv4_addr):

    #Split on the dot
    ipv4_str = ipv4_addr.split(".")
    #Turn array of strings into list of ints
    ipv4_int = list(map(int, ipv4_str))
    #Go through the list and bit shift it by 8 times it's index from the right
    for i in list(range(0,len(ipv4_int))):
        #Index 0 is most significant, index at len-1 is least, that's why subtract i from max index
        #Index 0 = bit shift 3-0 * 8 = 24, index 3 = 3-3 * 8 = 0
        ipv4_int[i] = ipv4_int[i] << ((len(ipv4_int)-1-i)*8)

    #Bitwise OR all the values in the array
    value = ipv4_int[0]
    for i in list(range(1,len(ipv4_int))):
        value = value | ipv4_int[i]
    return value

def get_subnet_mask_value(slash):

    #Split whats passed in on the slash and grab the value to the right of the slash
    network = slash.split('/')
    network = int(network[1])
    #Host bits are 32 minus the network bits
    host = 32-network
    #Thinking in binary, get a string of n 1s where n = network
    mask = (2**network)-1
    #Add host number of 0s by shifting it over host times
    return mask << host

def ips_same_subnet(ip1, ip2, slash):

    subnet_mask = get_subnet_mask_value(slash)

    ipv4_1 = ipv4_to_value(ip1)
    ipv4_2 = ipv4_to_value(ip2)
    
    #And the ip value and subnet mask value to get the network
    val1 = ipv4_1 & subnet_mask
    val2 = ipv4_2 & subnet_mask
    return (val1 == val2)

def find_router_for_ip(routers, ip):

    for key, value in routers.items():
        #key is the ip, and value['netmask'] is it's corresponding slash value
        if ips_same_subnet(key,ip,value['netmask']):
            return key

    return None

def dijkstras_shortest_path(routers, src_ip, dest_ip):
    """
    This function takes a dictionary representing the network, a source
    IP, and a destination IP, and returns a list with all the routers
    along the shortest path.

    The source and destination IPs are **not** included in this path.

    Note that the source IP and destination IP will probably not be
    routers! They will be on the same subnet as the router. You'll have
    to search the routers to find the one on the same subnet as the
    source IP. Same for the destination IP. [Hint: make use of your
    find_router_for_ip() function from the last project!]

    The dictionary keys are router IPs, and the values are dictionaries
    with a bunch of information, including the routers that are directly
    connected to the key.

    This partial example shows that router `10.31.98.1` is connected to
    three other routers: `10.34.166.1`, `10.34.194.1`, and `10.34.46.1`:

    {
        "10.34.98.1": {
            "connections": {
                "10.34.166.1": {
                    "netmask": "/24",
                    "interface": "en0",
                    "ad": 70
                },
                "10.34.194.1": {
                    "netmask": "/24",
                    "interface": "en1",
                    "ad": 93
                },
                "10.34.46.1": {
                    "netmask": "/24",
                    "interface": "en2",
                    "ad": 64
                }
            },
            "netmask": "/24",
            "if_count": 3,
            "if_prefix": "en"
        },
        ...

    The "ad" (Administrative Distance) field is the edge weight for that
    connection.

    **Strong recommendation**: make functions to do subtasks within this
    function. Having it all built as a single wall of code is a recipe
    for madness.
    """

    src_router = find_router_for_ip(routers, src_ip)
    dst_router = find_router_for_ip(routers, dest_ip)

    if ips_same_subnet(src_router, dst_router, "/24"):
        return []
    
    to_visit = set()
    distance = {}
    parent = {}

    for vertex in routers:
        parent[vertex] = None
        distance[vertex] = math.inf
        to_visit.add(vertex)

    distance[src_router] = 0
    while len(to_visit) != 0:

        current_node = next(iter(to_visit))
        for vertex in to_visit:
            if distance[vertex] < distance[current_node]:
                current_node = vertex
        to_visit.remove(current_node)


        for neighbor in routers[current_node]['connections']:
            if neighbor in to_visit:
                dist = distance[current_node] + routers[current_node]['connections'][neighbor]['ad']
                if dist < distance[neighbor]:
                    distance[neighbor] = dist
                    parent[neighbor] = current_node

    current_node = dst_router
    path = []
    while current_node != src_router:
        path.append(current_node)
        current_node = parent[current_node]
    path.append(src_router)

    path.reverse()
    return path
#------------------------------
# DO NOT MODIFY BELOW THIS LINE
#------------------------------
def read_routers(file_name):
    with open(file_name) as fp:
        data = fp.read()

    return json.loads(data)

def find_routes(routers, src_dest_pairs):
    for src_ip, dest_ip in src_dest_pairs:
        path = dijkstras_shortest_path(routers, src_ip, dest_ip)
        print(f"{src_ip:>15s} -> {dest_ip:<15s}  {repr(path)}")

def usage():
    print("usage: dijkstra.py infile.json", file=sys.stderr)

def main(argv):
    try:
        router_file_name = argv[1]
    except:
        usage()
        return 1

    json_data = read_routers(router_file_name)

    routers = json_data["routers"]
    routes = json_data["src-dest"]

    find_routes(routers, routes)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
    
