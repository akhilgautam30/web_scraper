import asyncio
from playwright.async_api import async_playwright
import csv

BASE_URL = "https://oda.com/no/products/"
OUTPUT_FILE = "oda_product_catalogue.csv"

async def handle_cookie_popup(page):
    try:
        accept_button = page.locator("button:has-text('Godkjenn kun nødvendige')")
        await accept_button.click(timeout=10000)
        await page.wait_for_load_state('networkidle')
        print("Cookie popup handled.")
    except Exception as e:
        print(f"Error handling cookie popup: {e}")

async def get_product_details(page):
    print("Getting product details...")
    try:
        await page.wait_for_selector('[data-testid="product-tile"]', timeout=60000)
        product_articles = page.locator('[data-testid="product-tile"]')
        count = await product_articles.count()
        print(f"Found {count} products")
        
        products = []
        for i in range(count):
            article = product_articles.nth(i)
            name = await article.locator('h2').inner_text()
            price = await article.locator('.k-text-style--label-m:visible').first.inner_text()
            unit_price_element = article.locator('[data-testid$="unit-price"]')
            unit_price = await unit_price_element.inner_text() if await unit_price_element.count() else "N/A"

            products.append({
                "name": name.strip(),
                "price": price.strip(),
                "unit_price": unit_price.strip()
            })

        # Check for next page
        next_button = page.locator('a[aria-label="Neste side"]:visible')
        if await next_button.count() > 0:
            await next_button.click()
            await page.wait_for_load_state('networkidle')
        else:
            return products
        
        return products
    except Exception as e:
        print(f"Error getting product details: {str(e)}")
        return []

async def scrape_products(page):
    await handle_cookie_popup(page)
    await page.wait_for_selector('//*[@id="main-content"]')
    products = await get_product_details(page)
    return products

async def scrape_categories(page):
    try:
        await page.wait_for_selector('//*[@id="main-content"]/div/div/div/section[4]/div', timeout=60000)
        category_links = page.locator('//*[@id="main-content"]/div/div/div/section[4]/div//a[contains(@href, "/categories/")]')
        count = await category_links.count()
        print(f"Found {count} categories")
        
        categories = []
        for i in range(count):
            link = category_links.nth(i)
            name = await link.inner_text()
            url = await link.get_attribute("href")
            categories.append({"name": name, "url": url})
        
        return categories
    except Exception as e:
        print(f"Error scraping categories: {str(e)}")
        return []

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto(BASE_URL)
        await page.wait_for_load_state('domcontentloaded')

        categories = await scrape_categories(page)
        print(f"Found {len(categories)} categories")

        all_products = []
        for category in categories:
            print(f"Processing category: {category['name']}")
            await page.goto(category['url'], timeout=60000)
            await page.wait_for_load_state('networkidle')
            products = await get_product_details(page)
            print(f"Found {len(products)} products in {category['name']}")
            for product in products:
                product["category"] = category["name"]
            all_products.extend(products)

        with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['category', 'name', 'price', 'unit_price']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for product in all_products:
                writer.writerow(product)

        print(f"Data saved to {OUTPUT_FILE}")
        await browser.close()

asyncio.run(main())
