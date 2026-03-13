import asyncio
import traceback
from playwright.async_api import async_playwright
from .config import ADMIN_SECRET, BOT_CONFIG

BROWSER_ARGS = [
    '--disable-dev-shm-usage',
    '--disable-gpu',
    '--no-gpu',
    '--disable-default-apps',
    '--disable-translate',
    '--disable-device-discovery-notifications',
    '--disable-software-rasterizer',
    '--disable-xss-auditor',
    '--disable-crash-reporter',
    '--disable-features=LocalNetworkAccessChecks' # purely prevent unintended solution
]

async def visitUrl(urlToVisit):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=BROWSER_ARGS
        )
        context = await browser.new_context()

        try:
            page = await context.new_page()
            page.set_default_timeout(BOT_CONFIG['VISIT_DEFAULT_TIMEOUT_SECOND'] * 1000)

            print(f'[*] Bot setting admin cookie...')
            await context.add_cookies([{
                'name': 'admin_secret',
                'value': ADMIN_SECRET,
                'domain': BOT_CONFIG['APP_DOMAIN'],
                'path': '/',
                'httpOnly': True,
                'sameSite': 'Lax',
            }])

            print(f'[*] Bot visiting {urlToVisit} for {BOT_CONFIG["VISIT_SLEEP_SECOND"]} seconds...')
            await page.goto(urlToVisit, wait_until='load', timeout=10_000)
            await asyncio.sleep(BOT_CONFIG['VISIT_SLEEP_SECOND'])

            print('[*] Bot finished visiting')
            return True
        except Exception as e:
            print(f'[-] Bot error: {e}')
            traceback.print_exc()
            return False
        finally:
            await context.close()
            await browser.close()
            print('[*] Bot browser closed')