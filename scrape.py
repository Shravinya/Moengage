import asyncio
import csv
import nest_asyncio
from playwright.async_api import async_playwright

nest_asyncio.apply()

BASE_URL = 'https://help.moengage.com'

async def scrape_article_links_and_content():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,  # Change to True to run headless
            args=[
                "--start-maximized",
                "--disable-blink-features=AutomationControlled"
            ]
        )
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36'
        )
        page = await context.new_page()
        await page.goto(f'{BASE_URL}/hc/en-us')
        await page.wait_for_load_state('networkidle')

        # Step 1: Get all article links
        links = await page.query_selector_all('a')
        article_urls = []
        for link in links:
            href = await link.get_attribute('href')
            if href and '/hc/en-us/articles/' in href:
                # Normalize relative URLs to absolute URLs
                if href.startswith('/'):
                    href = BASE_URL + href
                if href not in article_urls:
                    article_urls.append(href)

        print(f"Found {len(article_urls)} unique article URLs.")

        # Step 2: Visit each article and extract title + body text
        articles_data = []
        for i, url in enumerate(article_urls, start=1):
            print(f"[{i}/{len(article_urls)}] Fetching: {url}")
            try:
                await page.goto(url)
                await page.wait_for_load_state('networkidle')

                # Extract Title
                title_elem = await page.query_selector('h1.article-title, h1#article-title, h1')
                title = await title_elem.inner_text() if title_elem else "No Title Found"

                # Extract Body Text - main article content
                # MoEngage articles use div with class 'article-body' or 'article-content' commonly
                body_elem = await page.query_selector('div.article-body, div.article-content, article.article')
                body_text = await body_elem.inner_text() if body_elem else "No Content Found"

                articles_data.append({
                    "Title": title.strip(),
                    "URL": url,
                    "Body Text": body_text.strip()
                })
            except Exception as e:
                print(f"Failed to fetch or parse {url}: {e}")
                articles_data.append({
                    "Title": "Error fetching article",
                    "URL": url,
                    "Body Text": str(e)
                })

        await browser.close()

    return articles_data


if __name__ == "__main__":
    data = asyncio.get_event_loop().run_until_complete(scrape_article_links_and_content())

    # Save to CSV
    csv_file = 'moengage_articles_with_content.csv'
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['Title', 'URL', 'Body Text'])
        writer.writeheader()
        for article in data:
            writer.writerow(article)

    print(f"\nSaved {len(data)} articles with content to '{csv_file}'")
