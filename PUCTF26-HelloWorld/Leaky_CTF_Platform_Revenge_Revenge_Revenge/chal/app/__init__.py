import asyncio
import secrets
from flask import Flask, request, render_template, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from urllib.parse import urlparse
from . import config, turnstile, bot

app = Flask(__name__)
limiter = Limiter(
    get_remote_address,
    app=app,
    storage_uri=config.REDIS_URL,
)
flags = [config.CORRECT_FLAG]

@app.after_request
def add_headers(response):
    response.headers['Cache-Control'] = 'no-store'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'deny'
    return response

@app.route('/')
def index():
    return render_template('index.html', name='Leaky CTF Platform')

@app.route('/search')
def search():
    if request.cookies.get('admin_secret', '') != config.ADMIN_SECRET:
        return 'Access denied. Only admin can access this endpoint.', 403

    flag = request.args.get('flag', '')
    if not flag:
        return 'Invalid flag', 400

    foundFlag = any(f for f in flags if f.startswith(flag))
    if not foundFlag:
        return 'Your flag was not found in our key-value store.', 200

    return 'Your flag was found in our key-value store!', 200

@app.route('/spam_flags')
@limiter.limit('1 per second')
def spamFlags():
    size = request.args.get('size', type=int, default=10)
    if size < 1 or size > config.MAX_SPAM_FLAGS_LENGTH:
        return f'Size must be between 1 and {config.MAX_SPAM_FLAGS_LENGTH}', 400
    if len(flags) + size > config.MAX_FLAGS_LENGTH:
        return f'Cannot add more flags. It would exceed the maximum of {config.MAX_FLAGS_LENGTH}. I don\'t want people to DoS my server :D', 400
    
    for _ in range(size):
        flags.append(f'{config.SIMUATION_FLAG_PREFIX}{{{secrets.token_hex(config.RANDOM_HEX_LENGTH)}}}')

    return f'Done adding flags. Total flags: {len(flags)}', 200

@app.route('/submit_flag')
@limiter.limit('2 per minute')
def submitFlag():
    flag = request.args.get('flag', '')
    if not flag:
        return 'Please give me a flag', 400
    if not flag.startswith(config.CORRECT_FLAG_PREFIX):
        return 'Incorrect flag format', 400
    if len(flag) != len(config.CORRECT_FLAG):
        return 'Incorrect flag length', 400
    if flag != config.CORRECT_FLAG:
        return 'Incorrect flag', 400
    
    return f'Correct! The real flag is: {config.REAL_FLAG}', 200

@app.route('/report', methods=['GET'])
def viewReportPage():
    return render_template(
        'report.html', 
        name='Leaky CTF Platform', 
        isTurnstileEnabled=config.TURNSTILE_CONFIG['ENABLE_TURNSTILE'], 
        turnstileSiteKey=config.TURNSTILE_CONFIG['TURNSTILE_SITE_KEY']
    )

@app.route('/report', methods=['POST'])
@limiter.limit('2 per minute')
def report():
    isTurnstileValid = turnstile.validateTurnstileAnswer(request.form.get('answer', ''), request.remote_addr)
    if not isTurnstileValid:
        return jsonify({'error': 'Invalid CloudFlare Turnstile Captcha. Please try again.'}), 400

    url = request.form.get('url', '')
    if not url:
        return jsonify({'error': 'Please provide a URL to visit.'}), 400
    
    parsedUrl = urlparse(url)
    if not parsedUrl.scheme:
        return jsonify({'error': 'Invalid URL. Please include the URL scheme (http:// or https://).'}), 400
    if parsedUrl.scheme not in ['http', 'https']:
        return jsonify({'error': 'Invalid URL scheme. Only http and https are allowed.'}), 400
    if not parsedUrl.netloc:
        return jsonify({'error': 'Invalid URL. Please provide a valid URL with a hostname.'}), 400
    
    isBotVisitedSuccessfully = asyncio.run(bot.visitUrl(parsedUrl.geturl()))
    if not isBotVisitedSuccessfully:
        return jsonify({'error': 'The admin bot failed to visit your URL. Likely due to a timeout error.'}), 500
    
    return jsonify({'success': 'The admin bot has visited your URL.'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)