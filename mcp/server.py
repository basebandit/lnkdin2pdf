from pathlib import Path
from typing import Any, Dict, List, Optional

from PyPDF2 import PdfReader
from pydantic import AnyUrl

from mcp.server.fastmcp import FastMCP
from mcp.types import Resource
from pdf.generator import generate_pdf
from scraper.linkedin_scraper import extract_post_content
from utils.logger import configure_logger
from utils.validators import clean_linkedin_url, is_valid_linkedin_url

logger = configure_logger()
default_output_dir = Path.home() / "Downloads"

mcp = FastMCP("lnkdin2pdf", dependencies=["PyPDF2[all]"])


@mcp.tool(description="Generate a formatted PDF from a LinkedIn post URL.")
async def generate_pdf_from_url(
    url: str, output_dir: Optional[str] = None
) -> Dict[str, Any]:
    if not is_valid_linkedin_url(url):
        raise ValueError("Invalid LinkedIn post URL.")

    output_path = Path(output_dir or default_output_dir).expanduser()
    output_path.mkdir(parents=True, exist_ok=True)

    post = await extract_post_content(clean_linkedin_url(url))
    filename = f"linkedin_post_{abs(hash(post.content)) % 999999}.pdf"
    pdf_file = output_path / filename
    generate_pdf(post, pdf_file)

    return {
        "message": f"PDF saved at: {pdf_file}",
        "preview": Resource(
            uri=AnyUrl(f"file://{pdf_file}"),
            name=pdf_file.name,
            mimeType="application/pdf",
        ),
    }


@mcp.tool(description="Read and extract text from a PDF file.")
async def read_pdf(file_path: str) -> str:
    path = Path(file_path).expanduser()
    if not path.exists() or not path.is_file() or path.suffix.lower() != ".pdf":
        raise ValueError("Invalid PDF file path.")

    try:
        from io import BytesIO

        reader = PdfReader(BytesIO(path.read_bytes()))
        return "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    except Exception as e:
        raise RuntimeError(f"Failed to read PDF content: {e}") from e


@mcp.tool(
    description="Generate PDFs for each LinkedIn post URL in a .txt or .csv file."
)
async def generate_pdfs_from_file(
    file_path: str, output_dir: Optional[str] = None
) -> Dict[str, Any]:
    path = Path(file_path).expanduser()
    if not path.exists() or not path.is_file():
        raise ValueError("Invalid file path.")
    if path.suffix not in (".txt", ".csv"):
        raise ValueError("Only .txt and .csv files are supported.")

    lines = path.read_text().strip().splitlines()

    if path.suffix == ".csv":
        urls = [line.split(",")[0].strip() for line in lines if line.strip()]
    else:
        urls = [line.strip() for line in lines if line.strip()]

    output_path = Path(output_dir or default_output_dir).expanduser()
    output_path.mkdir(parents=True, exist_ok=True)

    results: Dict[str, Any] = {}
    for url in urls:
        try:
            if not is_valid_linkedin_url(url):
                raise ValueError("Invalid LinkedIn URL.")

            post = await extract_post_content(clean_linkedin_url(url))
            filename = f"linkedin_post_{abs(hash(post.content)) % 999999}.pdf"
            pdf_file = output_path / filename
            generate_pdf(post, pdf_file)

            results[url] = {
                "message": "PDF generated",
                "preview": Resource(
                    uri=AnyUrl(f"file://{pdf_file}"),
                    name=pdf_file.name,
                    mimeType="application/pdf",
                ),
            }

        except Exception as e:
            results[url] = {"message": f"Failed: {e}"}

    return results


@mcp.resource("file://posts")
def list_post_pdfs() -> List[Resource]:
    """
    Lists all LinkedIn post PDFs as MCP resources.
    """
    pdfs = sorted(default_output_dir.glob("linkedin_post_*.pdf"))
    return [
        Resource(
            uri=AnyUrl(f"file://{f}"),
            name=f.name,
            mimeType="application/pdf",
        )
        for f in pdfs
        if f.is_file()
    ]


@mcp.resource("file://posts/{name}")
def get_post_pdf(name: str) -> Resource:
    """
    Returns a specific LinkedIn post PDF as an MCP Resource.
    """
    path = (default_output_dir / name).expanduser()
    if not path.exists() or not path.is_file() or path.suffix.lower() != ".pdf":
        raise FileNotFoundError(f"No PDF found with name: {name}")

    return Resource(
        uri=AnyUrl(f"file://{path}"),
        name=path.name,
        mimeType="application/pdf",
    )
