import subprocess
from pathlib import Path
import uuid


def convert_with_pandoc_to_markdown(filepath: str, input_format: str) -> str:
    """Use Pandoc to convert a file to Markdown via a temporary file near the original."""
    input_path = Path(filepath)

    if not input_path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    try:
        tmp_filename = f".tmp_{uuid.uuid4().hex}.md"
        output_path = input_path.parent / tmp_filename

        result = subprocess.run(
            ["pandoc", str(filepath), "-f", input_format, "-t", "markdown", "-o", str(output_path)],
            capture_output=True,
            text=True,
            check=True,
        )

        markdown = output_path.read_text(encoding="utf-8")
        output_path.unlink(missing_ok=True)  # cleanup

        return markdown.strip()

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Pandoc conversion failed: {e.stderr}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error in pandoc markdown conversion: {e}")
