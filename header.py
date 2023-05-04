from rich.console import Console
from rich.panel import Panel
from rich import box
from rich.align import Align
from rich.text import Text

import styles


multiline_text = '''    ▄═^'`' ¬.                                     █▌
 ,█▀         '                           ____     █▌___      ____
 █▌            ▐█       █▌  █▌ ⌐^"``   ─`    "▄   █▌      ,▄"    "▄.   █▌ ⌐^"``
▐█             ▐█       █▌  █▌'              ,▐█  █▌     ▐█        █▄  █▌'
 ██            ▐█       █▌  █▌        ,▄═^^"` ▐█  █▌     ██        ██  █▌
  ▀█         , ▐█       █▌  █▌       ▐█       ▐█  █▌      █▄      ▄█   █▌
   `▀═..,. ═`   ▀▀w___='█▌  █▌        ▀∞____='▀█| ▀▌∞__    ▀∞____∞▀    █▌'''

def header():
   console = Console()
   panel = Align.center(
      Panel(Panel(multiline_text, box=box.SQUARE, padding=(1, 3), expand=False, style="bright_cyan on bright_white", 
      border_style="bright_white"), expand=False, style="on yellow", border_style="yellow",  box=box.SQUARE
      ))
   console.print(panel)

   welcome_text = Text(
      "\nWelcome to Curator, a program designed to help you create the perfect collection of your favorite arcade games! "
      "Using this program is designed to be simple, just follow the instructions in each of the prompts. If you would like more "
      "information on a prompt or how it impacts your collection type \"info\".\n", style=styles.prompt)
   console.print(welcome_text)
   continue_text = Text("Press Enter to continue...", style=styles.prompt)
   console.input(continue_text)
   print("\n\n")

