import asyncio
import json
import os
from browser_use_sdk.v3 import AsyncBrowserUse
from playwright.async_api import async_playwright
from datetime import datetime

# NUOVA API KEY
API_KEY = os.environ.get("BROWSER_USE_API_KEY", "bu_p13_SIvj0Y2JtzsA7fyZZ72xwlmmNMixXMyYft1ZA5s")

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
            
            # === STAMPA TUTTI I COOKIE NEL LOG ===
            print("\n" + "=" * 60)
            print("📋 LISTA COMPLETA COOKIE")
            print("=" * 60)
            
            login_names = ['sesids', 'user_id', 'has_account', 'no_auto_login', 'se']
            
            for cookie in all_cookies:
                print(f"\n🍪 {cookie['name']}")
                print(f"   Value: {cookie['value']}")
                print(f"   Domain: {cookie.get('domain', 'N/A')}")
                print(f"   Path: {cookie.get('path', 'N/A')}")
                print(f"   Secure: {cookie.get('secure', False)}")
                print(f"   HttpOnly: {cookie.get('httpOnly', False)}")
                if cookie.get('expires'):
                    print(f"   Expires: {datetime.fromtimestamp(cookie['expires']).isoformat()}")
            
            # Cookie specifici per Divella
            sesids = next((c['value'] for c in all_cookies if c['name'] == 'sesids'), None)
            user_id = next((c['value'] for c in all_cookies if c['name'] == 'user_id'), None)
            
            print("\n" + "=" * 60)
            print("🎯 COOKIE PER DIVELLA")
            print("=" * 60)
            print(f"sesids = {sesids}")
            print(f"user_id = {user_id}")
            
            # Formato per Divella (copia-incolla)
            print("\n" + "=" * 60)
            print("📋 FORMATO COPIA-INCOLLA PER DIVELLA")
            print("=" * 60)
            print(f"session.cookies.set('sesids', '{sesids}')")
            print(f"session.cookies.set('user_id', '{user_id}')")
            
            cookies_data = {
                'timestamp': datetime.now().isoformat(),
                'url': page.url,
                'all_cookies': {c['name']: c['value'] for c in all_cookies},
                'divella_cookies': {'sesids': sesids, 'user_id': user_id}
            }
            
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
    else:
        print("❌ Cookie non ottenuti")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
