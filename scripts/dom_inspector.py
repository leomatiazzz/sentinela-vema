"""
DOM Browser & Inspector para Streamlit (Sentinela-VEMA).
Utiliza Playwright para navegar, coletar logs do console, testar cliques e capturar erros e screenshots.
"""
import os
import time
from playwright.sync_api import sync_playwright

CHROME_PATH = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
OUTPUT_DIR = "data/inspect"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def inspecionar():
    console_messages = []
    page_errors = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=CHROME_PATH,
            headless=True
        )
        page = browser.new_page(viewport={"width": 1400, "height": 900})

        page.on("console", lambda msg: console_messages.append(f"[{msg.type}] {msg.text}"))
        page.on("pageerror", lambda err: page_errors.append(str(err)))

        print("Navegando para http://localhost:8501...")
        page.goto("http://localhost:8501", wait_until="networkidle", timeout=30000)
        time.sleep(3)  # aguarda renderização completa do Streamlit

        # 1. Screenshot e DOM da página inicial (Tab 1)
        page.screenshot(path=f"{OUTPUT_DIR}/tab1_inicial.png", full_page=True)
        print("Screenshot da Tab 1 capturada.")

        # Verifica textos e elementos da Tab 1
        tabs = page.query_selector_all('[data-baseweb="tab"]')
        print(f"Abas encontradas: {len(tabs)}")
        for idx, t in enumerate(tabs):
            print(f"  Aba {idx + 1}: {t.inner_text()}")

        # 2. Testa Navegação para Tab 2
        print("\nClicando na Aba 2 (Triagem e julgamento em bloco)...")
        tabs[1].click()
        time.sleep(2)
        page.screenshot(path=f"{OUTPUT_DIR}/tab2_clustering.png", full_page=True)
        
        # Testa botão de gerar minuta na Tab 2
        btn_minuta = page.query_selector("button:has-text('Gerar minuta')")
        if btn_minuta:
            print("Botão 'Gerar minuta' encontrado. Clicando...")
            btn_minuta.click()
            time.sleep(2)
            page.screenshot(path=f"{OUTPUT_DIR}/tab2_minuta_gerada.png", full_page=True)
            print("Minuta gerada com sucesso.")
        else:
            print("AVISO: Botão 'Gerar minuta' NÃO encontrado!")

        # 3. Testa Navegação para Tab 3
        print("\nClicando na Aba 3 (Investigador de similaridade)...")
        tabs[2].click()
        time.sleep(2)
        page.screenshot(path=f"{OUTPUT_DIR}/tab3_similaridade.png", full_page=True)

        # Testa busca por processo na Tab 3
        btn_buscar_proc = page.query_selector("button:has-text('Buscar processos similares')")
        if btn_buscar_proc:
            print("Botão 'Buscar processos similares' encontrado. Clicando...")
            btn_buscar_proc.click()
            time.sleep(3)
            page.screenshot(path=f"{OUTPUT_DIR}/tab3_resultado_processo.png", full_page=True)
            print("Busca por processo executada.")
        else:
            print("AVISO: Botão 'Buscar processos similares' NÃO encontrado!")

        # Testa Modo B (Fatos livres)
        radio_fatos = page.query_selector("label:has-text('Analisar nova demanda')")
        if radio_fatos:
            print("Alternando para Modo B (Fatos livres)...")
            radio_fatos.click()
            time.sleep(2)
            btn_buscar_fatos = page.query_selector("button:has-text('Buscar precedentes')")
            if btn_buscar_fatos:
                print("Botão 'Buscar precedentes semelhantes na VEMA' encontrado. Clicando...")
                btn_buscar_fatos.click()
                time.sleep(3)
                page.screenshot(path=f"{OUTPUT_DIR}/tab3_resultado_fatos.png", full_page=True)
                print("Busca por fatos executada.")

        # 4. Testa Navegação para Tab 4
        print("\nClicando na Aba 4 (Diferenciais e arquitetura)...")
        tabs[3].click()
        time.sleep(2)
        page.screenshot(path=f"{OUTPUT_DIR}/tab4_arquitetura.png", full_page=True)

        # Verifica se a imagem da arquitetura carregou
        img_arq = page.query_selector("img[src*='arquitetura']")
        all_imgs = page.query_selector_all("img")
        print(f"Total de imagens na página: {len(all_imgs)}")
        for img in all_imgs:
            src = img.get_attribute("src") or ""
            print(f"  Imagem src: {src[:80]}")

        # Salva log de console e erros
        print(f"\nTotal de mensagens no console: {len(console_messages)}")
        for m in console_messages:
            if "error" in m.lower() or "warning" in m.lower():
                print("  " + m)

        print(f"\nTotal de erros de página não capturados: {len(page_errors)}")
        for err in page_errors:
            print("  ERRO: " + err)

        browser.close()
        print("\nInspeção visual e funcional concluída.")

if __name__ == "__main__":
    inspecionar()

