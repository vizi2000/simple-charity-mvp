import requests
import hmac
import hashlib
import base64
import logging

logger = logging.getLogger(__name__)

def generate_hash(params, secret_key):
    sorted_params = sorted(params.items())
    param_string = '|'.join([str(k) + '=' + str(v) for k, v in sorted_params])
    logger.debug(f"Param string for hash: {param_string}")
    hash_value = hmac.new(secret_key.encode(), param_string.encode(), hashlib.sha256).digest()
    return base64.b64encode(hash_value).decode()

def create_payment(params, endpoint, secret_key):
    params['hash'] = generate_hash(params, secret_key)
    logger.debug(f"Sending request to {endpoint} with params: {params}")
    response = requests.post(endpoint, data=params)
    logger.debug(f"Response status code: {response.status_code}, Response body: {response.text}")
    return response

# Example usage
# response = create_payment(payment_params, 'https://test.fiserv.com', 'your_secret_key')
