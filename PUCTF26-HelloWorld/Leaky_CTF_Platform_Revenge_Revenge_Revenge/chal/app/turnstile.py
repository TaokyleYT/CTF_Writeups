# Clouflare Turnstile validation. Not related to the challenge.
import requests
from app import config

def validateTurnstileAnswer(answer, remoteip):
    if config.TURNSTILE_CONFIG['ENABLE_TURNSTILE'] == False:
        return True
    
    if not answer:
        return False
    
    data = {
        'secret': config.TURNSTILE_CONFIG['TURNSTILE_SECRET_KEY'],
        'response': answer,
        'remoteip': remoteip,
    }
    resp = requests.post('https://challenges.cloudflare.com/turnstile/v0/siteverify', data=data)
    result = resp.json()
    if not result.get('success', False):
        return False
    
    return True