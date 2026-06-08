# Documentação Playwright - Guia Prático

## 📚 Índice
1. [O que é Playwright?](#o-que-é-playwright)
2. [Instalação](#instalação)
3. [Conceitos Básicos](#conceitos-básicos)
4. [Browser e Context](#browser-e-context)
5. [Seletores CSS](#seletores-css)
6. [Localizadores (Locators)](#localizadores-locators)
7. [Interações com Página](#interações-com-página)
8. [Esperas (Waits)](#esperas-waits)
9. [Extração de Dados](#extração-de-dados)
10. [Exemplos Práticos](#exemplos-práticos)

---

## O que é Playwright?

**Playwright** é uma biblioteca Python para automação de navegadores web. Permite:
- ✅ Controlar Chrome, Firefox, Safari
- ✅ Simular ações humanas (clique, digitação)
- ✅ Extrair dados de páginas dinâmicas
- ✅ Testar aplicações web
- ✅ Fazer web scraping

### Vantagens:
- Suporta múltiplos navegadores
- Async/await para operações rápidas
- Bom para sites com JavaScript
- Anti-detecção de bot integrada

---

## Instalação

```bash
pip install playwright
playwright install
```

Ou com webdriver-manager (automático):
```bash
pip install playwright webdriver-manager
```

---

## Conceitos Básicos

### Estrutura Hierárquica

```
playwright
    ├── browser (Chrome, Firefox, Safari)
    │   ├── context (abas, cookies isolados)
    │   │   └── page (página individual)
    │   │       ├── locator (seletor de elemento)
    │   │       └── frame (iframe)
    └── sync_playwright (API síncrona)
```

---

## Browser e Context

### Criar um Browser

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    # Lançar navegador Chrome
    browser = p.chromium.launch(headless=False)
    
    # headless=True  → sem interface gráfica
    # headless=False → com interface gráfica
    
    browser.close()
```

### Context (Contexto Isolado)

Um contexto é como uma "aba anônima" - tem cookies, localStorage, etc. isolados.

```python
browser = p.chromium.launch()

# Criar contexto com user agent
context = browser.new_context(
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...",
    viewport={"width": 1280, "height": 720},
    locale="pt-BR",
)

# Adicionar script de anti-detecção
context.add_init_script(
    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
)

page = context.new_page()
```

---

## Seletores CSS

Playwright usa **seletores CSS** para encontrar elementos. Exemplos:

```python
# Por tag
page.locator("h1")
page.locator("button")

# Por classe
page.locator(".titulo")
page.locator("a.link-azul")

# Por ID
page.locator("#botao-submit")

# Por atributo
page.locator("input[type='email']")
page.locator("[data-testid='search']")

# Combinações
page.locator("div.container h2 span")
page.locator("li.item:nth-child(2)")

# Pseudo-seletores
page.locator("a:first-child")
page.locator("button:last-of-type")
```

### Seletores Úteis para Web Scraping

```python
# Encontrar todas as colunas de uma tabela
page.locator("table tr td")

# Encontrar links
page.locator("a[href*='amazon.com']")

# Elementos com texto específico
page.locator("button:has-text('Próximo')")

# Classes múltiplas
page.locator("span.a-price.a-color-base")
```

---

## Localizadores (Locators)

**Locator** é um objeto que representa um seletor. Ele é **preguiçoso** (lazy):

```python
# Criar locator (não executa ainda)
button = page.locator("button#submit")

# Contar elementos
count = button.count()  # Quantos botões com ID "submit"?

# Pegar o primeiro
first_button = button.first
# ou
first_button = page.locator("button#submit").first

# Pegar um específico
second = button.nth(1)

# Testar se existe
exists = button.count() > 0
```

### Métodos Importantes do Locator

```python
# Obter texto
text = locator.inner_text()

# Obter HTML
html = locator.inner_html()

# Obter atributo
href = locator.get_attribute("href")
data_id = locator.get_attribute("data-id")

# Verificar visibilidade
is_visible = locator.is_visible()

# Verificar se está habilitado
is_enabled = locator.is_enabled()
```

---

## Interações com Página

### Navegar

```python
# Ir para URL
page.goto("https://www.amazon.com.br/s?k=ps5")

# Esperar carregar
page.goto(url, wait_until="domcontentloaded")  # apenas DOM
page.goto(url, wait_until="networkidle")       # sem requisições pendentes

# Voltar/Avançar
page.go_back()
page.go_forward()

# Recarregar
page.reload()
```

### Cliques e Digitação

```python
# Clicar
button = page.locator("button.submit")
button.click()

# Digitar em input
input_field = page.locator("input#search")
input_field.fill("ps5")  # Limpa e digita

# Pressionar tecla específica
input_field.press("Enter")
input_field.press("Tab")

# Limpar input
input_field.fill("")
```

### Scroll

```python
# Scroll para elemento
element = page.locator("h2#target")
element.scroll_into_view()

# Scroll genérico
page.evaluate("window.scrollBy(0, 500)")
```

---

## Esperas (Waits)

### wait_for_selector (Seletor aparecer)

```python
# Esperar até 15 segundos
page.wait_for_selector("div.s-main-slot", timeout=15000)

# Se não encontrar em 15s, lança TimeoutError
```

### wait_for_load_state (Página carregar)

```python
# Esperar DOM construído
page.wait_for_load_state("domcontentloaded")

# Esperar sem requisições pendentes
page.wait_for_load_state("networkidle")

# Usar após clicar botão de próxima página
button.click()
page.wait_for_load_state("networkidle")
time.sleep(1)  # Extra safety
```

### wait_for_timeout (Aguardar X ms)

```python
# Esperar 2 segundos (útil antes de aceitar cookies)
page.wait_for_timeout(2000)
# ou
import time
time.sleep(2)
```

---

## Extração de Dados

### Extrair de um elemento

```python
# Título
title = page.locator("h2").inner_text()

# Preço
price = page.locator("span.price").inner_text()  # "R$ 1.234,00"

# Link
href = page.locator("a.product").get_attribute("href")

# Múltiplos valores
links = page.locator("a.product")
for i in range(links.count()):
    url = links.nth(i).get_attribute("href")
    print(url)
```

### Extrair lista completa

```python
# Pegar todos os produtos
items = page.locator("div.product-item")

results = []
for i in range(items.count()):
    item = items.nth(i)
    title = item.locator("h2").inner_text()
    price = item.locator("span.price").inner_text()
    link = item.locator("a").get_attribute("href")
    
    results.append({
        "title": title,
        "price": price,
        "url": link
    })
```

### Usar query_selector (Alternativa)

```python
# Equivalente ao locator, mas retorna ElementHandle
element = page.query_selector("h2")
element.inner_text()

# Múltiplos
items = page.query_selector_all("div.item")
for item in items:
    title = item.query_selector("h2").inner_text()
```

---

## Exemplos Práticos

### Exemplo 1: Scraping Amazon PS5

```python
from playwright.sync_api import sync_playwright
import json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    page = context.new_page()
    
    # Navegar
    page.goto("https://www.amazon.com.br/s?k=ps5", wait_until="domcontentloaded")
    
    # Esperar resultados
    page.wait_for_selector("div.s-main-slot", timeout=15000)
    
    # Extrair dados
    items = page.locator("div.s-main-slot div[data-component-type='s-search-result']")
    results = []
    
    for i in range(items.count()):
        item = items.nth(i)
        title = item.locator("h2").inner_text()
        
        # Filtrar PS5
        if "ps5" not in title.lower():
            continue
        
        price_el = item.locator("span.a-offscreen")
        price = price_el.inner_text() if price_el.count() > 0 else ""
        
        results.append({
            "title": title,
            "price": price
        })
    
    print(f"Encontrados {len(results)} produtos")
    
    browser.close()
```

### Exemplo 2: Paginação

```python
# Scraping com múltiplas páginas
for page_num in range(3):
    print(f"Página {page_num + 1}")
    
    # Extrair dados...
    items = page.locator("div.item")
    
    # Próxima página
    try:
        next_button = page.locator("a.next-page")
        if next_button.count() > 0:
            next_button.click()
            page.wait_for_load_state("networkidle")
            import time
            time.sleep(1)
    except:
        break
```

### Exemplo 3: Preenchendo Formulário

```python
# Preencher campo de busca
search = page.locator("input#search")
search.fill("PlayStation 5")
search.press("Enter")

page.wait_for_load_state("networkidle")
```

### Exemplo 4: Aceitar Cookies

```python
# Tentar clicar botão de aceitar
try:
    accept_btn = page.locator("button#accept-cookies")
    if accept_btn.count() > 0:
        accept_btn.click()
        page.wait_for_timeout(1000)
except:
    pass  # Pode não existir
```

---

## Dicas e Truques

### 1. Anti-Detecção de Bot

```python
# Adicionar ao contexto
context.add_init_script(
    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
)
```

### 2. Verificar Se Elemento Existe

```python
if page.locator("h2").count() > 0:
    title = page.locator("h2").inner_text()
```

### 3. Try-Except para Elementos Opcionais

```python
try:
    price = page.locator("span.price").inner_text()
except:
    price = ""
```

### 4. Múltiplas Tentativas

```python
import time
for attempt in range(3):
    try:
        page.goto(url, timeout=10000)
        break
    except:
        print(f"Tentativa {attempt + 1} falhou, retentando...")
        time.sleep(2)
```

### 5. Salvar Screenshot (Debug)

```python
page.screenshot(path="debug.png")
```

### 6. Inspecionar HTML

```python
html = page.content()
print(html[:500])
```

---

## Comparação: Locator vs query_selector

```python
# Locator (recomendado)
page.locator("h2").count()           # Lazy
page.locator("h2").first             # Pega primeiro

# query_selector (mais direto)
page.query_selector("h2")            # Retorna elemento ou None
page.query_selector_all("h2")        # Retorna lista

# Ambos funcionam, Locator é mais legível
```

---

## Tratamento de Erros

```python
from playwright.sync_api import sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

try:
    page.wait_for_selector("div.results", timeout=5000)
except PlaywrightTimeoutError:
    print("Elemento não encontrado em 5 segundos")

try:
    page.goto(url, timeout=10000)
except Exception as e:
    print(f"Erro ao navegar: {e}")
```

---

## Referência Rápida

| Operação | Código |
|----------|--------|
| Navegar | `page.goto(url)` |
| Esperar elemento | `page.wait_for_selector(css)` |
| Clicar | `page.locator(css).click()` |
| Digitar | `page.locator(css).fill(text)` |
| Pegar texto | `page.locator(css).inner_text()` |
| Pegar atributo | `page.locator(css).get_attribute(attr)` |
| Contar elementos | `page.locator(css).count()` |
| Primeiro elemento | `page.locator(css).first` |
| Elemento N | `page.locator(css).nth(n)` |
| Scroll | `page.locator(css).scroll_into_view()` |
| Screenshot | `page.screenshot(path=file)` |

---

## Recursos Adicionais

- [Documentação Oficial](https://playwright.dev/python/)
- [Seletores CSS](https://developer.mozilla.org/pt-BR/docs/Web/CSS/Seletor)
- [Locators API](https://playwright.dev/python/docs/locators)

---

## Seu Projeto

Você está usando Playwright em:
- ✅ `automacao.py` — Scraping Amazon com Playwright
- ✅ `mercado.py` — Scraping Mercado Livre com Playwright
- ✅ `main.py` — Consolida resultados de ambos

**Padrão usado**: 
1. Lançar browser com `headless=False` para debug
2. Adicionar init script anti-detecção
3. Usar `wait_for_selector` antes de extrair dados
4. Looping por páginas com paginação
5. Salvar em JSON/CSV

---

Última atualização: junho 2026
