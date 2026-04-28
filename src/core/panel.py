# panel.py - Multi-panel management
import requests
import json
import uuid
from datetime import datetime, timedelta
from ..core.config import PANELS

class XUIPanel:
    def __init__(self, panel_config):
        self.id = panel_config['id']
        self.base_url = panel_config['url'].rstrip('/')
        self.username = panel_config['username']
        self.password = panel_config['password']
        self.inbound_id = panel_config.get('inbound_id', 1)
        self.session = requests.Session()
        self.logged_in = False
        proxy = panel_config.get('proxy')
        if proxy:
            self.session.proxies = {'http': proxy, 'https': proxy}

    def login(self):
        if self.logged_in:
            return
        login_url = f"{self.base_url}/login"
        data = {
            'username': self.username,
            'password': self.password
        }
        response = self.session.post(login_url, data=data)
        if response.status_code != 200 or not response.json().get('success'):
            raise Exception(f"Login failed for panel {self.id}")
        self.logged_in = True

    def ensure_login(self):
        if not self.logged_in:
            self.login()

    def get_inbounds(self):
        self.ensure_login()
        url = f"{self.base_url}/panel/api/inbounds/list"
        response = self.session.get(url)
        return response.json()

    def add_client(self, email, total_gb=0, expiry_time=0):
        self.ensure_login()
        url = f"{self.base_url}/panel/api/inbounds/addClient"
        client_id = str(uuid.uuid4())
        data = {
            'id': self.inbound_id,
            'settings': json.dumps({
                'clients': [{
                    'id': client_id,
                    'email': email,
                    'totalGB': total_gb,
                    'expiryTime': expiry_time,
                    'enable': True,
                    'tgId': '',
                    'subId': ''
                }]
            })
        }
        response = self.session.post(url, data=data)
        result = response.json()
        if result.get('success'):
            return client_id
        else:
            raise Exception(f"Failed to add client to panel {self.id}")

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


class PanelManager:
    def __init__(self):
        self.panels = {}
        for panel_config in PANELS:
            if panel_config.get('enabled', True):
                self.panels[panel_config['id']] = XUIPanel(panel_config)

    def get_panel(self, panel_id=None):
        """Get a panel by ID, or return the first available panel"""
        if panel_id and panel_id in self.panels:
            return self.panels[panel_id]
        return next(iter(self.panels.values())) if self.panels else None

    def get_available_panel(self):
        """Get an available panel using round-robin or load balancing"""
        # For now, just return the first panel
        # TODO: Implement load balancing logic
        return next(iter(self.panels.values())) if self.panels else None

    def get_all_panels(self):
        """Get all enabled panels"""
        return list(self.panels.values())


# Global panel manager instance
panel_manager = PanelManager()