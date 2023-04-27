"""
CONSOLE LOADER
"""
from src.constants import con

if con.headless:
    from src.utils.strings import Console
else:
    from src.gui.console import Console
console = Console()
