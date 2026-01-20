"""
dodo.py - Doit build automation for Corporate Bond Returns pipeline

Run with: doit
"""

import platform
import subprocess
import sys
from pathlib import Path

import chartbook

sys.path.insert(1, "./src/")

BASE_DIR = chartbook.env.get_project_root()
DATA_DIR = BASE_DIR / "_data"
OUTPUT_DIR = BASE_DIR / "_output"
OS_TYPE = "nix" if platform.system() != "Windows" else "windows"


def jupyter_execute_notebook(notebook):
    """Execute a notebook and save the output in-place."""
    subprocess.run(
        [
            "jupyter",
            "nbconvert",
            "--to",
            "notebook",
            "--execute",
            "--inplace",
            notebook,
        ],
        check=True,
    )


def jupyter_to_html(notebook, output_dir=OUTPUT_DIR):
    """Convert a notebook to HTML."""
    subprocess.run(
        [
            "jupyter",
            "nbconvert",
            "--to",
            "html",
            "--output-dir",
            str(output_dir),
            notebook,
        ],
        check=True,
    )


def task_config():
    """Create necessary directories."""
    return {
        "actions": [
            f"mkdir -p {DATA_DIR}" if OS_TYPE == "nix" else f"mkdir {DATA_DIR}",
            f"mkdir -p {OUTPUT_DIR}" if OS_TYPE == "nix" else f"mkdir {OUTPUT_DIR}",
        ],
        "targets": [DATA_DIR, OUTPUT_DIR],
        "uptodate": [True],
        "verbosity": 2,
    }


def task_pull_bond_data():
    """Pull corporate bond data from OpenBondAssetPricing.com."""
    return {
        "actions": ["python src/pull_open_source_bond.py"],
        "file_dep": ["src/pull_open_source_bond.py"],
        "targets": [
            DATA_DIR / "corporate_bond_returns.parquet",
            DATA_DIR / "treasury_bond_returns.parquet",
        ],
        "verbosity": 2,
    }


def task_calc_returns():
    """Calculate corporate bond portfolio returns."""
    return {
        "actions": ["python src/calc_corp_bond_returns.py"],
        "file_dep": [
            "src/calc_corp_bond_returns.py",
            "src/pull_open_source_bond.py",
            DATA_DIR / "corporate_bond_returns.parquet",
        ],
        "targets": [DATA_DIR / "corp_bond_portfolio_returns.parquet"],
        "verbosity": 2,
    }


def task_create_ftsfr_datasets():
    """Create standardized FTSFR datasets."""
    return {
        "actions": ["python src/create_ftsfr_datasets.py"],
        "file_dep": [
            "src/create_ftsfr_datasets.py",
            "src/calc_corp_bond_returns.py",
            "src/pull_open_source_bond.py",
            DATA_DIR / "corporate_bond_returns.parquet",
        ],
        "targets": [
            DATA_DIR / "ftsfr_corp_bond_returns.parquet",
            DATA_DIR / "ftsfr_corp_bond_portfolio_returns.parquet",
        ],
        "verbosity": 2,
    }


def task_run_notebooks():
    """Execute and convert summary notebooks."""
    notebooks = ["src/summary_corp_bond_returns_ipynb.py"]
    notebook_build_dir = OUTPUT_DIR / "_notebook_build"

    for notebook_py in notebooks:
        notebook_ipynb = notebook_py.replace("_ipynb.py", ".ipynb")
        notebook_name = Path(notebook_ipynb).stem
        notebook_build_path = notebook_build_dir / f"{notebook_name}.ipynb"

        yield {
            "name": notebook_name,
            "actions": [
                f"mkdir -p {notebook_build_dir}" if OS_TYPE == "nix" else f"mkdir {notebook_build_dir}",
                f"ipynb-py-convert {notebook_py} {notebook_ipynb}",
                lambda nb=notebook_ipynb: jupyter_execute_notebook(nb),
                lambda nb=notebook_ipynb: jupyter_to_html(nb),
                f"cp {notebook_ipynb} {notebook_build_path}",
            ],
            "file_dep": [
                notebook_py,
                DATA_DIR / "ftsfr_corp_bond_returns.parquet",
                DATA_DIR / "ftsfr_corp_bond_portfolio_returns.parquet",
            ],
            "targets": [
                notebook_ipynb,
                OUTPUT_DIR / f"{notebook_name}.html",
                notebook_build_path,
            ],
            "verbosity": 2,
        }


def task_generate_pipeline_site():
    """Generate the chartbook documentation site."""
    return {
        "actions": ["chartbook build -f"],
        "file_dep": [
            "chartbook.toml",
            OUTPUT_DIR / "_notebook_build" / "summary_corp_bond_returns.ipynb",
        ],
        "targets": [BASE_DIR / "docs" / "index.html"],
        "verbosity": 2,
    }
