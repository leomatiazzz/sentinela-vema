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

    # Seleciona as abas usando o seletor que funcionou perfeitamente
    tabs = page.query_selector_all('[data-baseweb="tab"]')
    if not tabs:
        tabs = page.query_selector_all('button[role="tab"], [data-testid="stTab"]')
    print(f"Total de abas encontradas: {len(tabs)}")
    for i, t in enumerate(tabs):
        print(f"Tab {i}: {t.inner_text()}")

    # 1. Aba 1 - Panorama
    page.screenshot(path=f"{OUTPUT_DIR}/tab1_panorama.png", full_page=True)
    print("Tab 1 capturada.")

    # 2. Aba 2 - Triagem e Julgamento em Bloco
    if len(tabs) > 1:
        tabs[1].click()
        time.sleep(1.5)
        # Clica no botão de gerar minuta
        btn_minuta = page.query_selector('button:has-text("Gerar minuta de despacho")')
        if btn_minuta:
            btn_minuta.click()
            time.sleep(1.5)
            print("Botão de minuta acionado.")
        page.screenshot(path=f"{OUTPUT_DIR}/tab2_triagem.png", full_page=True)
        print("Tab 2 capturada.")

    # 3. Aba 3 - Investigador de Similaridade
    if len(tabs) > 2:
        tabs[2].click()
        time.sleep(1.5)
        # Clica no botão de buscar similares por processo
        btn_busca = page.query_selector('button:has-text("Buscar processos similares")')
        if btn_busca:
            btn_busca.click()
            time.sleep(2)
            print("Busca por similaridade acionada.")
        page.screenshot(path=f"{OUTPUT_DIR}/tab3_similaridade_processo.png", full_page=True)
        print("Tab 3 (por processo) capturada.")

        # Agora testa o modo B: Análise de fatos livres
        radio_fatos = page.query_selector('label:has-text("Analisar nova demanda")')
        if radio_fatos:
            radio_fatos.click()
            time.sleep(1.5)
            btn_busca_fatos = page.query_selector('button:has-text("Buscar precedentes semelhantes na VEMA")')
            if btn_busca_fatos:
                btn_busca_fatos.click()
                time.sleep(2)
                print("Busca por texto fático acionada.")
            page.screenshot(path=f"{OUTPUT_DIR}/tab3_similaridade_fatos.png", full_page=True)
            print("Tab 3 (por fatos) capturada.")

    # 4. Aba 4 - Diferenciais e Arquitetura
    if len(tabs) > 3:
        tabs[3].click()
        time.sleep(1.5)
        page.screenshot(path=f"{OUTPUT_DIR}/tab4_arquitetura.png", full_page=True)
        print("Tab 4 capturada.")

    browser.close()
    print("Todas as inspeções DOM e capturas foram concluídas com sucesso!")
