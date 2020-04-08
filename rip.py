import sys
import socket
import select
import datetime
import time

HOST = "127.0.0.1"



class Demon:
    def __init__(self, id, inputs, outputs, timer=None):
        self.id = id
        self.inputs = inputs
        self.outputs = outputs
        self.timer = timer

    def __repr__(self):
        return "{}".format((self.id, self.inputs, self.outputs, self.timer))
    
    """router1[router2.id] .  returns Output_Port"""
    def __getitem__(self, router_id):            
        for i in self.outputs:
            if i.peer_id == router_id:
                return i
    def getOutputPorts(self):
        ports = []
        for output in self.outputs:
            ports.append(output.port)
        return ports

class Outport_Port:
    def __init__(self, port, metric, peer_id):
        self.port = port
        self.metric = metric
        self.peer_id = peer_id

    def __repr__(self):
        return "{}".format((self.port, self.metric, self.peer_id))

class Routing_Table(list) :     # acts like a dictionary in terms of indexing
    def __init__(self):         
        list.__init__(self)

    def __getitem__(self, router_id):            
        for entry in self:
            if entry.router == router_id:
                return entry

    def __setitem__(self, router_id, new_data):         # new_data = (distance, nexthop)
        for entry in self:
            if entry.router == router_id:       
                entry.distance = new_data[0]
                entry.nexthop = new_data[1]
                break

    def __repr__(self):
        if len(self) == 0:
            return "[]"
        result = "\n"
        for entry in self:
            result += "     {}\n".format(entry)
        return "[{}]".format(result)


class Table_Entry:
    """
    page 8 says entry could have 
     - address: in IP implementations of these algorithms, this will be
     the IP address of the host or network.

    - router: the first router along the route to the destination.

    - interface: the physical network which must be used to reach the
        first router.

    - metric: a number, indicating the distance to the destination.

    - timer: the amount of time since the entry was last updated.
   """
    def __init__(self, router, distance, nexthop):
        self.router = router
        self.distance = distance
        self.nexthop = nexthop

    def __repr__(self):
        return "dest: {}, dist: {}, next hop: {}".format(self.router, self.distance, self.nexthop)


def bellman_ford(routing_table, id, response): 
    response       #uses the update/response packet data???
    if routing_table[id] is not None:
        k = None
        distance = min(routing_table[id].distance, routing_table[id].distance)
    pass
    
def message_header(command, version):
    """ pg 20
        command:
            1=request
            2=response
        version:
            always 2?
    """
    return command.to_bytes(1, byteorder='big') + version.to_bytes(1, byteorder='big') + (0).to_bytes(2, byteorder='big')

def message_entry(afi, ipv4_addr, metric):
    """pg 21"""
    return afi.to_bytes(2, byteorder='big') + (0).to_bytes(2, byteorder='big') 
    + ipv4_addr.to_bytes(4, byteorder='big') + (0).to_bytes(8, byteorder='big') + metric.to_bytes(4, byteorder='big')


#----------------------------------------------------------  
def get_inputs(line, output=0):           #set output to 1 for the outputs config line
    inputs = line.split(' ')[1:]
    
    for i in range(len(inputs)):

        inputs[i] = inputs[i].strip(",")
        if output == 1:                                
            inputs[i] = get_output_input(inputs[i])
        else:
            inputs[i] = int(inputs[i])

    return inputs
    
def get_output_input(data):
    data = data.split('-')
    
    for i in range(len(data)):
        data[i] = int(data[i])
    return Outport_Port(data[0], data[1], data[2])
#----------------------------------------------------------    
# Validation checks (not complete)
def valid_config(router_id, demons, input_ports, output_ports):
    return unique_valid_id(router_id, demons) and valid_ports(input_ports, output_ports)

def unique_valid_id(router_id, demons):
    try:
        if router_id <= 0:
            print("router-id cannot be less than 0")
            sys.exit()
    except TypeError:
        print("router-id must be an integer")
        sys.exit()
    for demon in demons:
        if demon.id == router_id:
            print("router-id must be unique")
            sys.exit()
    return True


def valid_ports(input_ports, output_ports):
    try:
        for port in input_ports:
            if not (1024 <= port <= 64000):
                print("input-ports must be between 1024 and 64000")
                sys.exit()
    except TypeError:
        print("input-ports must be an integer")
        sys.exit()
    for port in output_ports:
        try:
            if not (1024 <= port.port <= 64000):
                print("output-ports must be an integer between 1024 and 64000")
                sys.exit()
            if port.port in input_ports:          # input port cannot be an output port
                print("input cannot port cannot be an output port")
                sys.exit()
        except TypeError:
            print("output-ports must be an integer")
            sys.exit()
        #if not (0 <= port.metric <= 15):           # metric bounds between 0 and ?(not sure) 
            #return False
        # Other checks

        ### 2 output ports going to the same router checker??? ###
    return True

