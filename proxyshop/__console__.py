from proxyshop.constants import con

if not con.headless:
    from proxyshop.gui.console import Console
else:
    from proxyshop.core import Console

console = Console()
