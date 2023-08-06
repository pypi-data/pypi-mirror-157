"""some basic configurations
"""
from pathlib import Path
import os
import os.path as osp

_BASE_DIR = Path.home() / ".shells" # Basic Path
_CONFIG_DIR = _BASE_DIR / "configs"  # Default Config Path

_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

BFF_ROOT_PATH = Path(osp.abspath(osp.dirname(__file__)))
BFF_OTHER_PATH = BFF_ROOT_PATH / "other"
BFF_TEMPLATE_PATH = BFF_ROOT_PATH / "template"

#Dictionary with console color codes to print text
terminal_colors = {
    'HEADER' : "\033[95m",
    'OKBLUE' : "\033[94m",
    'RED' : "\033[91m",
    'OKYELLOW' : "\033[93m",
    'GREEN' : "\033[92m",
    'LIGHTBLUE' : "\033[96m",
    'WARNING' : "\033[93m",
    'FAIL' : "\033[91m",
    'ENDC' : "\033[0m",
    'BOLD' : "\033[1m",
    'UNDERLINE' : "\033[4m" 
}