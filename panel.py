# panel.py
import requests
import json
import uuid
from datetime import datetime, timedelta
from config import PANEL_URL, USERNAME, PASSWORD, PANEL_PROXY

class XUIPanel:
    def __init__(self):
        self.base_url = PANEL_URL.rstrip('/')
        self.session = requests.Session()
        if PANEL_PROXY:
            if PANEL_PROXY.startswith('socks5://'):
                self.session.proxies = {'http': PANEL_PROXY, 'https': PANEL_PROXY}
            else:
                self.session.proxies = {'http': PANEL_PROXY, 'https': PANEL_PROXY}
        self.login()

    def login(self):
        login_url = f"{self.base_url}/login"
        data = {
            'username': USERNAME,
            'password': PASSWORD
        }
        response = self.session.post(login_url, data=data)
        if response.status_code != 200 or not response.json().get('success'):
            raise Exception("Login failed")

    def get_inbounds(self):
        url = f"{self.base_url}/panel/api/inbounds/list"
        response = self.session.get(url)
        return response.json()

    def add_client(self, inbound_id, email, total_gb=0, expiry_time=0):
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
        url = f"{self.base_url}/sub/{sub_id}"
        response = self.session.get(url)
        return response.text

    def get_client_traffic(self, email):
        # Assuming we can get traffic by email, but API might require client ID
        # This is a placeholder; adjust based on actual API
        inbounds = self.get_inbounds()
        for inbound in inbounds['obj']:
            if inbound['id'] == INBOUND_ID:
                clients = json.loads(inbound['settings'])['clients']
                for client in clients:
                    if client['email'] == email:
                        return client.get('totalGB', 0) - client.get('usedGB', 0)  # Placeholder
        return None

    def update_client(self, inbound_id, client_id, updates):
        url = f"{self.base_url}/panel/api/inbounds/updateClient/{client_id}"
        data = {
            'id': inbound_id,
            **updates
        }
        response = self.session.post(url, data=data)
        return response.json()