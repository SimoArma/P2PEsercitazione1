import select
import socket
from Worker import *
from ManageDB import *

# Insieme di costanti utilizzate nel progetto
#TCP_IP4 = '127.0.0.1'  # Con questo ip il bind viene effettuato su tutte le interfacce di rete
#TCP_IP6 = '::1'  # Con questo ip il bind viene effettuato su tutte le interfacce di rete

TCP_IP4 = 'localhost'
TCP_IP6 = '::1'

TCP_PORT = 5432

class MultiServer:

    database = None
    lock = None
    thread_list = {}
    server_socket4 = None
    server_socket6 = None

    def __init__(self):
        self._stop = threading.Event()
        self.database = ManageDB()
        self.lock = threading.Lock()
        self.thread_list = {}

    def start(self):

        # Creo il socket ipv4, imposto l'eventuale riutilizzo, lo assegno all'ip e alla
        try:
            self.server_socket4 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket4.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket4.bind((TCP_IP4, TCP_PORT))

        # Gestisco l'eventuale exception
        except socket.error as msg:
            print('Errore durante la creazione del socket IPv4: ' + msg[1] + '\n')

        # Creo il socket ipv6, imposto l'eventuale riutilizzo, lo assegno all'ip e alla porta
        try:
            self.server_socket6 = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            self.server_socket6.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket6.bind((TCP_IP6, TCP_PORT))

        # Gestisco l'eventuale exception
        except socket.error as msg:
            print('Errore durante la creazione del socket IPv6: ' + msg[1] + '\n')

        # Metto il server in ascolto per eventuali richieste sui socket appena creati
        self.server_socket4.listen(5)
        self.server_socket6.listen(5)

        # Continuo ad eseguire questo codice
        while True:

            # Per non rendere accept() bloccante uso l'oggetto select con il metodo select() sui socket messi in ascolto
            input_ready, read_ready, error_ready = select.select([self.server_socket4, self.server_socket6], [], [])

            # Ora controllo quale dei due socket ha ricevuto una richiesta
            for s in input_ready:

                # Il client si è collegato tramite socket IPv4, accetto quindi la sua richiesta avviando il worker
                if s == self.server_socket4:
                    client_socket4, address4 = self.server_socket4.accept()
                    client_thread = Worker(client_socket4, self.database, self.lock)
                    client_thread.run()

                # Il client si è collegato tramite socket IPv6, accetto quindi la sua richiesta avviando il worker
                elif s == self.server_socket6:
                    client_socket6, address6 = self.server_socket6.accept()
                    client_thread = Worker(client_socket6, self.database, self.lock)
                    client_thread.run()

tcpServer = MultiServer()
tcpServer.start()
