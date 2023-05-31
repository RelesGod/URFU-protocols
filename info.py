class Info:
    def __init__(self, ip_number, ip_address, as_number=None, country=None, provider=None):
        self.ip_number = ip_number
        self.ip_address = ip_address
        self.as_number = as_number
        self.country = country
        self.provider = provider

    def __str__(self):
        return (f'{self.ip_number}'.ljust(5) +
                f'{self.ip_address}'.ljust(16) +
                f'{self.as_number}'.ljust(16) +
                f'{self.country}'.ljust(10) +
                f'{self.provider}'
                )