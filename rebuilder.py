import subprocess
import os
import shutil
import sys
from rich import print
from rich.text import Text
from rich.console import Console
from rich.emoji import Emoji

import styles

def rebuild(mame_tree, mame_root, rebuilder_exe, roms_folder, chds_folder, samples_folder):

    """
    Step 1. Create collection folder and determine compression settings
    """

    console = Console()

    #Create a folder for collection
    folder_path_text = f"[{styles.prompt}]Enter the full path of the output folder for your collection.[/{styles.prompt}]\n[not bold white](A subfolder 'roms', and 'samples' if provided, will be created under this folder):[/not bold white]"

    while True:
        output_folder = console.input(folder_path_text)
        try:
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            console.print("Ok\n", style=styles.success)
            break
        except OSError as e:
            console.print(f"Error creating folder '{output_folder}': {e}\n", style=styles.error)

    #Ask user for their preferred compression level
    compression_choice_text = f"[{styles.prompt}]Select a compression format:[/{styles.prompt}]\n[not bold white]1. zip - has universal compatibility with all frontends\n2. 7z - results in 30-70% smaller file sizes\n(1/2):[/not bold white]"

    while True:
        compression_choice = console.input(compression_choice_text)
        if compression_choice == "1":
            compression = "zip"
            console.print("Ok\n", style=styles.success)
            break
        if compression_choice == "2":
            compression = "7z"
            console.print("Ok\n", style=styles.success)
            break
        else:
            console.print("Please select one of the available options.\n", style=styles.error) 

    #Ask user for their preferred merge mode
    compression_choice_text = f"[{styles.prompt}]Select a merge mode (How MAME file are stored):[/{styles.prompt}]\n[not bold white]1. Standalone - Highly recommended if you filtered the parent/clones based on language and # of players, other modes will result in unusable files.\n2. Full - Only recommended if you kept or removed all clones. One file for each parent set. Clones are kept inside the parent archive. Results in a smaller total file size.\n3. Split - Only recommended if you kept all clones. One file for each parent and every clone.\n(1/2/3):[/not bold white]"

    while True:
        compression_choice = console.input(compression_choice_text)
        if compression_choice == "1":
            mode = "standalone"
            console.print("Ok\n", style=styles.success)
            break
        if compression_choice == "2":
            mode = "full"
            console.print("Ok\n", style=styles.success)
            break
        if compression_choice == "3":
            mode = "split"
            console.print("Ok\n", style=styles.success)
            break
        else:
            console.print("Please select one of the available options.\n", style=styles.error) 

    xml_file = "mame.xml"

    """
    Step 2. Create rebuilder filter argument and chunk
    """

    # Extract machine names and join them with '|'
    machine_names = []
    for machine in mame_root.findall('machine'):
        name = machine.get('name')
        machine_names.append(name)

    mame_files = '|'.join(machine_names)

    # Chunk the mame file names into sizes that don't exceed the cmd input character limit
    def split_mame_files(mame_files, chunk_size):
        machine_names = mame_files.split("|")
        chunks = [machine_names[i:i+chunk_size] for i in range(0, len(machine_names), chunk_size)]
        return ["|".join(chunk) for chunk in chunks]

    chunk_size = 2500
    mame_files_chunks = split_mame_files(mame_files, chunk_size)

    if chds_folder == "none":
        total_batches = len(mame_files_chunks)
    else:
        total_batches = len(mame_files_chunks) * 2

    # Process roms folder with Rebuilder
    if total_batches > 1:
        console.print(Text("Due to program limitations your collection will be processed in batches. Also note that you will see some "
                            "sample specific warnings. Rebilder corrects for this internally and will not affect its output.", style=styles.info))
    else:
         console.print(Text("You will see some sample specific warnings. Rebilder corrects for this internally and will not affect its output.", style=styles.info))

    console.input(Text("Press Enter to continue...", style=styles.prompt))

    for batch_num, mame_files_chunk in enumerate(mame_files_chunks, start=1):
            # Print a message before running the rebuilder subprocess
        print(Text(f"Processing batch {batch_num} of {total_batches}", style=styles.info))

        args = [
            rebuilder_exe,
            "-x", xml_file,
            "-i", roms_folder,
            "-o", output_folder,
            "-c", compression,
            "-m", mode,
            "-p", "roms",
            "-f", mame_files_chunk
        ]

        returncode = subprocess.call(args)

        if returncode == 0:
            console.print(Text(f"Rebuilder completed batch {batch_num} of {total_batches} successfully.", style=styles.success))
        else:
            console.print("Rebuilder encountered an error.", style=styles.error)

    # Process chds folder with Rebuilder
    if chds_folder != "none":
        current_batch = batch_num
        for batch_num, mame_files_chunk in enumerate(mame_files_chunks, start=1):
                # Print a message before running the rebuilder subprocess
            console.print(Text(f"Processing batch {batch_num + current_batch} of {total_batches}", style=styles.info))

            args = [
                rebuilder_exe,
                "-x", xml_file,
                "-i", chds_folder,
                "-o", output_folder,
                "-c", compression,
                "-m", mode,
                "-p", "roms",
                "-f", mame_files_chunk
            ]

            returncode = subprocess.call(args)

            if returncode == 0:
                console.print(Text(f"Rebuilder completed batch {batch_num + current_batch} of {total_batches} successfully.", style=styles.success))
            else:
                console.print("Rebuilder encountered an error.", style=styles.error)


    """
    Step 3. Create and populate samples folder
    """

    if samples_folder != "none":
        destination_folder = os.path.join(output_folder, "samples")

        # Create the destination folder if it doesn't exist
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)

        # Extract the 'sampleof' attribute values and store them in a set
        sampleof_values = set()
        for machine in mame_root.findall('./machine'):
            sampleof = machine.get('sampleof')
            if sampleof:
                sampleof_values.add(sampleof + '.zip')


        # Iterate through files in the source folder
        for file in os.listdir(samples_folder):
            # If the file is a .zip and its name is in the sampleof_values set, copy it to the destination folder
            if file.endswith('.zip') and file in sampleof_values:
                shutil.copy(os.path.join(samples_folder, file), os.path.join(destination_folder, file))
                print(f'Moved {file} to {destination_folder}')

    """
    Step 4. Exit
    """

    closing_text = Text(f"Successfully created your new collection here: {output_folder}\n", style=styles.success)
    console.print(closing_text)
    close_text = Text(f"You may now close the window and get playing! {Emoji('slightly_smiling_face')}", style=styles.prompt)
    console.print(close_text)

    sys.exit(0)