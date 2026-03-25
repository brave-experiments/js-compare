from __future__ import annotations

from pathlib import Path
from shutil import rmtree
from subprocess import DEVNULL, run
from typing import TYPE_CHECKING

from js_compare.consts import WORKSPACE_PATH

if TYPE_CHECKING:
    from typing import Optional

TEMPLATES_DIR: Path = WORKSPACE_PATH / "templates"
JS_SCRIPT = Path("js_to_graphml.js")
SCRIPT_TEMPLATE: Path = TEMPLATES_DIR / JS_SCRIPT

def install_tool(tool_dir: Path) -> Path:
    if tool_dir.is_dir():
        msg = f"Unable to install tool at {tool_dir}. Directory exists."
        raise ValueError(msg)

    tool_dir.mkdir()
    run(["npm", "init", "-y"], cwd=tool_dir, stdout=DEVNULL, check=True)

    install_npm_packages_cmd = [
        "npm", "install", "-y",
        "@babel/parser@7", "@babel/traverse@7", "xmlbuilder2@4"
    ]
    run(install_npm_packages_cmd, cwd=tool_dir, stdout=DEVNULL, check=True)

    template_script_path = TEMPLATES_DIR / JS_SCRIPT
    return template_script_path.copy_into(tool_dir)

def uninstall_tool(tool_dir: Path) -> None:
    if not tool_dir.is_dir():
        msg = f"Unable to uninstall tool at {tool_dir}. No directory exists."
        raise ValueError(msg)
    rmtree(tool_dir)

def update_tool(tool_dir: Path) -> None:
    if not tool_dir.is_dir():
        msg = f"Unable to update tool at {tool_dir}. No directory exists."
        raise ValueError(msg)
    run(["npm", "update", "-y"], cwd=tool_dir, stdout=DEVNULL, check=True)

def check_tool(tool_dir: Path) -> bool:
    if not tool_dir.is_dir():
        return False
    script_path = tool_dir / JS_SCRIPT
    if not script_path.is_file():
        return False
    return True

def run_tool(tool_dir: Path, code: Path,
             output: Optional[Path]=None) -> Optional[str]:
    if not tool_dir.is_dir():
        msg = f"Unable to run tool at {tool_dir}. No directory exists."
        raise ValueError(msg)

    script_path = tool_dir / JS_SCRIPT
    if not script_path.is_file():
        msg = f"Unable to run script at {script_path}. No file exists."
        raise ValueError(msg)

    if not code.is_file():
        msg = f"Unable to parse JS code at {code}. No file exists."
        raise ValueError(msg)

    cmd: list[str | Path] = ["node", script_path, code]
    if output is None:
        capture_output = True
        stdout = None
    else:
        capture_output = False
        stdout = output.open("w")
    rs = run(cmd, cwd=tool_dir, capture_output=capture_output, stdout=stdout,
             encoding="utf8", check=True)
    if capture_output:
        return rs.stdout
    return None
