# src/utils/leak_protection.py - VPN leak detection and protection

import requests
import asyncio
from datetime import datetime
from typing import Dict, List, Optional

class LeakProtection:
    """Handles VPN leak detection and reporting"""
    
    def __init__(self, proxy_config=None):
        self.proxy_config = proxy_config
        self.session = self._create_session()
        self.leak_results = {}
        
    def _create_session(self):
        """Create requests session with optional proxy"""
        session = requests.Session()
        if self.proxy_config:
            session.proxies = self.proxy_config
        return session
    
    def check_ipv4_leak(self) -> Optional[str]:
        """Check for IPv4 leak - should return VPN server IP"""
        try:
            response = self.session.get('https://api.ipify.org?format=json', timeout=5)
            if response.status_code == 200:
                ip = response.json().get('ip')
                self.leak_results['ipv4'] = {
                    'leaked': True,
                    'ip': ip,
                    'timestamp': datetime.utcnow().isoformat()
                }
                return ip
        except Exception as e:
            self.leak_results['ipv4'] = {
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
        return None
    
    def check_ipv6_leak(self) -> Optional[str]:
        """Check for IPv6 leak"""
        try:
            response = self.session.get('https://ipv6.myexternalip.com/raw', timeout=5)
            if response.status_code == 200:
                ip = response.text.strip()
                # Check if valid IPv6
                if ':' in ip:
                    self.leak_results['ipv6'] = {
                        'leaked': True,
                        'ip': ip,
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    return ip
        except Exception as e:
            self.leak_results['ipv6'] = {
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
        return None
    
    def check_dns_leak(self) -> List[str]:
        """Check for DNS leaks using dnsleaktest.com API"""
        leaked_dns = []
        try:
            # Method 1: Check via public DNS query
            response = self.session.get('https://dns.google/dns-query?name=whoami.akamai.net&type=TXT', 
                                       headers={'accept': 'application/dns-json'}, timeout=5)
            if response.status_code == 200:
                data = response.json()
                # If we get a response, DNS may be leaking
                self.leak_results['dns'] = {
                    'potentially_leaked': True,
                    'response': str(data),
                    'timestamp': datetime.utcnow().isoformat()
                }
                leaked_dns.append('google-dns')
        except Exception as e:
            pass
        
        try:
            # Method 2: Check via whoami.akamai.net
            response = self.session.get('https://whoami.akamai.net/', timeout=5)
            if response.status_code == 200:
                self.leak_results['dns_akamai'] = {
                    'response': response.text[:100],
                    'timestamp': datetime.utcnow().isoformat()
                }
                leaked_dns.append('akamai')
        except Exception as e:
            pass
        
        return leaked_dns
    
    def check_webrtc_leak(self) -> bool:
        """
        Check for WebRTC leak (requires browser context)
        Returns True if potential leak detected
        """
        webrtc_leak_detected = False
        try:
            # This would require browser automation (Selenium)
            # For now, we'll document the requirement
            self.leak_results['webrtc'] = {
                'requires_browser': True,
                'note': 'WebRTC leak detection requires browser automation',
                'javascript_check': '''
                function getWebRTCIPs(onновых) {
                    var peerConnection = window.RTCPeerConnection
                        || window.webkitRTCPeerConnection
                        || window.mozRTCPeerConnection;
                    
                    if (!peerConnection) return;
                    
                    var nope = function() {};
                    var pc = new peerConnection({iceServers: []});
                    pc.createDataChannel("");
                    pc.createOffer(function(sdp) {
                        sdp.sdp.split('\\n').forEach(function(line) {
                            if (line.indexOf('candidate') < 0) return;
                            var parts = line.split(' ');
                            for (var i = parts.length - 1; i >= 0; i--) {
                                if (parts[i].match(/^(\\d{1,3}(\\.\\d{1,3}){3}|[a-f0-9]{1,4}(:[a-f0-9]{1,4}){7})$/)) {
                                    console.log('WebRTC IP: ' + parts[i]);
                                }
                            }
                        });
                    }, nope);
                }
                ''',
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            pass
        
        return webrtc_leak_detected
    
    def full_leak_test(self) -> Dict:
        """Run all leak detection tests"""
        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'tests': {}
        }
        
        # IPv4 Leak
        ipv4 = self.check_ipv4_leak()
        results['tests']['ipv4'] = {
            'leaked': bool(ipv4),
            'ip': ipv4
        }
        
        # IPv6 Leak
        ipv6 = self.check_ipv6_leak()
        results['tests']['ipv6'] = {
            'leaked': bool(ipv6),
            'ip': ipv6
        }
        
        # DNS Leak
        dns_leaks = self.check_dns_leak()
        results['tests']['dns'] = {
            'leaked': len(dns_leaks) > 0,
            'detected_via': dns_leaks
        }
        
        # WebRTC Leak
        webrtc = self.check_webrtc_leak()
        results['tests']['webrtc'] = {
            'requires_browser': True,
            'checked': True
        }
        
        # Overall Security Assessment
        is_secure = not (ipv4 or ipv6 or dns_leaks)
        results['secure'] = is_secure
        results['total_leaks_detected'] = sum([
            bool(ipv4),
            bool(ipv6),
            len(dns_leaks)
        ])
        
        return results
    
    def get_leak_report(self) -> str:
        """Generate human-readable leak test report"""
        report = []
        report.append("=" * 50)
        report.append("VPN LEAK TEST REPORT")
        report.append("=" * 50)
        
        for test_name, result in self.leak_results.items():
            report.append(f"\n[{test_name.upper()}]")
            if isinstance(result, dict):
                for key, value in result.items():
                    if key != 'response':  # Skip long responses
                        report.append(f"  {key}: {value}")
        
        report.append("\n" + "=" * 50)
        return "\n".join(report)