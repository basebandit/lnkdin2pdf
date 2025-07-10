import argparse
from pathlib import Path
from utils.validators import is_valid_linkedin_url, clean_linkedin_url
from scraper.linkedin_scraper import extract_post_content
from pdf.generator import generate_pdf


def read_input(input_path: Path) -> tuple[list[str], list[str]]:
    urls = []
    if input_path.suffix == ".txt":
        with input_path.open("r") as f:
            urls = [line.strip() for line in f if line.strip()]
    elif input_path.suffix == ".csv":
        with input_path.open("r") as f:
            urls = [line.strip().split(",")[0] for line in f if line.strip()]
    else:
        raise ValueError("Unsupported file format. Use .txt or .csv")

    valid_urls = [url for url in urls if is_valid_linkedin_url(url)]
    invalid_urls = [url for url in urls if not is_valid_linkedin_url(url)]
    return valid_urls, invalid_urls


def process_url(url: str, debug: bool = False) -> None:
    clean_url = clean_linkedin_url(url)
    print(f"🔗 Processing: {clean_url}")
    try:
        post = extract_post_content(clean_url, debug=debug)
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        filename = f"linkedin_post_{abs(hash(post.content)) % 999999}.pdf"
        generate_pdf(post, output_dir / filename)
    except Exception as e:
        print(f"❌ Failed to process post: {e}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert LinkedIn post(s) to PDF.")
    parser.add_argument("--url", help="Single LinkedIn post URL")
    parser.add_argument(
        "--file",
        type=Path,
        help="Path to .txt or .csv file containing LinkedIn post URLs",
    )
    parser.add_argument(
        "-d", "--debug", action="store_true", help="Enable debug mode (show browser)"
    )

    args = parser.parse_args()
    if args.url:
        if is_valid_linkedin_url(args.url):
            process_url(args.url, debug=args.debug)
        else:
            print("❌ Invalid LinkedIn post URL.")
    elif args.file:
        try:
            valid_urls, invalid_urls = read_input(args.file)
            print(f"✅ Found {len(valid_urls)} valid LinkedIn URLs.")
            if invalid_urls:
                print(f"⚠️ Skipped {len(invalid_urls)} invalid URLs.")
            for url in valid_urls:
                process_url(url, debug=args.debug)
        except Exception as e:
            print(f"❌ Error reading input file: {e}")
    else:
        print("ℹ️ Please provide either --url or --file")


if __name__ == "__main__":
    main()
