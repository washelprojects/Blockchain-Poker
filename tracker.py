import pickle
from socket import *
import threading
import time
import sys

class Tracker:
    """
    Manages peers and their connection states.

    Attributes:
        online (list): List of tuples containing active peer information and their connection states.
        stop_event (threading.Event): Event to signal termination of the peer manager thread.
    """
    def __init__(self):
        """
        Initialize a Tracker object.
        """
        #list of adresses and there current state of connection
        #(address of active peer, itterations since last 'ALIVE' confirmation)
        self.online = [] 
        self.stop_event = threading.Event()

    def peer_manager(self, node_socket):
        """
        Manage incoming peer connections and handle ALIVE confirmations.

        Args:
            node_socket (socket): Socket object for communication with peers.
        """
        node_socket.settimeout(3)

        while not self.stop_event.is_set():
            data = None
            try:
                data, addr = node_socket.recvfrom(2048)
            
                data = pickle.loads(data)
                #if you recieve a new entry
                if data[0] == 'HELLO':
                    print("new entry")
                    entry = [addr[0], addr[1], 0]
                    self.online.append((entry, data[1]))
                    b = 'TRACKER'
                    message_to_peers = (b, self.online)
                    pickled_list = pickle.dumps(message_to_peers)
                    for peer in self.online:
                        print("send to: ", peer)
                        node_socket.sendto(pickled_list, (peer[0][0], peer[0][1]))

                #if you recieve confirmation of alive
                if data == b'ALIVE':
                    for peer in self.online:
                        peer[0][2]=peer[0][2]+1
                        if  addr[1] == peer[0][1]:
                            print("updating peer : ", peer[0][1])
                            print("recieved address : " , addr[1])
                            peer[0][2] = 0
                            print("ALIVE:", peer[0][1])
                        if  peer[0][2] == 5:
                            print("KILLING:", peer[0][1])
                            #remove peer 
                            self.online.remove(peer)
                            b = 'TRACKER'
                            message_to_peers = (b, self.online)
                            pickled_list = pickle.dumps(message_to_peers) 
                            for peer in self.online:
                                node_socket.sendto(pickled_list, (peer[0][0], peer[0][1]))
            except KeyboardInterrupt:
                print(f"\nTerminating Tracker...")
                tracker.stop_event.set()
            except:
                self.online.clear()
                pass
                print(self.online)
                # time.sleep(0.1)
            

if __name__ == "__main__":
    arguments = sys.argv
    if len(arguments) != 3:
        print(f"Invalid Arguments: Call using 'python3 tracker.py <tracker address> <tracker port>")
    else:
        tracker_address = arguments[1]
        tracker_port = int(arguments[2])
        tracker = Tracker()
        server_address = (tracker_address, tracker_port)
        node_socket = socket(AF_INET, SOCK_DGRAM)
        node_socket.bind(server_address)
        tracker.peer_manager(node_socket)
        while not tracker.stop_event.is_set():
            time.sleep(1)
        print(f"Tracker Terminated!")
        node_socket.close()
