"""A script to generate Notebooks for documentation."""
import argparse
import fnmatch
import os
import typing as t
from pathlib import Path

import requests
from jupytext import cli as jupytext_cli

BASE_EXAMPLE_URL = "https://docs.zhinst.com/zhinst-toolkit/en/latest/examples"
EXAMPLES_DIR = Path(__file__).parent.parent / "examples"
EXAMPLES_ONLY_SYNC = ["nodetree.md"]
EXCLUDED_FILES = ["README.md"]


def download_example_file(filename: str) -> bytes:
    """Download example file.

    Arguments:
        filename: notebook filename.
    Returns:
        Notebook contents
    """
    url = f"{BASE_EXAMPLE_URL}/{filename}"
    response = requests.get(url)
    response.raise_for_status()
    return response.content


def get_notebook_examples() -> None:
    """Get notebook examples."""
    for example_file in fnmatch.filter(os.listdir(EXAMPLES_DIR), "*.md"):
        if example_file in EXAMPLES_ONLY_SYNC or example_file in EXCLUDED_FILES:
            continue
        example_file = example_file.replace(".md", ".ipynb")
        contents = download_example_file(example_file)
        if contents:
            with open(f"{EXAMPLES_DIR / example_file}", "wb") as f:
                f.write(contents)


def generate_and_sync_example_notebooks(src: t.List[Path]) -> None:
    """Generate and sync given source files to notebooks.

    Arguments:
        src: Source files
    """
    str_path = [str(path) for path in src]
    jupytext_cli.jupytext(["--sync", *str_path])


def generate_notebooks(args: argparse.Namespace) -> None:
    """Generate notebooks either from local or remote.

    Arguments:
        args: Namespace arguments
    """
    if args.src == "local":
        generate_and_sync_example_notebooks([EXAMPLES_DIR / "*.md"])
    else:
        get_notebook_examples()
        generate_and_sync_example_notebooks(
            [EXAMPLES_DIR / file for file in EXAMPLES_ONLY_SYNC]
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Notebooks.")
    parser.add_argument("src", help="Source of Notebooks", choices=["local", "remote"])
    generate_notebooks(parser.parse_args())
