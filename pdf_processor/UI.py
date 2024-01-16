import time

from rich import print
from rich.layout import Layout
from rich.panel import Panel
from rich.live import Live
from rich.table import Table
from rich.style import Style
from rich.prompt import Prompt

from rich.console import Console

console = Console()

fileTable = Table(title="Files")
fileTable.add_column("")
fileTable.add_column("Name")

selectionStyle = Style(color="magenta", bgcolor="yellow", italic=True)

fileTable.add_row("1", "whatever.pdf", style=selectionStyle)
fileTable.add_row("2", "whatever.pdf")
fileTable.add_row("3", "whatever.pdf")
fileTable.add_row("4", "whatever.pdf")

functionmap = {
    "1": ["merge"],
    "2": ["OCR(language=eng,pages=all"],
    "3": ["Change Pages(style=arabic;startpage"],
    "4": ["Bookmark"],
    "ex": ["Extract pages and bookmarks"],
    "exwb": ["Extract pages without bookmarks (way faster"],
    "spl": ["Split PDF to PNG"],
    "clr": ["Remove all page labels"],
    "editmeta": ["Manually edit metadata"],
    "o": ["Open current file"],
    "rn": ["Rename Output"],
}

stepsTable = Table(title="Steps")
stepsTable.add_column("")
stepsTable.add_column("Name")
stepsTable.add_column("")

for key, item in functionmap.items():
    stepsTable.add_row(key, item[0])




print(stepsTable)

Prompt.ask("What to do?")

