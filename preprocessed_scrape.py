import csv
import asyncio
import nest_asyncio
from playwright.async_api import async_playwright

nest_asyncio.apply()

input_file = 'moengage_articles_with_content.csv'
output_file = 'filtered_article_links_content.csv'

allowed_prefixes = [
    'https://help.moengage.com/hc/en-us/articles/',
    'https://developers.moengage.com/hc/en-us/articles/',
    'https://partners.moengage.com/hc/en-us/articles/'
]

# Read and filter URLs from input CSV
filtered_links = []
with open(input_file, mode='r', encoding='utf-8') as infile:
    reader = csv.DictReader(infile)
    for row in reader:
        url = row.get('Article URL') or row.get('URL')
        if url and any(url.startswith(prefix) for prefix in allowed_prefixes):
            filtered_links.append(url)

print(f"✅ Found {len(filtered_links)} article links to scrape.")

# Define scraping logic
async def scrape_articles_to_csv(urls, output_file):
    results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36'
        )
        page = await context.new_page()

        for url in urls:
            try:
                print(f"🔍 Scraping: {url}")
                await page.goto(url)
                await page.wait_for_load_state('networkidle')

                # Extract title and body
                title_el = await page.query_selector('h1.article-title, h6.article-title')
                title = await title_el.inner_text() if title_el else '[No Title Found]'

                body_el = await page.query_selector('div.article__body')
                body_text = await body_el.inner_text() if body_el else '[No Body Found]'

                results.append({
                    'Title': title.strip(),
                    'URL': url,
                    'Body Text': body_text.strip()
                })
            except Exception as e:
                print(f"⚠️ Error scraping {url}: {e}")
                results.append({
                    'Title': '[Error]',
                    'URL': url,
                    'Body Text': str(e)
                })

        await browser.close()

    # Write to output CSV
    with open(output_file, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['Title', 'URL', 'Body Text'])
        writer.writeheader()
        for row in results:
            writer.writerow(row)

    print(f"\n✅ Done! Scraped {len(results)} articles saved to '{output_file}'.")

# Run the main async function
asyncio.get_event_loop().run_until_complete(scrape_articles_to_csv(filtered_links, output_file))
