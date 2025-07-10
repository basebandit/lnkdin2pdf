from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from dataclasses import dataclass
from urllib.parse import urlparse, urlunparse
import time
import requests
from pathlib import Path
import mimetypes


@dataclass
class LinkedInPost:
    url: str
    content: str
    image_paths: list[str]


def strip_url_query(url: str) -> str:
    parsed = urlparse(url)
    return urlunparse(parsed._replace(query="", fragment=""))


def download_image(url: str, dest_dir: Path) -> str:
    response = requests.get(url, stream=True, timeout=10)
    if response.status_code != 200:
        raise ValueError(f"Failed to download image: {url}")

    mime = response.headers.get("Content-Type", "")
    if "pdf" in mime.lower():
        raise ValueError("PDFs are not supported as post images.")

    ext = mimetypes.guess_extension(mime.split(";")[0]) or ".jpg"
    filename = f"img_{hash(url)}{ext}"
    out_path = dest_dir / filename

    with open(out_path, "wb") as f:
        for chunk in response.iter_content(1024):
            f.write(chunk)

    return str(out_path)


def extract_post_content(url: str, debug: bool = False) -> LinkedInPost:
    clean_url = strip_url_query(url)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not debug, slow_mo=100 if debug else 0)
        context = browser.new_context()
        page = context.new_page()

        print(f"🔍 Visiting {clean_url}")
        page.goto(clean_url, timeout=60000)
        time.sleep(3)

        # Dismiss login modal
        modal_closed = False
        dismiss_selectors = [
            "button.contextual-sign-in-modal__modal-dismiss",
            "button.sign-in-modal__dismiss",
        ]

        for selector in dismiss_selectors:
            try:
                button = page.locator(selector)
                if button.is_visible():
                    print(f"🚪 Dismissing login modal ({selector})...")
                    button.click()
                    page.wait_for_timeout(2000)
                    modal_closed = True
                    break
            except PlaywrightTimeoutError:
                continue

        if not modal_closed:
            print("⚠️ Modal not dismissed on first attempt. Retrying...")
            time.sleep(2)
            for selector in dismiss_selectors:
                try:
                    button = page.locator(selector)
                    if button.is_visible():
                        print(f"🚪 Retrying modal dismiss ({selector})...")
                        button.click()
                        page.wait_for_timeout(2000)
                        break
                except PlaywrightTimeoutError:
                    continue

        content = None
        image_paths = []
        dest_dir = Path("output/assets")
        dest_dir.mkdir(parents=True, exist_ok=True)

        # Extract post text
        selectors = [
            "div.update-components-text__text-view",
            "div.feed-shared-update-v2__description",
            "p.attributed-text-segment-list__content",
            "span[dir='ltr']",
        ]

        for selector in selectors:
            try:
                page.wait_for_selector(selector, timeout=5000)
                locator = page.locator(selector).first
                content = locator.inner_text().strip()
                if content:
                    break
            except PlaywrightTimeoutError:
                continue

        if not content:
            debug_html = "output/debug_failed_post.html"
            Path(debug_html).write_text(page.content(), encoding="utf-8")
            page.screenshot(path="output/debug_failed_post.png", full_page=True)
            raise RuntimeError("❌ Could not find post content with known selectors")

        # Extract images from ul[data-test-id="feed-images-content"]
        try:
            img_locator = page.locator('ul[data-test-id="feed-images-content"] img')
            count = img_locator.count()

            for i in range(count):
                img = img_locator.nth(i)
                img.scroll_into_view_if_needed()
                page.wait_for_timeout(300)

                # Prefer data-delayed-url over src
                delayed_url = img.get_attribute("data-delayed-url")
                fallback_url = img.get_attribute("src")
                final_url = delayed_url or fallback_url

                if final_url and final_url.startswith("http"):
                    try:
                        downloaded_path = download_image(final_url, dest_dir)
                        image_paths.append(downloaded_path)
                    except Exception as e:
                        print(f"⚠️ Failed to download image {final_url}: {e}")

        except Exception as e:
            print(f"⚠️ No images found: {e}")

        browser.close()

        return LinkedInPost(url=clean_url, content=content, image_paths=image_paths)
