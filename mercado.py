import csv
import json
import time

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

SEARCH_URL = "https://lista.mercadolivre.com.br/ps5"
OUTPUT_JSON = "mercado_ps5.json"
OUTPUT_CSV  = "mercado_ps5.csv"

def create_browser_context(playwright):
    browser = playwright.chromium.launch(
        headless=False,
        args=["--disable-blink-features=AutomationControlled"]
    )
    context = browser.new_context(
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/126.0.0.0 Safari/537.36"
        ),
        viewport={"width": 1280, "height": 720},
        locale="pt-BR",
    )
    context.add_init_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
    )
    return browser, context

def extract_title(item) -> str:
    try:
        el = item.query_selector("h2.poly-box a")
        title = el.get_attribute("aria-label") if el else ""
        if not title:
            h2 = item.query_selector("h2.poly-box")
            title = h2.inner_text().strip() if h2 else ""
        return title
    except Exception:
        return ""
    
def extract_price(item) -> str:
    try:
        reais = item.query_selector("span.andes-money-amount__fraction")
        centavos = item.query_selector("span.andes-money-amount__cents")

        if reais:
            preco = reais.inner_text().strip()
            if centavos:
                preco += f",{centavos.inner_text().strip()}"
            return f"R$ {preco}"
        return ""
    except Exception:
        return ""
    
def extract_link(item) -> str:
    try:
        el = item.query_selector("h2.poly-box a")
        href = el.get_attribute("href") if el else ""
        return href.split("#")[0] if href else ""
    except Exception:
        return ""
    
def extract_saller(item) -> str:
    try:
        el = item.query_selector("span.poly-component__saller")
        return el.inner_text().strip() if el else ""
    except Exception:
        return ""
    
def scrape_ps5_prices(max_pages: int = 2):
    results = []

    with sync_playwright() as p:
        browser, context = create_browser_context(p)
        page = context.new_page()

        try:
            page.goto(SEARCH_URL)
            page.wait_for_selector("li.ui-search-layout__item", timeout=15000)

            for page_number in range(max_pages):
                print(f"\nProcessando pagina {page_number + 1}..." )
                page.wait_for_selector("li.ui-search-layout__item")

                items = page.query_selector_all("li.ui-search-layout__item")

                for item in items:
                    # Extrair título
                    title_el = item.query_selector("a.poly-component__title")
                    if not title_el:
                        continue
                    title = title_el.inner_text().strip()
                    
                    if not title:
                        continue
                    
                    normalized = title.lower()
                    if "ps5" not in normalized and "playstation 5" not in normalized:
                        continue

                    # Extrair preço
                    price = extract_price(item)

                    # Extrair link
                    link = title_el.get_attribute("href") or ""

                    results.append({
                        "site": "Mercado Livre",
                        "title": title,
                        "price": price,
                        "url": link,
                        "saller": ""
                    })
                    print(f"  ✓ {title[:60]}... | {price}")

                try:
                    next_btn = page.query_selector("a.andes-pagination__link[title='seguinte']")
                    if not next_btn:
                        next_btn = page.query_selector("a[aria-label='Seguinte']")

                    if not next_btn:
                        print("sem mais paginas")
                        break

                    next_btn.click()
                    page.wait_for_load_state("networkidle")
                    time.sleep(1)

                except PlaywrightTimeoutError:
                    print("sem mais paginas")
                    break
        finally:
            browser.close()

    return results

if __name__ == "__main__":
    extracted = scrape_ps5_prices(max_pages = 2)
    print(f"\nExtraídos {len(extracted)} produtos de PS5 no Mercado Livre")

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(extracted, f, ensure_ascii=False, indent=2)

    with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["site", "title", "price", "url", "saller"])
        writer.writeheader()
        for item in extracted:
            writer.writerow(item)

    print(f"Dados salvos em {OUTPUT_JSON} e {OUTPUT_CSV}")
