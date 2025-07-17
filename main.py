import argparse
import asyncio
from pathlib import Path

from pdf.generator import generate_pdf
from scraper.linkedin_scraper import extract_post_content
from utils.logger import configure_logger
from utils.validators import clean_linkedin_url, is_valid_linkedin_url

logger = configure_logger()


def read_input(input_path: Path) -> list[str]:
    if input_path.suffix == ".txt":
        with input_path.open("r") as f:
            return [line.strip() for line in f if line.strip()]
    elif input_path.suffix == ".csv":
        with input_path.open("r") as f:
            return [line.strip().split(",")[0] for line in f if line.strip()]
    else:
        raise ValueError("Unsupported file format. Use .txt or .csv")


async def process_url(url: str, debug: bool = False) -> None:
    try:
        logger.info(f"Processing: {url}")
        post = await extract_post_content(clean_linkedin_url(url), debug=debug)
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        filename = f"linkedin_post_{abs(hash(post.content)) % 999999}.pdf"
        generate_pdf(post, output_dir / filename)
    except Exception as e:
        logger.error(f"Failed to process {url}: {e}")


async def main() -> None:
    parser = argparse.ArgumentParser(description="Convert LinkedIn post(s) to PDF.")
    parser.add_argument("--url", help="Single LinkedIn post URL")
    parser.add_argument(
        "--file", type=Path, help="Path to .txt or .csv file with LinkedIn post URLs"
    )
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")

    args = parser.parse_args()

    if args.url:
        if is_valid_linkedin_url(args.url):
            await process_url(args.url, debug=args.debug)
        else:
            logger.error("Invalid LinkedIn URL.", "error")
    elif args.file:
        urls = read_input(args.file)
        valid_urls = [u for u in urls if is_valid_linkedin_url(u)]
        logger.info(f"Found {len(valid_urls)} valid LinkedIn URLs.", "success")
        await asyncio.gather(
            *(process_url(u, args.debug) for u in valid_urls),
            return_exceptions=True,  # Ensures one failure doesn't cancel all
        )
    else:
        logger.info("Please provide either --url or --file")


if __name__ == "__main__":
    asyncio.run(main())
