import os
import subprocess
from rich.console import Console
import styles

def extract_mame_xml(mame_exe):
    output_file = 'mame.xml'

    console = Console()

    if not os.path.exists(mame_exe):
        console.print(f"Couldn't find {mame_exe}. Make sure the path is correct.", style=styles.error)
        console.print("Press Enter to terminate...", style=styles.prompt)
        input()
        os._exit(1)

    try:
        # Start a subprocess with a pipe to capture stdout
        with console.status(f"[{styles.processing}]Extracting database file from mame.exe...", spinner="bouncingBall", spinner_style=styles.processing) as status:
            output_data = subprocess.check_output([mame_exe, '-listxml'])

        # Write the output to the output file
        with open(output_file, 'wb') as f:
            f.write(output_data)

        console.print("Successfully extracted MAME database.", style=styles.done_processing)
    
    except subprocess.CalledProcessError as e:
        console.print(f"Failed to extract MAME data: {e}", style=styles.error)