# payment.py
import requests
import json
from config import PANEL_PROXY

class PaymentGateway:
    def __init__(self, gateway_name, **kwargs):
        self.gateway_name = gateway_name
        self.proxy = PANEL_PROXY
        self.kwargs = kwargs

    def create_payment(self, amount, description, callback_url):
        """Create a payment and return payment URL"""
        raise NotImplementedError

    def verify_payment(self, authority):
        """Verify payment and return transaction details"""
        raise NotImplementedError

class ZarinpalGateway(PaymentGateway):
    def __init__(self, merchant_id):
        super().__init__('zarinpal', merchant_id=merchant_id)
        self.api_url = "https://api.zarinpal.com/pg/v4/payment"
        self.verify_url = "https://api.zarinpal.com/pg/v4/payment/verify.json"

    def create_payment(self, amount, description, callback_url):
        payload = {
            "merchant_id": self.kwargs['merchant_id'],
            "amount": int(amount * 10),  # Zarinpal uses toman
            "description": description,
            "callback_url": callback_url
        }
        proxies = {'http': self.proxy, 'https': self.proxy} if self.proxy else None
        response = requests.post(self.api_url, json=payload, proxies=proxies)
        data = response.json()
        if data['data']['code'] == 100:
            authority = data['data']['authority']
            payment_url = f"https://www.zarinpal.com/pg/StartPay/{authority}"
            return {'success': True, 'payment_url': payment_url, 'authority': authority}
        return {'success': False, 'error': 'Failed to create payment'}

    def verify_payment(self, authority, amount):
        payload = {
            "merchant_id": self.kwargs['merchant_id'],
            "amount": int(amount * 10),
            "authority": authority
        }
        proxies = {'http': self.proxy, 'https': self.proxy} if self.proxy else None
        response = requests.post(self.verify_url, json=payload, proxies=proxies)
        data = response.json()
        if data['data']['code'] == 100:
            return {'success': True, 'ref_id': data['data']['ref_id']}
        return {'success': False, 'error': 'Payment verification failed'}

class PayirGateway(PaymentGateway):
    def __init__(self, api_key):
        super().__init__('payir', api_key=api_key)
        self.api_url = "https://pay.ir/pg/send"
        self.verify_url = "https://pay.ir/pg/verify"

    def create_payment(self, amount, description, callback_url):
        payload = {
            "api": self.kwargs['api_key'],
            "amount": int(amount * 10),
            "redirect": callback_url,
            "description": description
        }
        proxies = {'http': self.proxy, 'https': self.proxy} if self.proxy else None
        response = requests.post(self.api_url, data=payload, proxies=proxies)
        data = response.json()
        if data.get('status') == 1:
            payment_url = f"https://pay.ir/pg/{data['token']}"
            return {'success': True, 'payment_url': payment_url, 'token': data['token']}
        return {'success': False, 'error': 'Failed to create payment'}

    def verify_payment(self, token, amount):
        payload = {
            "api": self.kwargs['api_key'],
            "token": token,
            "amount": int(amount * 10)
        }
        proxies = {'http': self.proxy, 'https': self.proxy} if self.proxy else None
        response = requests.post(self.verify_url, data=payload, proxies=proxies)
        data = response.json()
        if data.get('status') == 1:
            return {'success': True, 'trans_id': data.get('transId')}
        return {'success': False, 'error': 'Payment verification failed'}

class IDPayGateway(PaymentGateway):
    def __init__(self, api_key):
        super().__init__('idpay', api_key=api_key)
        self.api_url = "https://api.idpay.ir/v1.1/payment"
        self.verify_url = "https://api.idpay.ir/v1.1/payment/verify"

    def create_payment(self, amount, description, callback_url, user_id):
        payload = {
            "order_id": str(user_id),
            "amount": int(amount * 10),
            "name": "VPN Config",
            "phone": "09000000000",
            "mail": "user@example.com",
            "desc": description,
            "callback": callback_url
        }
        headers = {
            "Content-Type": "application/json",
            "X-API-KEY": self.kwargs['api_key']
        }
        proxies = {'http': self.proxy, 'https': self.proxy} if self.proxy else None
        response = requests.post(self.api_url, json=payload, headers=headers, proxies=proxies)
        data = response.json()
        if data.get('status') == 100:
            payment_url = f"https://idpay.ir/web/gateway/{data['id']}"
            return {'success': True, 'payment_url': payment_url, 'id': data['id']}
        return {'success': False, 'error': 'Failed to create payment'}

    def verify_payment(self, transaction_id, amount):
        payload = {
            "id": transaction_id,
            "order_id": None,
            "amount": int(amount * 10)
        }
        headers = {
            "Content-Type": "application/json",
            "X-API-KEY": self.kwargs['api_key']
        }
        proxies = {'http': self.proxy, 'https': self.proxy} if self.proxy else None
        response = requests.post(self.verify_url, json=payload, headers=headers, proxies=proxies)
        data = response.json()
        if data.get('status') == 100:
            return {'success': True, 'track_id': data.get('track_id')}
        return {'success': False, 'error': 'Payment verification failed'}

def get_payment_gateway(gateway_name, **kwargs):
    if gateway_name == 'zarinpal':
        return ZarinpalGateway(kwargs.get('merchant_id'))
    elif gateway_name == 'payir':
        return PayirGateway(kwargs.get('api_key'))
    elif gateway_name == 'idpay':
        return IDPayGateway(kwargs.get('api_key'))
    else:
        raise ValueError(f"Unknown payment gateway: {gateway_name}")