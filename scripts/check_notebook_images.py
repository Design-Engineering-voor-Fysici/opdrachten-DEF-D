import json
import re
import sys
from pathlib import Path

# Regexes to catch common image references
MARKDOWN_IMG_RE = re.compile(
    r'!\[.*?\]\(\s*([^\s")]+)'
)

PY_IMG_RE = re.compile(
    r'(?:Image\s*\(\s*filename\s*=\s*|imread\s*\(|open\s*\()\s*[\'"]([^\'"]+)[\'"]'
)

def extract_image_paths(nb_path: Path):
    with nb_path.open(encoding="utf-8") as f:
        nb = json.load(f)

    paths = set()

    for cell in nb.get("cells", []):
        source = "".join(cell.get("source", []))

        if cell.get("cell_type") == "markdown":
            paths.update(MARKDOWN_IMG_RE.findall(source))

        if cell.get("cell_type") == "code":
            paths.update(PY_IMG_RE.findall(source))

    return paths


def main():
    repo_root = Path(".").resolve()
    notebooks = list(repo_root.rglob("*.ipynb"))

    if not notebooks:
        print("No notebooks found.")
        return

    missing = []

    for nb in notebooks:
        img_paths = extract_image_paths(nb)
        for img in img_paths:
            img_path = (nb.parent / img).resolve()
            if not img_path.exists():
                missing.append((nb, img))

    if missing:
        print("Missing image files detected:\n")
        for nb, img in missing:
            print(f"- {nb}: {img}")
        sys.exit(1)

    print("All referenced notebook images exist.")


if __name__ == "__main__":
    main()
