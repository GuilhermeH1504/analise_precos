"""
Script principal para rodar os scrapers de PS5, consolidar a base atual
e alimentar um historico simples de precos.
"""

from automacao import scrape_ps5_prices as scrape_amazon
from dados import append_history, clean_results, get_timestamp, save_snapshot
from mercado import scrape_ps5_prices as scrape_mercado


def main():
    print("=" * 60)
    print("INICIANDO SCRAPERS DE PS5")
    print("=" * 60)

    collected_at = get_timestamp()

    print("\n[1/2] Raspando Amazon...")
    amazon_results = scrape_amazon(max_pages=2)
    print(f"[OK] Amazon: {len(amazon_results)} produtos encontrados")

    print("\n[2/2] Raspando Mercado Livre...")
    mercado_results = scrape_mercado(max_pages=2)
    print(f"[OK] Mercado Livre: {len(mercado_results)} produtos encontrados")

    all_results = amazon_results + mercado_results
    cleaned_results = clean_results(all_results, collected_at=collected_at)

    print(f"\n{'=' * 60}")
    print(f"TOTAL BRUTO: {len(all_results)} produtos encontrados")
    print(f"TOTAL LIMPO: {len(cleaned_results)} produtos com preco valido")
    print(f"{'=' * 60}")

    output_json = "ps5_consolidado.json"
    output_csv = "ps5_consolidado.csv"
    history_csv = "historico_precos.csv"

    save_snapshot(cleaned_results, csv_path=output_csv, json_path=output_json)
    append_history(cleaned_results, history_path=history_csv)

    print(f"[OK] JSON consolidado: {output_json}")
    print(f"[OK] CSV consolidado: {output_csv}")
    print(f"[OK] Historico atualizado: {history_csv}")
    print("\nScraping concluido com sucesso!")


if __name__ == "__main__":
    main()
