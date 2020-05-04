import sys
import socket
import select
import datetime
import time
import random

HOST = "127.0.0.1"
UNREACHABLE = 28            # 16 in documentation 


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
        self.last_response = time.time()

    def __repr__(self):
        return "|DEST: {} | DIST: {} | next hop: {}| last response timer: {}".format(self.router, self.distance, self.nexthop, int(time.time() - self.last_response))
    
    def timedOut(self, seconds):
        return int(time.time() - self.last_response) == seconds

    def garbage(self, timeout, seconds):
        return int(time.time() - self.last_response) >= seconds

#------------------------------------------------------------------------------------------------------------------

# ----------------------------- update_packet processing ---------------------------------------------------------- 
    




def message_header(command, own_router_id):
    """ pg 20
        command:
            1=request
            2=response

        router_id:
            The router id of this router 
    """
    version = 2
    return bytearray(command.to_bytes(1, byteorder='big') + version.to_bytes(1, byteorder='big') + own_router_id.to_bytes(2, byteorder='big'))

def message_entry(dest_router_id, metric):
    """pg 21"""
    afi = 2
    return bytearray(afi.to_bytes(2, byteorder='big') + (0).to_bytes(2, byteorder='big') 
    + dest_router_id.to_bytes(4, byteorder='big') + (0).to_bytes(8, byteorder='big') + metric.to_bytes(4, byteorder='big'))


def generate_update_packet(recieverId, id, table):
    """
        recieverId: The router id of reciever
        
        id: The router id of this router 
        table: This router's routing table

        returns: update packet
    """
    packet = message_header(2, id)
    print("\ngenerating Packet for router {}".format(recieverId))
    for entry in table:

        distance = UNREACHABLE
        if recieverId != entry.nexthop:
            distance = entry.distance
        packet += message_entry(entry.router, distance)

    return packet

#----------------------------------------------------------------------------------------------------------







def initial_entries(table, demon):
    """ adds neigbours listed in config file. This function is only used at the start of the program 
    before the infinite loop 

        table: This router's routing table
        demon: demon

        returns entries as a way to remember adj routers
    """
    entries = []
    for output in demon.outputs:
        table.append(Table_Entry(output.peer_id, output.metric, output.peer_id))
        entries.append(Table_Entry(output.peer_id, output.metric, output.peer_id))

    return entries


#----------------------------------------------------------------------------------------------------------


#-------------- Handling of recieved packets --------------------------------------------------------------


def read_packet(own_id, packet):
    """ gets list of entries to be compared with routing table
    
        packet: recieved from another router

        returns: list of entries 
    """
    entries = []
    try:
        # Header handling
        command = packet[0]                                 
        version = packet[1]
        sender_id = int.from_bytes(packet[2:4], "big")

        if version != 2:
            return None

        if command == 2:        # packet is a response

            # entry handling 
            ei = 4              # entry index  
            num_of_entries = int((len(packet) - 4)/20)
            for i in range(num_of_entries):
                
                # is valid format
                valid = (int.from_bytes(packet[ei:ei+2], "big") == 2    # AFI    
                and int.from_bytes(packet[ei+2:ei+4], "big") == 0       # must be zero
                and int.from_bytes(packet[ei+8:ei+16], "big") == 0)     # must be zero

                if valid:
                    router_id = int.from_bytes(packet[ei+4:ei+8], "big")
                    metric = int.from_bytes(packet[ei+16:ei+20], "big")
                    if router_id != own_id:
                        entries.append(Table_Entry(router_id, metric, sender_id))
                    ei += 20

            return sender_id, entries

        elif command == 1:         # packet is a request
            pass

    except IndexError:
        print("unable to read packet")
        return entries

def update_table(sender_id, table, entries, routerId, OutputSockets, adj):
    print(table)
    if table[sender_id] is None:
        for neighbour in adj: 
            if neighbour.router == sender_id:        
                table.append(Table_Entry(sender_id, neighbour.distance, sender_id))
                break

    else:
        table[sender_id].last_response = time.time()         # A packet has been recieved from this sender since the timeout
    table_change = False                       # bool for if there is a table change

    for entry in entries:
        

        if table[entry.router] is None:         # new router id added is added to table
            add_entry(table, entry)
        else:
            # bellman ford updates to table
            if bellman_ford(table, entry):
                table_change = True

    # TRIGGERED UPDATE
    if table_change:
        print(table)                                                # if there is a table change send
        print("A Table Change has occured that has made a route unreachable\nResending packets\n")
        send_update_packet(OutputSockets, routerId, table)



def add_entry(table, entry):
    print(table)
    dest = entry.router
    dist = entry.distance
    sender = entry.nexthop

    new_dist = dist + table[sender].distance
    if new_dist >= UNREACHABLE:
        return
    new_entry = Table_Entry(dest, new_dist, sender)
    table.append(new_entry)


def bellman_ford(routing_table, response_entry): 
    dest = response_entry.router
    dist = response_entry.distance
    response_sender = response_entry.nexthop
    original = routing_table[dest].distance
    original_nexthop = routing_table[dest].nexthop

    new_distance = min(dist + routing_table[response_sender].distance , routing_table[dest].distance)
    
    if new_distance >= UNREACHABLE:                         # calculated distance is infinity 
        routing_table[dest] = (UNREACHABLE, None)

    elif routing_table[dest].nexthop == response_sender and dist == UNREACHABLE:        # the router that you learned the route from has lost their link from that destianation
        routing_table[dest] = (UNREACHABLE, None)

    elif new_distance != routing_table[dest].distance:                                  # otherwise if new distance is smaller than one in table relace it (this if statement might be redundant!)
        routing_table[dest] = (new_distance, response_sender)
        routing_table[dest].last_response = time.time()

    elif original_nexthop == routing_table[dest].nexthop:
        routing_table[dest].last_response = routing_table[routing_table[dest].nexthop].last_response

  
    if routing_table[dest].nexthop != None:                                           # NEED TO RETEST THESE LINES 
        if routing_table[routing_table[dest].nexthop].distance == UNREACHABLE:
            routing_table[routing_table[dest]] = (UNREACHABLE, None)

    return original != routing_table[dest].distance and routing_table[dest].distance == UNREACHABLE
    


        
