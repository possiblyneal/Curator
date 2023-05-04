import xml.etree.ElementTree as ET
import os
import zipfile
from rich.console import Console
from rich.text import Text

from rich_pbar import loaded_pbar
import styles
from mamefile_extractor import extract_mame_xml
from ini_data import ini_data
from basic_questions import questions


def combine_xml_data(mame_exe, catver_file, rebuilder_exe, languages_file, roms_folder, chds_folder, samples_folder):

    console = Console()

    """
    Section 1. Extract and parse mame.xml
    """

    # Call the extract mame xml function to extract mame.xml from mame.exe
    extract_mame_xml(mame_exe)
          
    with console.status(f"[{styles.processing}]Loading MAME database...", spinner="bouncingBall", spinner_style=styles.processing):
        mame_tree = ET.parse("mame.xml")
        mame_root = mame_tree.getroot()

    console.print("Successfuly loaded MAME database.", style=styles.done_processing)

    """
    Section 2. Add Genre and Language data to xml
    """

    mame_root = ini_data(mame_root, catver_file, languages_file)

    """
    Section 3. Create a set of all owned ROM/CHD fileneames
    """
    
    # Create a set of file names in the roms folder and chd folder
    def add_folder_names_from_zip(zip_file_path, names_set):
        with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
            for item in zip_file.infolist():
                file_path_parts = item.filename.split('/')
                if len(file_path_parts) > 1:
                    names_set.add(file_path_parts[0])

    roms = set()

    total_roms = sum(1 for _ in os.scandir(roms_folder))

    # Add zip file names and folder names inside zip files in roms_folder
    with loaded_pbar(console=console) as progress:
        task_id = progress.add_task(description="Identifying ROMs", total=total_roms)
        with os.scandir(roms_folder) as entries:
            for entry in entries:
                if entry.is_file() and entry.name.endswith(".zip"):
                    roms.add(entry.name.split('.')[0])
                    add_folder_names_from_zip(entry.path, roms)
                progress.advance(task_id)

    # Add zip file names and folder names inside zip files in chd_folder, if it's not "none"
    if chds_folder != "none":
        chds = set()
        total_chds = sum(1 for _ in os.scandir(chds_folder))
        with loaded_pbar(console=console) as progress:
            task_id = progress.add_task(description="Identifying CHDs", total=total_chds)
            with os.scandir(chds_folder) as entries:
                for entry in entries:
                    if entry.is_file() and entry.name.endswith(".chd"):
                        chds.add(entry.name.split('.')[0])                     
                    progress.advance(task_id)


    """
    Section 4. Remove any machines in the xml not matching ROM/CHD in folders
    """

    # Remove machines not matching a file in the ROM or CHD folders

    mame_root[:] = [machine for machine in mame_root if machine.get('name') in roms or chds]

    # Print the number of loaded games
    loaded_games_text = Text(f"You have loaded {len(mame_root)} games successfully.\n", style=styles.success)
    console.print(loaded_games_text)
    console.print(
        "Curator works by identifiying games that you wont want to play or can't play based on how you respond to a " 
        "series of questions and removing them from its internal database. Curator will use this database to create your "
        "new curated MAME collection. Your source folders will not be changed.\n", style=styles.info
        )
      
    questions(mame_tree, mame_root, rebuilder_exe, roms_folder, chds_folder, samples_folder)