import asyncio
import json
import os
from browser_use_sdk.v3 import AsyncBrowserUse
from playwright.async_api import async_playwright
from datetime import datetime

# NUOVA API KEY
API_KEY = os.environ.get("BROWSER_USE_API_KEY", "bu_jGikZymCNda8f1KLkBiFThn_axFR-DIjwzn6ohcoByY")

# Credenziali EasyHits4U
EMAIL = "sandrominori50+ulugarecexisa@gmail.com"
PASSWORD = "DDnmVV45!!"

async def wait_for_turnstile_token(page, timeout=60):
    """Aspetta che Turnstile generi il token"""
    print("⏳ Waiting for Turnstile token...")
    
    for i in range(timeout):
        token = await page.evaluate('''
            () => {
                const input = document.querySelector('input[name="cf-turnstile-response"]');
                return input ? input.value : null;
            }
        ''')
        
        if token and len(token) > 10:
            print(f"✅ Turnstile token obtained after {i+1} seconds")
            return token
        
        if i > 0 and i % 10 == 0:
            print(f"   Still waiting... {i}s")
        
        await asyncio.sleep(1)
    
    print("⚠️ Turnstile timeout")
    return None

async def get_all_cookies():
    print("=" * 60)
    print("EasyHits4U Cookie Manager")
    print(f"Time: {datetime.now().isoformat()}")
    print("=" * 60)
    
    client = AsyncBrowserUse(api_key=API_KEY)
    cookies_data = {}
    
    try:
        print("\n🔌 Creating cloud browser...")
        browser = await client.browsers.create()
        
        async with async_playwright() as p:
            pw_browser = await p.chromium.connect_over_cdp(browser.cdp_url)
            context = pw_browser.contexts[0]
            page = context.pages[0]
            
            print("🌐 Opening login page...")
            await page.goto("https://www.easyhits4u.com/logon/")
            
            print("📝 Filling form...")
            await page.fill('#username', EMAIL)
            await page.fill('#password', PASSWORD)
            
            token = await wait_for_turnstile_token(page)
            
            if token:
                print("🔐 Turnstile resolved, proceeding...")
            
            await page.wait_for_timeout(1000)
            
            print("🔑 Pressing Enter...")
            await page.keyboard.press('Enter')
            
            print("⏳ Waiting for redirect...")
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(5000)
            
            print("\n🍪 Fetching ALL cookies...")
            all_cookies = await context.cookies()
            
            # Organizza i cookie
            login_cookies = {}
            navigation_cookies = {}
            
            login_names = ['sesids', 'user_id', 'has_account', 'no_auto_login', 'se']
            
            for cookie in all_cookies:
                cookie_info = {
                    'value': cookie['value'],
                    'domain': cookie.get('domain', ''),
                    'path': cookie.get('path', ''),
                    'secure': cookie.get('secure', False),
                    'httpOnly': cookie.get('httpOnly', False)
                }
                
                if cookie['name'] in login_names:
                    login_cookies[cookie['name']] = cookie_info
                else:
                    navigation_cookies[cookie['name']] = cookie_info
            
            divella_cookies = {
                'sesids': login_cookies.get('sesids', {}).get('value'),
                'user_id': login_cookies.get('user_id', {}).get('value')
            }
            
            cookies_data = {
                'timestamp': datetime.now().isoformat(),
                'url': page.url,
                'login_cookies': login_cookies,
                'navigation_cookies': navigation_cookies,
                'divella_cookies': divella_cookies,
                'all_cookies': {c['name']: c['value'] for c in all_cookies}
            }
            
            print("\n" + "=" * 60)
            print("📊 COOKIE OTTENUTI")
            print("=" * 60)
            
            print("\n🔐 Login Cookies:")
            for name, info in login_cookies.items():
                print(f"   {name} = {info['value']}")
            
            print("\n🤖 Divella Cookies (essenziali):")
            print(f"   sesids = {divella_cookies['sesids']}")
            print(f"   user_id = {divella_cookies['user_id']}")
            
            print(f"\n📍 Final URL: {page.url}")
            
            with open("/tmp/cookies.json", "w") as f:
                json.dump(cookies_data, f, indent=2)
            print("\n💾 Cookies saved to /tmp/cookies.json")
            
            await pw_browser.close()
        
        await client.browsers.stop(browser.id)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        cookies_data = {'error': str(e), 'timestamp': datetime.now().isoformat()}
    
    return cookies_data

async def main():
    cookies = await get_all_cookies()
    
    print("\n" + "=" * 60)
    if cookies.get('divella_cookies', {}).get('sesids'):
        print("🎉🎉🎉 SUCCESSO! 🎉🎉🎉")
        print(f"   sesids = {cookies['divella_cookies']['sesids']}")
        print(f"   user_id = {cookies['divella_cookies']['user_id']}")
    else:
        print("❌ Cookie non ottenuti")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())