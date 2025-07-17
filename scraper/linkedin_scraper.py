import asyncio
import aiohttp
import mimetypes
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse, urlunparse
from playwright.async_api import (
    TimeoutError as PlaywrightTimeoutError,
)
from playwright.async_api import (
    async_playwright,
)
from utils.logger import configure_logger

logger = configure_logger()


@dataclass
class LinkedInPost:
    url: str
    content: str
    image_paths: list[str]


def strip_url_query(url: str) -> str:
    parsed = urlparse(url)
    return urlunparse(parsed._replace(query="", fragment=""))


async def download_image(
    session: aiohttp.ClientSession, url: str, dest_dir: Path
) -> str:
    async with session.get(url, timeout=10) as response:
        if response.status != 200:
            raise ValueError(f"Failed to download image: {url}")

        mime = response.headers.get("Content-Type", "")
        if "pdf" in mime.lower():
            raise ValueError("PDFs are not supported as post images.")

        ext = mimetypes.guess_extension(mime.split(";")[0]) or ".jpg"
        filename = f"img_{hash(url)}{ext}"
        out_path = dest_dir / filename

        with open(out_path, "wb") as f:
            async for chunk in response.content.iter_chunked(1024):
                f.write(chunk)

    return str(out_path)


async def extract_post_content(url: str, debug: bool = False) -> LinkedInPost:
    clean_url = strip_url_query(url)
    dest_dir = Path("output/assets")
    dest_dir.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=not debug, slow_mo=100 if debug else 0
        )
        context = await browser.new_context()
        page = await context.new_page()

        logger.info(f"Visiting {clean_url}")
        await page.goto(clean_url, timeout=60000)
        await asyncio.sleep(3)

        # Try dismissing login modal
        dismiss_selectors = [
            "button.contextual-sign-in-modal__modal-dismiss",
            "button.sign-in-modal__dismiss",
        ]
        for selector in dismiss_selectors:
            try:
                button = page.locator(selector)
                if await button.is_visible():
                    logger.info(f"Dismissing login modal ({selector})...")
                    await button.click()
                    await page.wait_for_timeout(2000)
                    break
            except PlaywrightTimeoutError:
                continue

        # Check for no-content card (private/unavailable)
        try:
            if await page.locator("div.no-content-card").is_visible():
                raise RuntimeError(
                    "Post is unavailable or private. You may need to log in."
                )
        except PlaywrightTimeoutError:
            pass

        # Try known selectors to extract text
        content = None
        selectors = [
            "div.update-components-text__text-view",
            "div.feed-shared-update-v2__description",
            "p.attributed-text-segment-list__content",
            "span[dir='ltr']",
        ]
        for selector in selectors:
            try:
                await page.wait_for_selector(selector, timeout=5000)
                locator = page.locator(selector).first
                content = await locator.inner_text()
                if content.strip():
                    content = content.strip()
                    break
            except PlaywrightTimeoutError:
                continue

        if not content:
            Path("output/debug_failed_post.html").write_text(await page.content())
            await page.screenshot(path="output/debug_failed_post.png", full_page=True)
            raise RuntimeError("Could not find post content with known selectors.")

        # Extract images
        image_paths = []
        try:
            img_locator = page.locator('ul[data-test-id="feed-images-content"] img')
            count = await img_locator.count()

            async with aiohttp.ClientSession() as session:
                for i in range(count):
                    img = img_locator.nth(i)
                    await img.scroll_into_view_if_needed()
                    await page.wait_for_timeout(300)

                    delayed_url = await img.get_attribute("data-delayed-url")
                    fallback_url = await img.get_attribute("src")
                    final_url = delayed_url or fallback_url

                    if final_url and final_url.startswith("http"):
                        try:
                            path = await download_image(session, final_url, dest_dir)
                            image_paths.append(path)
                        except Exception as e:
                            logger.error(f"Failed to download image {final_url}: {e}")
        except Exception as e:
            logger.warning(f"No images found or failed to extract images: {e}")

        await browser.close()

        return LinkedInPost(url=clean_url, content=content, image_paths=image_paths)
