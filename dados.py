import csv
import json
import re
from datetime import datetime
from pathlib import Path


SNAPSHOT_FIELDS = ["coleta_em", "site", "title", "price", "price_num", "url"]


def get_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def fix_text(value) -> str:
    if value is None:
        return ""

    text = str(value).strip().replace("\xa0", " ")

    if any(marker in text for marker in ("Ã", "Â", "â")):
        try:
            repaired = text.encode("latin1").decode("utf-8")
            if repaired.count("�") <= text.count("�"):
                text = repaired
        except UnicodeError:
            pass

    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_price_text(value) -> str:
    text = fix_text(value)
    if not text:
        return ""
    return re.sub(r"^R\$\s*", "R$ ", text)


def parse_price(value):
    text = normalize_price_text(value)
    number = re.sub(r"[^0-9,.]", "", text)

    if not number:
        return None

    if "," in number:
        normalized = number.replace(".", "").replace(",", ".")
    else:
        parts = number.split(".")
        if len(parts) == 1:
            normalized = parts[0]
        elif len(parts[-1]) == 2:
            normalized = "".join(parts[:-1]) + "." + parts[-1]
        else:
            normalized = "".join(parts)

    try:
        return float(normalized)
    except ValueError:
        return None


def infer_site(site: str, url: str) -> str:
    clean_site = fix_text(site)
    if clean_site:
        return clean_site

    url_lower = fix_text(url).lower()
    if "amazon." in url_lower:
        return "Amazon"
    if "mercadolivre." in url_lower or "mercado livre" in url_lower:
        return "Mercado Livre"
    return ""


def clean_item(item: dict, collected_at: str) -> dict:
    url = fix_text(item.get("url", ""))
    price = normalize_price_text(item.get("price", ""))
    price_num = parse_price(price)

    return {
        "coleta_em": item.get("coleta_em") or collected_at,
        "site": infer_site(item.get("site", ""), url),
        "title": fix_text(item.get("title", "")),
        "price": price,
        "price_num": "" if price_num is None else f"{price_num:.2f}",
        "url": url,
    }


def clean_results(results, collected_at: str | None = None) -> list[dict]:
    timestamp = collected_at or get_timestamp()
    cleaned = [clean_item(item, timestamp) for item in results]

    return [
        item
        for item in cleaned
        if item["title"] and item["price_num"] and item["url"]
    ]


def save_snapshot(rows: list[dict], csv_path: str, json_path: str) -> None:
    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(rows, file, ensure_ascii=False, indent=2)

    with open(csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=SNAPSHOT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def append_history(rows: list[dict], history_path: str = "historico_precos.csv") -> None:
    path = Path(history_path)
    write_header = not path.exists() or path.stat().st_size == 0

    with open(path, "a", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=SNAPSHOT_FIELDS)
        if write_header:
            writer.writeheader()
        writer.writerows(rows)


def load_csv_rows(csv_path: str) -> list[dict]:
    with open(csv_path, encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))
