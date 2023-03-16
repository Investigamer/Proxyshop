from src.constants import con

if not con.headless:
    from src.gui.console import Console
else:
    from src.core import Console

console = Console()
