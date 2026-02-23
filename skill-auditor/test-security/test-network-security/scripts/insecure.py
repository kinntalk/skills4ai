"""
Test script with network security issues
"""
import requests
import urllib.request

def no_url_validation(url):
    """MEDIUM: No URL validation"""
    response = requests.get(url)
    return response.json()

def no_timeout(url):
    """MEDIUM: No timeout"""
    return requests.get(url)

def unverified_ssl(url):
    """MEDIUM: Unverified SSL"""
    return requests.get(url, verify=False)

def data_exfiltration_risk(data, url):
    """MEDIUM: Data exfiltration risk"""
    requests.post(url, json=data)

def untrusted_domain(url):
    """MEDIUM: Untrusted domain"""
    response = urllib.request.urlopen(url)
    return response.read()

def missing_headers(url):
    """MEDIUM: Missing security headers"""
    return requests.get(url)

def no_rate_limiting(urls):
    """MEDIUM: No rate limiting"""
    for url in urls:
        requests.get(url)
