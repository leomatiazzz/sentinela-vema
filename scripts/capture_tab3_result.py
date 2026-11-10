from playwright.sync_api import sync_playwright

CHROME_PATH = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=CHROME_PATH, headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 1800})
    page.goto("http://localhost:8501", wait_until="networkidle")
    page.wait_for_timeout(3000)

    # Seleciona Aba 3
    tabs = page.query_selector_all('[data-baseweb="tab"]')
    if not tabs:
        tabs = page.query_selector_all('[data-testid="stTab"], button[role="tab"]')
    
    tabs[2].click()
    page.wait_for_timeout(1000)
    
    btn = page.query_selector('button:has-text("Buscar processos similares")')
    if btn:
        btn.click()
        page.wait_for_timeout(2500)
    
    page.screenshot(path="data/inspect/tab3_resultado_similaridade.png")
    browser.close()
    print("Captura da busca por similaridade concluída!")

