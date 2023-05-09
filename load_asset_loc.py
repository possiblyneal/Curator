import os
from pathlib import Path
import xml.etree.ElementTree as ET
from rich.console import Console

from asset_loc import asset_loc
from xml_combiner import combine_xml_data
import styles

def load_asset_loc():

    console = Console()

    def is_valid_file(file_path, file_name):
        return Path(file_path).exists() and Path(file_path).is_file() and os.path.basename(file_path) == file_name

    def is_valid_folder(folder_path, allow_none=False):
        if allow_none and folder_path.lower() == "none":
            return True
        return Path(folder_path).exists() and Path(folder_path).is_dir()

    file_folder_loc = "file_folder_loc.xml"

    if Path(file_folder_loc).exists():
        tree = ET.parse(file_folder_loc)
        root = tree.getroot()
        first_element = root.find("mame_exe")
        second_element = root.find("rebuilder_exe")
        third_element = root.find("catver_file")
        fourth_element = root.find("languages_file")
        fifth_element = root.find("roms_folder")
        sixth_element = root.find("chd_folder")
        seventh_element = root.find("samples_folder")

        if (first_element is not None and second_element is not None and third_element is not None and
                fourth_element is not None and fifth_element is not None and sixth_element is not None and
                seventh_element is not None and
                is_valid_file(first_element.text, 'mame.exe') and
                is_valid_file(second_element.text, 'rebuilder.exe') and
                is_valid_file(third_element.text, 'catver.ini') and
                is_valid_file(fourth_element.text, 'languages.ini') and
                is_valid_folder(fifth_element.text) and
                is_valid_folder(sixth_element.text, allow_none=True) and
                is_valid_folder(seventh_element.text, allow_none=True)):
            
            load_saved_prompt = f"[{styles.prompt}]Would you like to load the following saved file and folder locations?[/{styles.prompt}]\n[not bold white]mame.exe location = {first_element.text}\nrebuilder.exe location = {second_element.text}\ncatver.ini location = {third_element.text}\nlanguages.ini location = {fourth_element.text}\nROMs folder location = {fifth_element.text}\nCHDs folder location = {sixth_element.text}\nSamples folder location = {seventh_element.text}\n(y/n):[/not bold white]"

            while True:
                load_saved = console.input(load_saved_prompt)

                if load_saved.lower() == "y":
                    mame_exe = first_element.text
                    rebuilder_exe = second_element.text
                    catver_file = third_element.text
                    languages_file = fourth_element.text
                    roms_folder = fifth_element.text
                    chds_folder = sixth_element.text
                    samples_folder = seventh_element.text

                    console.print("Ok \n", style = styles.success)

                    combine_xml_data(mame_exe, catver_file, rebuilder_exe, languages_file, roms_folder, chds_folder, samples_folder)


                elif load_saved.lower() == "n":
                    console.print("Ok \n", style = styles.success)
                    asset_loc(file_folder_loc)

                else:
                    console.print("Please select one of the available options.\n", style = styles.error)

        else:
            console.print("Unable to read file_folder_loc.xml or file_folder_loc.xml contains invalid paths. Please re-enter the file and folder paths.\n", style = styles.error) 
            asset_loc(file_folder_loc)
    else:
        console.print("Let's get started by identifying a few file and folder locations. For the best performance use the latest version of Rebuilder and the latest version of MAME, with the corresponding ROMs/CHDs and .ini files.\n", style = styles.info )
        asset_loc(file_folder_loc)