import os
import sys
from urllib import request
import re

from info import Info

ip_address_pattern = re.compile(r'[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+')
numbers_pattern = re.compile('[0-9]+')
as_pattern = re.compile(r'(?:origin|OriginAS): *([^\n]+)\n')
provider_pattern = re.compile(r'mnt-by: *([^\n]+)\n')
country_pattern = re.compile(r'(?:country|Country): *([^\n]+)\n')


def main():
    #tracert = get_tracert_output("vk.com")
    tracert = open('vk.com.txt', 'r').read()

    infos = parse_info_from_tracert(tracert)

    white_addresses = [info for info in infos if is_ip_white(info.ip_address)]

    #Для каждого белого адреса находим AS, Страну и провайдера
    for info in white_addresses:
        update_info(info)
    print('№'.ljust(5) + 'Ip'.ljust(16) + 'AS'.ljust(16) + 'Country'.ljust(10) + 'Provider')
    for info in infos:
        print(info)


def get_tracert_output(ip_address):
    command = f'tracert {ip_address}'
    stream = os.popen(command)
    data = stream.read()
    with open(file=f'{ip_address}.txt', mode='w', encoding='utf8') as file:
        file.write(data)
    return data


def update_info(info):
    page = get_nic_ru_page(info.ip_address)

    as_number = try_get_info_from_page(page, as_pattern)
    provider = try_get_info_from_page(page, provider_pattern)
    country = try_get_info_from_page(page, country_pattern)

    info.as_number = as_number
    info.provider = provider
    info.country = country


def try_get_info_from_page(page, pattern):
    try:
        return pattern.search(page).group(1)
    except:
        return None


def get_nic_ru_page(ip):
    try:
        with request.urlopen(get_nic_ru_whois_address(ip)) as response:
            return response.read().decode('utf8')
    except:
        return ''


def get_nic_ru_whois_address(ip):
    #whois сервис от nic.ru
    return f'https://www.nic.ru/whois/?searchWord={ip}'


def is_ip_white(ip):
    octets = [int(x) for x in ip.split('.')]
    if octets[0] == 10:
        return False
    if octets[0] == 192 and octets[1] == 168:
        return False
    if octets[0] == 172 and 16 <= octets[1] <= 31:
        return False
    return True


def parse_info_from_tracert(tracert):
    lines = tracert.splitlines()[3: -2]
    ip_addresses = []
    for i in range(len(lines)):
        line = lines[i]
        if line:
            address = ip_address_pattern.search(line)
            address_number = numbers_pattern.search(line)
            if address and address_number:
                ip_addresses.append(Info(address_number.group(0), address.group(0)))
    return ip_addresses


if __name__ == '__main__':
    main()