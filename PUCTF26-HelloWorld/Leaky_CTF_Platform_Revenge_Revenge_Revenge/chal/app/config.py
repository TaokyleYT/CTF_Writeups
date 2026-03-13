import secrets
from os import getenv

REDIS_URL = getenv('REDIS_URL', 'redis://redis:6379/0')
REAL_FLAG = getenv('FLAG', 'PUCTF26{fake_flag}')
ADMIN_SECRET = secrets.token_hex(16)

CORRECT_FLAG_PREFIX = 'leakyctf'
SIMUATION_FLAG_PREFIX = 'flag'
RANDOM_HEX_LENGTH = 4
CORRECT_FLAG = f'{CORRECT_FLAG_PREFIX}{{{secrets.token_hex(RANDOM_HEX_LENGTH)}}}'
MAX_FLAGS_LENGTH = 1_000_000
MAX_SPAM_FLAGS_LENGTH = 100_000

BOT_CONFIG = {
    'APP_DOMAIN': 'localhost',
    'VISIT_DEFAULT_TIMEOUT_SECOND': 65,
    'VISIT_SLEEP_SECOND': 60
}

TURNSTILE_CONFIG = {
    'ENABLE_TURNSTILE': getenv('ENABLE_TURNSTILE', 'false').lower() == 'true',
    'TURNSTILE_SITE_KEY': getenv('TURNSTILE_SITE_KEY', ''),
    'TURNSTILE_SECRET_KEY': getenv('TURNSTILE_SECRET_KEY', '')
}