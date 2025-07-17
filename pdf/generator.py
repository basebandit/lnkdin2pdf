from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from typing_extensions import Any
from weasyprint import HTML

from scraper.linkedin_scraper import LinkedInPost
from utils.logger import configure_logger

env = Environment(loader=FileSystemLoader(Path(__file__).parent.parent / "templates"))

logger = configure_logger()


def render_html(post: LinkedInPost) -> Any:
    template = env.get_template("post_template.html")
    return template.render(content=post.content, images=post.image_paths, url=post.url)


def generate_pdf(post: LinkedInPost, output_path: Path) -> None:
    html_str = render_html(post)
    HTML(string=html_str, base_url=".").write_pdf(output_path)
    logger.info(f"PDF saved to: {output_path}\033[0m")
