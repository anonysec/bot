# payment.py
import requests
import json
from ..core.config import PANEL_PROXY
import logging
import time

logger = logging.getLogger(__name__)

class PaymentGateway:
    def __init__(self, gateway_name, enabled=True, **kwargs):
        self.gateway_name = gateway_name
        self.enabled = enabled
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

class TetraGateway(PaymentGateway):
    """Tetra Payment Gateway Integration - https://tetra98.com/docs"""
    def __init__(self, api_key):
        super().__init__('tetra', api_key=api_key)
        self.create_order_url = "https://tetra98.com/api/create_order"
        self.verify_url = "https://tetra98.com/api/verify"

    def create_payment(self, amount, description, callback_url, user_id=None, email="user@example.com", mobile="09000000000"):
        """
        Create payment order
        Args:
            amount: Amount in Rials (multiplied by 10,000 for Tetra)
            description: Order description
            callback_url: Callback URL for payment verification
            user_id: User ID for hash_id generation
            email: User email
            mobile: User mobile number
        """
        # Generate hash_id from user_id or timestamp
        hash_id = f"order-{user_id or int(time.time())}"
        
        # Tetra expects amount in Rials
        tetra_amount = int(amount * 10000)
        
        payload = {
            "ApiKey": self.kwargs['api_key'],
            "Hash_id": hash_id,
            "Amount": tetra_amount,
            "Description": description,
            "Email": email,
            "Mobile": mobile,
            "CallbackURL": callback_url
        }
        
        proxies = {'http': self.proxy, 'https': self.proxy} if self.proxy else None
        try:
            response = requests.post(
                self.create_order_url,
                json=payload,
                proxies=proxies,
                timeout=10,
                headers={"Content-Type": "application/json"}
            )
            data = response.json()
            
            if data.get('status') == '100' or data.get('status') == 100:
                return {
                    'success': True,
                    'payment_url': data.get('payment_url_web'),
                    'payment_url_bot': data.get('payment_url_bot'),
                    'authority': data.get('Authority'),
                    'tracking_id': data.get('tracking_id'),
                    'hash_id': hash_id
                }
            return {'success': False, 'error': data.get('error', 'Payment creation failed')}
        except Exception as e:
            logger.error(f"Tetra payment creation error: {e}")
            return {'success': False, 'error': str(e)}

    def verify_payment(self, authority):
        """
        Verify payment status
        Args:
            authority: Authority from payment response
        """
        payload = {
            "authority": authority,
            "ApiKey": self.kwargs['api_key']
        }
        
        proxies = {'http': self.proxy, 'https': self.proxy} if self.proxy else None
        try:
            response = requests.post(
                self.verify_url,
                json=payload,
                proxies=proxies,
                timeout=10,
                headers={"Content-Type": "application/json"}
            )
            data = response.json()
            
            if data.get('status') == '100' or data.get('status') == 100:
                return {
                    'success': True,
                    'authority': data.get('authority'),
                    'hash_id': data.get('hash_id')
                }
            return {'success': False, 'error': 'Verification failed'}
        except Exception as e:
            logger.error(f"Tetra verification error: {e}")
            return {'success': False, 'error': str(e)}

    def verify_callback(self, callback_data):
        """
        Verify callback from Tetra
        Expected callback: {status: 100, hash_id: "{hashid}", authority: "{authority}"}
        """
        try:
            status = callback_data.get('status')
            if status == 100 or status == '100':
                return {
                    'success': True,
                    'authority': callback_data.get('authority'),
                    'hash_id': callback_data.get('hash_id')
                }
            return {'success': False, 'error': 'Callback verification failed'}
        except Exception as e:
            logger.error(f"Tetra callback error: {e}")
            return {'success': False, 'error': str(e)}

def get_payment_gateway(gateway_name, **kwargs):
    """Get payment gateway instance by name"""
    if gateway_name == 'zarinpal':
        return ZarinpalGateway(kwargs.get('merchant_id'))
    elif gateway_name == 'payir':
        return PayirGateway(kwargs.get('api_key'))
    elif gateway_name == 'idpay':
        return IDPayGateway(kwargs.get('api_key'))
    elif gateway_name == 'tetra':
        return TetraGateway(kwargs.get('api_key'))
    else:
        raise ValueError(f"Unknown payment gateway: {gateway_name}")

def get_enabled_gateways(config):
    """Get list of enabled payment gateways from config"""
    gateways = {}
    
    if config.get('ZARINPAL_ENABLED', False) and config.get('ZARINPAL_MERCHANT_ID'):
        gateways['zarinpal'] = {
            'name': 'Zarinpal',
            'gateway': ZarinpalGateway(config['ZARINPAL_MERCHANT_ID'])
        }
    
    if config.get('PAYIR_ENABLED', False) and config.get('PAYIR_API_KEY'):
        gateways['payir'] = {
            'name': 'Pay.ir',
            'gateway': PayirGateway(config['PAYIR_API_KEY'])
        }
    
    if config.get('IDPAY_ENABLED', False) and config.get('IDPAY_API_KEY'):
        gateways['idpay'] = {
            'name': 'IDPay',
            'gateway': IDPayGateway(config['IDPAY_API_KEY'])
        }
    
    if config.get('TETRA_ENABLED', False) and config.get('TETRA_API_KEY'):
        gateways['tetra'] = {
            'name': 'Tetra',
            'gateway': TetraGateway(config['TETRA_API_KEY'])
        }
    
    return gateways

def has_payment_gateway():
    """Check if any payment gateway is enabled"""
    from ..core.config import ZARINPAL_ENABLED, PAYIR_ENABLED, IDPAY_ENABLED, TETRA_ENABLED
    return any([ZARINPAL_ENABLED, PAYIR_ENABLED, IDPAY_ENABLED, TETRA_ENABLED])

def get_payment_buttons():
    """Get payment gateway buttons for inline keyboard"""
    from ..core.config import (
        ZARINPAL_ENABLED, ZARINPAL_MERCHANT_ID,
        PAYIR_ENABLED, PAYIR_API_KEY,
        IDPAY_ENABLED, IDPAY_API_KEY,
        TETRA_ENABLED, TETRA_API_KEY
    )
    
    buttons = []
    
    if ZARINPAL_ENABLED and ZARINPAL_MERCHANT_ID:
        buttons.append(('Zarinpal', 'gateway_zarinpal'))
    
    if PAYIR_ENABLED and PAYIR_API_KEY:
        buttons.append(('Pay.ir', 'gateway_payir'))
    
    if IDPAY_ENABLED and IDPAY_API_KEY:
        buttons.append(('IDPay', 'gateway_idpay'))
    
    if TETRA_ENABLED and TETRA_API_KEY:
        buttons.append(('Tetra', 'gateway_tetra'))
    
    return buttons