#---------------------------------------------------------------------------------------------------------  


def get_demon(configs, demons):
    router_id = None
    input_ports = None
    output_ports = None

    for i in range(len(configs)):
        configs[i] = configs[i].rstrip()
        #print(configs[i])
        if configs[i].startswith("router-id:"):
            router_id = get_inputs(configs[i])[0]
            #print(router_id)
        elif configs[i].startswith("input-ports:"):
            input_ports = get_inputs(configs[i])
            #print(input_ports)
        elif configs[i].startswith("outputs:"):
            output_ports = get_inputs(configs[i], 1)
            #print(output_ports)
        elif configs[i].startswith("update:"):
            update = get_inputs(configs[i])[0]
            #print(update)

    if (router_id is None or input_ports is None or output_ports is None):      # Won't be able to detect errors in Config file that is formatted incorrect
        print("Mandatory parameter/s missing. requires router-id, input-ports, outputs")
        sys.exit()
    print("loaded values")
    print(router_id, input_ports,output_ports)
    print("")
    if valid_config(router_id, demons, input_ports, output_ports):
        return Demon(router_id, input_ports, output_ports, update)
    
                

def get_all_demons():
    demons = []
    demon = readconf(demons)

    if demon is None: 
        print("\nCould not use file '{}'\n".format(sys.argv[1])) 
        sys.exit()
    demons.append(demon)
    return demons
  
def readconf(demons):
    print("\n******trying to open file******\n")
    file = open("./Config/" + sys.argv[1], "r")

    configs = file.readlines()

    for x in configs:
        print(x)

    print("********************************\n")

    demons = get_demon(configs, demons)

    return demons
      

def inputSockets(deamon):
    print("")
    print("Starting input socket construction.\n")
    socket_values = deamon.inputs
    sockets = []

    for value in socket_values:
        print("Building socket " + str(value))
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((HOST, value))
        sockets.append(sock)
    print("\ninput socket construction done.\n" + str(len(sockets)) + " scokets have been made.")
    
    return sockets  

 
def outputsockets(demon):
    print("")
    print("Starting output socket construction.\n")
    socket_values = demon.outputs
    sockets = []
    
    for value in socket_values:
        print("Building socket " + str(value.port))
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #sock.connect((HOST, value.port))
        sockets.append((sock, value.port))
    print("\nOutput socket construction done.\n" + str(len(sockets)) + " scokets have been made.")
    
    return sockets 

def main():
    print("starting rip")

    """     how Routing_Table and Table_Entry work
    red = Routing_Table()
    print(red)
    entry = Table_Entry(1, 2, 3)
    print(entry)
    red.append(entry)
    print(red)
    print(red[1])
    red[1] = 1239, 51
    print(red[1])
    print(red)
    """
    

    if (len(sys.argv) < 2):
        print("no config file")
        sys.exit()

    demons = get_all_demons()
    
    #print(demons[0].outputs)
    OutputSockets = outputsockets(demons[0])
    InputSockets = inputSockets(demons[0])
    

    Timer = demons[0].timer
    temp = 0
    while True:
        currentDT = datetime.datetime.now()
        print("\nHeart Beat: " + currentDT.strftime("%H:%M:%S"))

        #MAIN OUTPUT CODE
        if((time.time() - Timer) >= demons[0].timer):  
            for sock in OutputSockets:
                print("sending to port " + str(sock[1]))
                sock[0].sendto(str.encode("This is a test " + str(temp)), (HOST, sock[1]))
            temp += 1
            Timer = time.time()

        ##MAIN INPUT CODE
        ##-------------------------------------------------------------------------------
        # this will block until at least one socket is ready (uncomment the one you want)
            #no timeout
        #ready_socks,_,_ = select.select(sockets, [], []) 
            #timeout
        ready_socks,_,_ = select.select(InputSockets, [], [], 1) ##timeout is in seconds
        ##------------------------------------------------------------------------------
        for sock in ready_socks:
            data, addr = sock.recvfrom(1024) # This is will not block
            print ("received message:", data)
    


if __name__ == "__main__":
    main()
