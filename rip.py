import sys
import socket
import select
import datetime

HOST = "127.0.0.1"



class Demon:
    def __init__(self, id, inputs, outputs, timer=None):
        self.id = id
        self.inputs = inputs
        self.outputs = outputs
        self.timer = timer

    def __repr__(self):
        return "router" + str(self.id)
    
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
        return Demon(router_id, input_ports, output_ports)
    
                

def get_all_demons():
    demons = []
    for i in range(1, len(sys.argv)):
        demon = readconf(i, demons)
        if demon is None: 
            print("\nCould not use file '{}'\n".format(sys.argv[i])) 
        else:
            demons.append(demon)
    return demons
  
def readconf(arg_num, demons):
    print("\n******trying to open file******\n")
    print(sys.argv[arg_num])
    file = open("./Config/" + sys.argv[arg_num], "r")

    configs = file.readlines()

    for x in configs:
        print(x)

    print("********************************\n")

    demons = get_demon(configs, demons)

    return demons
    
def allinputSockets(demons):
    sockets = []
    print("")
    print("Starting socket construction.\n")

    for demon in demons:
        print("")
        print(demon.id, demon.inputs, demon.outputs)
        print("")

        sockets += inputSockets(demon)

    print("\nsocket construction done.\n" + str(len(sockets)) + " scokets have been made.")
    return sockets      

def inputSockets(deamon):
    socket_values = deamon.inputs
    sockets = []
    for value in socket_values:
        print("Building socket " + str(value))
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((HOST, value))
        sockets.append(sock)

    return sockets

def ports_match(router1, router2):

    if (router1[router2.id] is None):       #is an Output_Port from router1 found with router_id of router2
        return False

    if (router2[router1.id] is None):       #is an Output_Port from router2 found with router_id of router1
        return False

    if not (router1[router2.id].port in router2.inputs):        # if the output port is found in router2's input ports
        return False

    if not (router2[router1.id].port in router1.inputs):        # if the output port is found in router1's input ports
        return False

    if not (router1[router2.id].metric == router2[router1.id].metric):      # metrics are the same
        return False

    return True

""" Checks that there are not going to be any duplicate port binding. doesnt work and is inefficent"""
def unique_link(router1, router2, demons):
    for demon in demons:
        counterA = 0
        counterB = 0
        for output in demon.outputs:
            print("output",output)
            print(router1[router2.id].port)
            if output.port == router1[router2.id].port:
                counterA += 1
            if output.port == router2[router1.id].port:
                counterB += 1
            print(counterA > 1 or counterB >1)
            if counterA > 1 or counterB >1:
                return False
        counterA = 0
        counterB = 0
        for port in demon.inputs:
            print("port",port)
            print(router1[router2.id].port)
            print(router2[router1.id].port)
            if port == router1[router2.id].port:
                counterA += 1
            if port == router2[router1.id].port:
                counterB += 1
            print(counterA > 1 or counterB >1)
            if counterA > 1 or counterB >1:
                return False
    return True




def are_neighboured(a, b, demons):
    if not (ports_match(a,b)):
        return False

    if not unique_link(a, b, demons):
        return False
    return True
        
    


def main():
    print("starting rip")

    if (len(sys.argv) < 2):
        print("no config file")
        sys.exit()

    demons = get_all_demons()
    
    print(demons[0])
    print(are_neighboured(demons[0], demons[1], demons))
    

    sockets = allinputSockets(demons)

    while True:
        currentDT = datetime.datetime.now()
        print("\nHeart Beat: " + currentDT.strftime("%H:%M:%S"))
        ##-------------------------------------------------------------------------------
        # this will block until at least one socket is ready (uncomment the one you want)
            #no timeout
        #ready_socks,_,_ = select.select(sockets, [], []) 
            #timeout
        ready_socks,_,_ = select.select(sockets, [], [], 1) ##timeout is in seconds
        ##------------------------------------------------------------------------------
        for sock in ready_socks:
            data, addr = sock.recvfrom(1024) # This is will not block
            print ("received message:", data)
    


if __name__ == "__main__":
    main()
