import os
import time
from playwright.sync_api import sync_playwright

CHROME_PATH = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
OUTPUT_DIR = "data/inspect"
os.makedirs(OUTPUT_DIR, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=CHROME_PATH, headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 950})
    page.goto("http://localhost:8501", wait_until="networkidle")
    time.sleep(3)

    # Encontra botões das abas
    tabs = page.query_selector_all('[data-testid="stTab"], [data-baseweb="tab"], button[role="tab"]')
    print(f"Total de abas encontradas: {len(tabs)}")
    for i, t in enumerate(tabs):
        print(f"Tab {i}: {t.inner_text()}")

    # Captura Tab 1 completo (scroll)
    page.screenshot(path=f"{OUTPUT_DIR}/screen_tab1.png", full_page=True)

    # Clica na Tab 2
    if len(tabs) > 1:
        tabs[1].click()
        time.sleep(2)
        page.screenshot(path=f"{OUTPUT_DIR}/screen_tab2.png", full_page=True)
        print("Tab 2 capturada.")

    # Clica na Tab 3
    if len(tabs) > 2:
        tabs[2].click()
        time.sleep(2)
        page.screenshot(path=f"{OUTPUT_DIR}/screen_tab3.png", full_page=True)
        print("Tab 3 capturada.")

    # Clica na Tab 4
    if len(tabs) > 3:
        tabs[3].click()
        time.sleep(2)
        page.screenshot(path=f"{OUTPUT_DIR}/screen_tab4.png", full_page=True)
        print("Tab 4 capturada.")

    browser.close()

