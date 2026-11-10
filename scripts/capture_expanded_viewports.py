from playwright.sync_api import sync_playwright
from PIL import Image

CHROME_PATH = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=CHROME_PATH, headless=True)
    # Viewport alta para ver todo o conteúdo de uma vez
    page = browser.new_page(viewport={"width": 1440, "height": 1800})
    page.goto("http://localhost:8501", wait_until="networkidle")
    page.wait_for_timeout(3000)

    # Captura viewport expandida
    page.screenshot(path="data/inspect/tab1_panorama_full.png")
    
    # Encontra todas as abas
    tabs = page.query_selector_all('button[role="tab"], [data-baseweb="tab"], [data-testid="stTab"]')
    print(f"Abas encontradas: {len(tabs)}")
    for i, t in enumerate(tabs):
        print(f"Aba {i}: {t.inner_text()}")
    
    # Aba 1
    page.screenshot(path="data/inspect/tab1_panorama_full.png")
    print("Aba 1 capturada.")
    
    # Aba 2
    if len(tabs) > 1:
        tabs[1].click()
        page.wait_for_timeout(1500)
        btn_minuta = page.query_selector('button:has-text("Gerar minuta de despacho padronizado em lote")')
        if btn_minuta:
            btn_minuta.click()
            page.wait_for_timeout(1500)
        page.screenshot(path="data/inspect/tab2_triagem_full.png")
        print("Aba 2 capturada.")

    # Aba 3
    if len(tabs) > 2:
        tabs[2].click()
        page.wait_for_timeout(1500)
        btn = page.query_selector('button:has-text("Buscar processos similares")')
        if btn:
            btn.click()
            page.wait_for_timeout(2500)
        page.screenshot(path="data/inspect/tab3_similaridade_full.png")
        print("Aba 3 capturada.")

    # Aba 4
    if len(tabs) > 3:
        tabs[3].click()
        page.wait_for_timeout(1500)
        page.screenshot(path="data/inspect/tab4_arquitetura_full.png")
        print("Aba 4 capturada.")

    browser.close()
    print("Capturas com viewport expandida concluídas com sucesso!")

