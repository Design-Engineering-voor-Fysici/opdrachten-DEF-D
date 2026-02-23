import json
import sys
from pathlib import Path

def check_notebook(path: Path) -> list[str]:
    errors = []

    with path.open(encoding="utf-8") as f:
        nb = json.load(f)

    expected = 1

    for idx, cell in enumerate(nb.get("cells", [])):
        if cell.get("cell_type") != "code":
            continue

        exec_count = cell.get("execution_count")

        if exec_count is None:
            errors.append(
                f"{path}: code cell {idx} is unexecuted; expected execution_count={expected}"
            )
            continue

        if exec_count != expected:
            errors.append(
                f"{path}: code cell {idx} has execution_count={exec_count}, "
                f"expected {expected}"
            )

        expected += 1

    return errors


def main() -> int:
    notebooks = list(Path(".").rglob("*.ipynb"))
    all_errors = []

    for nb in notebooks:
        all_errors.extend(check_notebook(nb))

    if all_errors:
        print("Notebook execution order check failed:\n")
        for err in all_errors:
            print(err)
        return 1

    print("All notebooks have used 'restart & run all'.")
    return 0


if __name__ == "__main__":
    sys.exit(main())