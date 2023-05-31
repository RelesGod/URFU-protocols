import pickle
import socket
import threading
import time

import dnslib as dnslib

DNS_PORT = 53
HOST = "127.0.0.1"
REMOTE_DNS_SERVER = "8.8.8.8"
IS_FINISHED = False
domain_answer_set = {}
LOCK = threading.Lock()


class DnsObject:
    def __init__(self, ttl, concat_data):
        self._init_time = time.time()
        self.ttl = ttl
        self.concat_data = concat_data

    def is_expired(self):
        return self.remain_ttl() == 0

    def remain_ttl(self):
        passed_time = int(time.time() - self._init_time)
        return max(0, self.ttl - passed_time)


def check_domain(respond):
    return respond.q.qname.label in domain_answer_set


def check_answer(respond):
    return respond.q.qtype in domain_answer_set[respond.q.qname.label]


def add_cash(respond):
    concat_data = respond.ar + respond.auth + respond.rr
    rtype = concat_data[0].rtype
    ttl = concat_data[0].ttl
    dns_object = DnsObject(ttl, concat_data)
    if not check_domain(respond):
        domain_answer_set[respond.q.qname.label] = {rtype: dns_object}
    else:
        domain_answer_set[respond.q.qname.label][rtype] = dns_object


def get_data(respond):
    return domain_answer_set[respond.q.qname.label][respond.q.qtype]


def add_answer(respond):
    data = get_data(respond)
    for addr in data.concat_data:
        respond.add_answer(dnslib.RR(
            rname=respond.q.qname, rclass=respond.q.qclass, rtype=respond.q.qtype,
            ttl=data.remain_ttl(),
            rdata=addr.rdata
        ))


def delete_expired_ttl():
    while not IS_FINISHED:
        time.sleep(3)
        with LOCK:
            for answer_set in domain_answer_set.values():
                dead = []
                for data in answer_set:
                    if answer_set[data].is_expired():
                        dead.append(data)

                for i in range(len(dead)):
                    answer_set.pop(dead[i])


def leave_on_exit():
    global IS_FINISHED
    while not IS_FINISHED:
        inp = input()
        if inp == 'exit':
            IS_FINISHED = True
            print('Конец')
        else:
            print('exit чтобы выйти')


def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_sock:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as remote_server_socket:
            server_sock.bind((HOST, DNS_PORT))
            remote_server_socket.connect((REMOTE_DNS_SERVER, DNS_PORT))
            server_sock.settimeout(1.0)
            remote_server_socket.settimeout(1.0)
            while not IS_FINISHED:
                try:
                    query_data, customer_addr = server_sock.recvfrom(10000)
                    parser_query = dnslib.DNSRecord.parse(query_data)
                    with LOCK:
                        if check_domain(parser_query):
                            if check_answer(parser_query):
                                print("уже есть к КЭШе")
                                add_answer(parser_query)
                                server_sock.sendto(parser_query.pack(), customer_addr)
                                continue

                        remote_server_socket.send(query_data)
                        respond_data, _ = remote_server_socket.recvfrom(10000)
                        parser_respond = dnslib.DNSRecord.parse(respond_data)
                        add_cash(parser_respond)
                        server_sock.sendto(respond_data, customer_addr)
                        print("отправил запрос")
                except socket.timeout:
                    pass
                except Exception as e:
                    print(e)


if __name__ == '__main__':
    try:
        with open('../backup.file', 'rb') as file:
            prev = pickle.loads(file.read())
            domain_answer_set = prev
    except Exception:
        pass
    threading.Thread(target=delete_expired_ttl).start()
    threading.Thread(target=leave_on_exit).start()
    try:
        start_server()
    except OSError as e:
        print(f'{HOST}/{DNS_PORT} Уже занят')
    except socket.error as e:
        print(f'Не удалось подключиться к {REMOTE_DNS_SERVER}/{DNS_PORT}')

    try:
        with open('../backup.file', 'wb') as file:
            file.write(pickle.dumps(domain_answer_set))
    except Exception as e:
        print(e)