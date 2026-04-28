# panel.py
import requests
import json
import uuid
from datetime import datetime, timedelta
from ..core.config import PANEL_URL, USERNAME, PASSWORD, PANEL_PROXY, INBOUND_ID

class XUIPanel:
    def __init__(self):
        self.base_url = PANEL_URL.rstrip('/')
        self.session = requests.Session()
        self.logged_in = False
        if PANEL_PROXY:
            self.session.proxies = {'http': PANEL_PROXY, 'https': PANEL_PROXY}

    def login(self):
        if self.logged_in:
            return
        login_url = f"{self.base_url}/login"
        data = {
            'username': USERNAME,
            'password': PASSWORD
        }
        response = self.session.post(login_url, data=data)
        if response.status_code != 200 or not response.json().get('success'):
            raise Exception("Login failed")
        self.logged_in = True

    def ensure_login(self):
        if not self.logged_in:
            self.login()

    def get_inbounds(self):
        self.ensure_login()
        url = f"{self.base_url}/panel/api/inbounds/list"
        response = self.session.get(url)
        return response.json()

    def add_client(self, inbound_id, email, total_gb=0, expiry_time=0):
        self.ensure_login()
        url = f"{self.base_url}/panel/api/inbounds/addClient"
        client_id = str(uuid.uuid4())
        data = {
            'id': inbound_id,
            'settings': json.dumps({
                'clients': [{
                    'id': client_id,
                    'email': email,
                    'totalGB': total_gb,
                    'expiryTime': expiry_time
                }]
            })
        }
        response = self.session.post(url, data=data)
        result = response.json()
        if result.get('success'):
            return client_id
        else:
            raise Exception("Failed to add client")

    def get_client_config(self, sub_id):
        self.ensure_login()
        url = f"{self.base_url}/sub/{sub_id}"
        response = self.session.get(url)
        return response.text

    def get_client_traffic(self, email):
        self.ensure_login()
        inbounds = self.get_inbounds()
        for inbound in inbounds.get('obj', []):
            if inbound.get('id') == INBOUND_ID:
                clients = json.loads(inbound.get('settings', '{}')).get('clients', [])
                for client in clients:
                    if client.get('email') == email:
                        return client.get('totalGB', 0) - client.get('usedGB', 0)
        return None

    def update_client(self, inbound_id, client_id, updates):
        self.ensure_login()
        url = f"{self.base_url}/panel/api/inbounds/updateClient/{client_id}"
        data = {
            'id': inbound_id,
            **updates
        }
        response = self.session.post(url, data=data)
        return response.json()

    def disable_client(self, email):
        """Disable client by setting expiry time to now"""
        self.ensure_login()
        inbounds = self.get_inbounds()
        for inbound in inbounds.get('obj', []):
            if inbound.get('id') == INBOUND_ID:
                clients = json.loads(inbound.get('settings', '{}')).get('clients', [])
                for client in clients:
                    if client.get('email') == email:
                        client_id = client.get('id')
                        # Set expiry time to now to disable the client
                        expiry_time = int(datetime.now().timestamp() * 1000)  # milliseconds
                        updates = {
                            'settings': json.dumps({
                                'clients': [{
                                    'id': client_id,
                                    'email': email,
                                    'totalGB': client.get('totalGB', 0),
                                    'expiryTime': expiry_time,  # Expire immediately
                                    'enable': False  # Disable the client
                                }]
                            })
                        }
                        result = self.update_client(INBOUND_ID, client_id, updates)
                        return result.get('success', False)
        return False

    def get_clients(self):
        """Get all clients from the inbound"""
        self.ensure_login()
        inbounds = self.get_inbounds()
        clients = []
        for inbound in inbounds.get('obj', []):
            if inbound.get('id') == INBOUND_ID:
                inbound_clients = json.loads(inbound.get('settings', '{}')).get('clients', [])
                for client in inbound_clients:
                    client['inbound_id'] = inbound['id']
                    clients.append(client)
        return clients