from base64 import urlsafe_b64encode
from hashlib import sha256
import re
import os


def create_token():
    """
    Create a random, shielded URL-safe 256bit token

    @return:str
    """
    # Get random seed
    seed = os.urandom(32)

    # Protect generator
    binary_token = sha256(sha256(seed).digest()).digest()

    # Return encoded version, strip last 2 chars (padding)
    return urlsafe_b64encode(binary_token)[:-2]

def valid_token(token):
    """
    Only accept valid urlsafe base64 chars for the token (not including pad). Must be a length of 42 (256bits in 4/3)

    @param token:str
    @return:bool
    """
    if len(token) != 42:
        return False

    # From rfc3548
    if not re.match(r'^[A-Za-z0-9\-_]$', token):
        return False

    return True