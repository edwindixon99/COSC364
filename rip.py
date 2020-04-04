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
    

def ports_match(router1, router2):
    """ checks if two routers have an input/output port connection.
        Args:
        router1 (Demon)
        router2 (Demon)
        Returns:
        bool
    """
    if (router1[router2.id] is None or router2[router1.id] is None):       #is an Output_Port from router1 found with router_id of router2
        return False                                                        #is an Output_Port from router2 found with router_id of router1
                                
    if not (router1[router2.id].port in router2.inputs):        # if the output port is found in router2's input ports
        return False

    if not (router2[router1.id].port in router1.inputs):        # if the output port is found in router1's input ports
        return False

    if not (router1[router2.id].metric == router2[router1.id].metric):      # metrics are the same
        print("metrics are not the same for routers {}, {}".format(router1.id, router2.id))
        sys.exit()
        #return False

    return True

def common_port(a, b):
    print(list(set(a.inputs) & set(b.getOutputPorts())))
    return list(set(a.inputs) & set(b.getOutputPorts()))[0]

def are_duplicate_ports(demons, port, a, b):
    """ ensures no other Host other than a or b have their input/outport ports 
        Args:
        demons (list)
        port (str): port that's being checked
        a (Demon)
        b (Demon)
    """
    totalinputs = set()
    totaloutputs = set()
    
    for demon in demons:
        outputs = demon.getOutputPorts()
        if demon != a and demon != b:
            if port in demon.inputs:
                print("Port {} is being used by 'router {}' for input and 'router {}' for output so cannot be used by 'router {}'"
                .format(port, a.id, b.id, demon.id))
                sys.exit()
            if port in outputs:
                print("Port {} is being used by 'router {}' for input and 'router {}' for output so cannot be used by 'router {}'"
                .format(port, a.id, b.id, demon.id))
                sys.exit()

        total = len(totalinputs) + len(demon.inputs)
        totalinputs = totalinputs | set(demon.inputs)
        realtotal = len(totalinputs)
        if not (total == realtotal):
            print("an input port of 'router {}' is already in use".format(demon.id))
            sys.exit()
        total = len(totaloutputs) + len(outputs)                                    #repeation of previous 5 lines 
        totaloutputs = totaloutputs | set(outputs)                                  #but with terms of output 
        realtotal = len(totaloutputs)
        if not (total == realtotal):
            print("an output port of 'router {}' is already in use".format(demon.id))
            sys.exit()



def check_ports(demons):
    """ checks that the ports given in the configs are valid together
        if the ports are invalid it will close the program
    Args:
        demons (list)
    """
    for a in demons:
        for b in demons:
            if a != b:
                if ports_match(a, b):
                    port = common_port(a, b)
                    are_duplicate_ports(demons, port, a, b)


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

def main():
    print("starting rip")

    if (len(sys.argv) < 2):
        print("no config file")
        sys.exit()

    demons = get_all_demons()
    
    check_ports(demons)
    

    print(demons[0])

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