#-----------------------------------------------------------------------------------------------------------
  




#------------------------------ Reading config files and setup -----------------------------------------------------  



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


def valid_config(router_id, input_ports, output_ports):
    return valid_id(router_id) and valid_ports(input_ports, output_ports)


def valid_id(router_id):
    try:
        if router_id <= 0:
            print("router-id cannot be less than 0")
            sys.exit()
    except TypeError:
        print("router-id must be an integer")
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
        if not (0 <= port.metric < UNREACHABLE):           # metric bounds between 0 and ?(not sure) 
            print("metric must be positive integer and less than {}".format(UNREACHABLE))
            sys.exit()

    return True



def get_demon(configs):
    router_id = None
    input_ports = None
    output_ports = None

    for i in range(len(configs)):
        configs[i] = configs[i].rstrip()

        if configs[i].startswith("router-id:"):
            router_id = get_inputs(configs[i])[0]

        elif configs[i].startswith("input-ports:"):
            input_ports = get_inputs(configs[i])

        elif configs[i].startswith("outputs:"):
            output_ports = get_inputs(configs[i], 1)

        elif configs[i].startswith("update:"):
            update = get_inputs(configs[i])[0]

    if (router_id is None or input_ports is None or output_ports is None):      # Won't be able to detect errors in Config file that is formatted incorrect
        print("Mandatory parameter/s missing. requires router-id, input-ports, outputs")
        sys.exit()
    print("loaded values")
    print(router_id, input_ports,output_ports)
    print("")

    if valid_config(router_id, input_ports, output_ports):
        return Demon(router_id, input_ports, output_ports, update)
    else:
        print("\nCould not use file '{}'\n".format(sys.argv[1])) 
        sys.exit()

  
def readconf():
    print("\n******trying to open file******\n")
    file = open("./Config/" + sys.argv[1], "r")

    configs = file.readlines()

    for x in configs:
        print(x)

    print("********************************\n")

    demon = get_demon(configs)

    return demon
      
#-----------------------------------------------------------------------------------------------




#------------------------------ Port setup -----------------------------------------------------  
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
        sockets.append((value.peer_id, (sock, value.port)))
    print("\nOutput socket construction done.\n" + str(len(sockets)) + " scokets have been made.")
    
    return sockets 



#-----------------------------------------------------------------------------------------------





def timeout(entry, table):
    """ 
    checks for changes in the topology of the network whether or not routers have
    turned off

    using variable adj not sure if it's good, still looking for alternative
    adj:
        list of entries of adjacent routers
    """
    print("TIMEOUT")
    print()
    
    entry.distance = UNREACHABLE
    entry.nexthop = None
    entry.last_response = time.time()

    print(table)
    print()

def garbage_timeout(table, entry):
    print("GARBAGE TIMEOUT")
    print("entry has been unreachable for atleast 120 seconds")
    print(entry)
    table.remove(entry)



def send_update_packet(OutputSockets, routerId, table):
    """sends packets to adj routers on the ports given in the config file
    OutputSockets: 
        sockets to send packets to neighbours
    routerID: 
        ID of this router (sender)
    """

    for (recieverId, sock) in OutputSockets:
        packet = generate_update_packet(recieverId, routerId, table)
        print("sending to port " + str(sock[1]))
        print()
        sock[0].sendto(packet, (HOST, sock[1]))



#-----------------------------------------------------------------------------------------------


def main():
    print("starting rip")

    if (len(sys.argv) < 2):
        print("no config file")
        sys.exit()

    demon = readconf()
    routerId = demon.id

    OutputSockets = outputsockets(demon)
    InputSockets = inputSockets(demon)

    table = Routing_Table()
    
    adj = initial_entries(table, demon)



    Timer = demon.timer
    timeoutTimer = 180       # timeout will be 180 instead of 60
    garbageTimer = 120
    while True:
        currentDT = datetime.datetime.now()
        print("\nHeart Beat: " + currentDT.strftime("%H:%M:%S"))
        print()
        print(table)

        #MAIN OUTPUT CODE
        if((time.time() - Timer) >= demon.timer):
            send_update_packet(OutputSockets, routerId, table)
            Timer = time.time() + random.choice(range(-5, 5))
        
        # NEIGHBOUR ROUTER TIMEOUT    
        for entry in table:
            if entry != None:
                if entry.distance == UNREACHABLE:
                    if entry.garbage(timeoutTimer, garbageTimer):       # final will be 120
                        garbage_timeout(table, entry)
                else:
                    if entry.timedOut(timeoutTimer):                    # final will be 180
                        timeout(entry, table)



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
            # print ("received packet")
            sender_id, entries = read_packet(routerId, data)
            print ("received packet from " + str(sender_id))
            # print(table)
            update_table(sender_id, table, entries, routerId, OutputSockets, adj)
            # print(table)
            # print()
    


if __name__ == "__main__":
    if (sys.version_info < (3, 0)):
        print("")
        print("*" * 19)
        print("Please use python 3")
        print("")
        print("")
        sys.exit()
    main()
