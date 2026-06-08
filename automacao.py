import csv
import json
import time

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

SEARCH_URL = "https://www.amazon.com.br/s?k=ps5"
OUTPUT_JSON = "amazon_ps5.json"
OUTPUT_CSV  = "amazon_ps5.csv"


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
    context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")

    return browser, context


def accept_cookies(page) -> None:
    
    try:
        cookie_btn = page.query_selector("#sp-cc-accept")
        if cookie_btn:
            cookie_btn.click()
            time.sleep(1)
    except Exception:
        pass


def extract_title(item) -> str:
    
    try:
        el = item.query_selector("h2")
        return el.inner_text().strip() if el else ""
    except Exception:
        return ""


def extract_price(item) -> str:
    try:
        el = item.query_selector("span.a-price span.a-offscreen")
        return el.inner_text().strip() if el else ""
    except Exception:
        return ""


def extract_link(item, title: str) -> str:
    
    anchors = item.query_selector_all("a.a-link-normal")

    for anchor in anchors:
        href = anchor.get_attribute("href") or ""
        text = anchor.inner_text().strip()
        if href and title and title.lower() in text.lower():
            return href

    for anchor in anchors:
        href = anchor.get_attribute("href") or ""
        if href and "/dp/" in href:
            return href

    return ""


def scrape_ps5_prices(max_pages: int = 2):
    results = []

    
    with sync_playwright() as p:
        browser, context = create_browser_context(p)
        page = context.new_page()

        try:
            page.goto(SEARCH_URL)
            accept_cookies(page)

          
            page.wait_for_selector("div.s-main-slot")

            for page_number in range(max_pages):
                print(f"\nProcessando página {page_number + 1}...")

                page.wait_for_selector("div.s-main-slot")

               
                items = page.query_selector_all(
                    "div.s-main-slot div[data-component-type='s-search-result']"
                )

                for item in items:
                    title = extract_title(item)
                    if not title:
                        continue

                    normalized = title.lower()
                    if "ps5" not in normalized and "playstation 5" not in normalized:
                        continue

                    price = extract_price(item)
                    link  = extract_link(item, title)
                    asin  = item.get_attribute("data-asin") or ""

                    if link.startswith("/"):
                        link = "https://www.amazon.com.br" + link

                    results.append({
                        "site": "Amazon",
                        "asin":  asin,
                        "title": title,
                        "price": price,
                        "url":   link,
                    })

                    print(f"  ✓ {title[:60]}... | {price}")

                
                try:
                    next_btn = page.query_selector("ul.a-pagination li.a-last a")
                    if not next_btn:
                        print("Sem mais páginas.")
                        break

                    next_btn.click()

                   
                    page.wait_for_load_state("networkidle")
                    time.sleep(1)

                except PlaywrightTimeoutError:
                    print("Timeout na paginação.")
                    break

        finally:
            browser.close()

    return results


if __name__ == "__main__":
    extracted = scrape_ps5_prices(max_pages=2)
    print(f"\nExtraídos {len(extracted)} produtos de PS5")

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(extracted, f, ensure_ascii=False, indent=2)

    with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["site", "asin", "title", "price", "url"])
        writer.writeheader()
        for item in extracted:
            writer.writerow(item)

    print(f"Dados salvos em {OUTPUT_JSON} e {OUTPUT_CSV}")
