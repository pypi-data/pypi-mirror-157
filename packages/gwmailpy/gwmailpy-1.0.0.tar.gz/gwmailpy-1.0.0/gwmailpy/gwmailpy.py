import httpx, random, string

class GwApi:
    # The main class for our wrapper.
    def __init__(self, proxy: str= None, timeout: int=15) -> None:
        self.session = httpx.Client(headers={'content-type': 'application/json'}, timeout=timeout, proxies=proxy)
        self.base_url = 'https://api.mail.gw'
    # Load domains
    def load_domains(self) -> list:
        domains: list = []
        
        for item in self.session.get(f'{self.base_url}/domains').json()['hydra:member']:
            domains.append(item['domain'])

        return domains
    # Load mails
    def load_mail(self, name: str = ''.join(random.choice(string.ascii_lowercase) for _ in range(15)), password: str= None, domain: str = None) -> str:
        mail: str =  f'{name}@{domain if domain != None else self.load_domains()[0]}'
        response: int = self.session.post(f'{self.base_url}/accounts', json={'address': mail, 'password': mail}).status_code
        
        try:
            if response == 201:
                token = self.session.post(f'{self.base_url}/token', json={'address': mail, 'password': mail if password == None else password}).json()['token']
                self.session.headers['authorization'] = f'Bearer {token}'
                return mail
        except:
            return 'Error: Email Creation failed.'
    # Load inbox
    def load_inbox(self):
        response = self.session.get(f'{self.base_url}/messages').json()['hydra:member']
        return response
    # Fetch message
    def get_message(self, message_id: str):
        response = self.session.get(f'{self.base_url}/messages/{message_id}').json()
        return response
    # Fetch message value
    def get_message_value(self, message_id: str):
        response = self.get_message(message_id)['text']
        return response