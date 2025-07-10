from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from pathlib import Path
from typing_extensions import Any
from scraper.linkedin_scraper import LinkedInPost

env = Environment(loader=FileSystemLoader(Path(__file__).parent.parent / "templates"))


def render_html(post: LinkedInPost) -> Any:
    template = env.get_template("post_template.html")
    return template.render(content=post.content, images=post.image_paths, url=post.url)


def generate_pdf(post: LinkedInPost, output_path: Path) -> None:
    html_str = render_html(post)
    HTML(string=html_str, base_url=".").write_pdf(output_path)
    print(f"📄 PDF saved to: {output_path}")
