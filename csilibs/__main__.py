# Help file
from rich.console import Console
from rich.markdown import Markdown
import os

_abs_path = os.path.abspath(os.path.dirname(__file__))  

console = Console()
with open(os.path.join(_abs_path,"../README.md")) as readme:
    markdown = Markdown(readme.read())
console.print(markdown)
