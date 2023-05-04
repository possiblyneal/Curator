from pathlib import Path
from rich.prompt import Prompt
from rich.console import Console
from rich.text import Text
import xml.etree.ElementTree as ET
from xml.dom import minidom

from xml_combiner import combine_xml_data
import styles

def asset_loc(file_folder_loc):

    console = Console()

    mame_exe_prompt = Text("Enter the file location of mame.exe or type 'info'", style=styles.prompt)
    mame_exe_info = "Info: Navigate to https://www.mamedev.org/release.html to download the latest version.\n"

    while True:
        mame_exe = Prompt.ask(mame_exe_prompt, default="info", show_default=False)
        mame_exe = mame_exe.strip('"')
        
        if Path(mame_exe).is_file() and Path(mame_exe).name.lower() == 'mame.exe':
            console.print(f"File validated!\n", style=styles.success)
            break  
        elif mame_exe.lower() == "info":
            console.print(mame_exe_info, style=styles.info)
        else:
            console.print(f"Invalid file! Please provide a valid mame.exe file path.\n", style=styles.error)

    rebuilder_prompt = Text("Enter the file location of rebuilder.exe or type 'info'", style=styles.prompt)
    rebuilder_info = "Info: Navigate to https://mamedev.emulab.it/clrmamepro/#downloads to download rebuilder.exe.\n"

    while True:
        rebuilder_exe = Prompt.ask(rebuilder_prompt, default="info", show_default=False)
        rebuilder_exe = rebuilder_exe.strip('"')
        
        if Path(rebuilder_exe).is_file() and Path(rebuilder_exe).name.lower() == 'rebuilder.exe':
            console.print(f"File validated!\n", style=styles.success)
            break  
        elif rebuilder_exe.lower() == "info":
            console.print(rebuilder_info, style=styles.info)
        else:
            console.print(f"Invalid file! Please provide a valid rebuilder.exe file path.\n", style=styles.error)
            
    catver_prompt = Text("Enter the file location of catver.ini or type 'info'", style=styles.prompt)
    catver_info = "Info: Navigate to https://www.progettosnaps.net/catver/ to download catver.ini.\n"

    while True:
        catver_file = Prompt.ask(catver_prompt, default="info", show_default=False)
        catver_file = catver_file.strip('"')
        
        if Path(catver_file).is_file() and Path(catver_file).name.lower() == 'catver.ini':
            console.print(f"File validated!\n", style=styles.success)
            break  
        elif catver_file.lower() == "info":
            console.print(catver_info, style=styles.info)
        else:
            console.print(f"Invalid file! Please provide a valid catver.ini file path.\n", style=styles.error)

    languages_prompt = Text("Enter the file location of languages.ini or type 'info'", style=styles.prompt)
    languages_info = "Info: Navigate to https://www.progettosnaps.net/languages/ to download languages.ini.\n"

    while True:
        languages_file = Prompt.ask(languages_prompt, default="info", show_default=False)
        languages_file = languages_file.strip('"')
        
        if Path(languages_file).is_file() and Path(languages_file).name.lower() == 'languages.ini':
            console.print(f"File validated!\n", style=styles.success)
            break  
        elif languages_file.lower() == "info":
            console.print(languages_info, style=styles.info)
        else:
            console.print(f"Invalid file! Please provide a valid languages.ini file path.\n", style=styles.error)

    roms_folder_prompt = Text("Enter the file folder where your ROMs are stored or type 'info'", style=styles.prompt)
    roms_folder_info = Text("Info: It’s the folder that holds all the .zip files! A ROM is a digital file containing the data from a game's original read-only memory (ROM) chip.\n")
    while True:
        roms_folder = Prompt.ask(roms_folder_prompt, default="info", show_default=False)
        roms_folder = roms_folder.strip('"')
        
        if Path(roms_folder).is_dir():
            console.print(f"location validated!\n", style=styles.success)
            break
        elif roms_folder.lower() == "info":
            console.print(roms_folder_info, style=styles.info)    
        else:
            console.print(f"Invalid directory! Please provide a valid ROM directory.\n", style=styles.error)

    use_chds_prompt = Text("Would you like to include CHDs in your collection? (y/n/info)", style=styles.prompt)

    while True:
        use_chds = Prompt.ask(use_chds_prompt, default="info", show_default=False)
        use_chds_info = Text("A CHD (Compressed Hunks of Data) file is a compressed digital representation of additional data associated with an arcade game, usually used for larger storage devices such as hard drives, CD-ROMs, or LaserDiscs. CHDs need the corresponding ROM to run in MAME.\n")
        if use_chds.lower() == "info":
            console.print(use_chds_info, style=styles.info)
        elif use_chds.lower() == "y":
            console.print("Ok\n", style=styles.success)
            chd_folder_prompt = Text("Enter the file folder location where your CHDs are stored (or \"back\" to go back)", style=styles.prompt)
            chd_folder_info = Text("Info: It’s the folder that holds all the .chd files! A CHD (Compressed Hunks of Data) file is a compressed digital representation of additional data associated with an arcade game, usually used for larger storage devices such as hard drives, CD-ROMs, or LaserDiscs. CHDs need the corresponding ROM to run in MAME.\n")
            while True:
                chds_folder = Prompt.ask(chd_folder_prompt, default="info", show_default=False)
                chds_folder = chds_folder.strip("'")
                
                if Path(chds_folder).is_dir():
                    console.print(f"location validated!\n", style=styles.success)
                    break
                elif chds_folder.lower() == "info":
                    console.print(chd_folder_info, style=styles.info)    
                elif chds_folder.lower() == "back":
                    print("\n")
                    break
                else:
                    console.print(f"Invalid directory! Please provide a valid CHD directory.\n", style=styles.error)
            if Path(chds_folder).is_dir():
                break
        elif use_chds.lower() == "n":
            console.print("Ok\n", style=styles.success)
            chds_folder = "none"
            break
        else:
            console.print(f"Please select one of available options\n", style=styles.error)


    use_samples_prompt = Text("Would you like to include samples in your collection? (y/n/info)", style=styles.prompt)

    while True:
        use_samples = Prompt.ask(use_samples_prompt, default="info", show_default=False)
        if use_samples.lower() == "info":
            console.print("Info: A MAME sample is a collection of audio files used to reproduce sounds that the MAME emulator (Multiple Arcade Machine Emulator) cannot generate accurately due to limitations or inaccuracies in the emulation of certain arcade hardware. MAME samples are typically in WAV format and are organized in folders corresponding to specific games. They can be downloaded here: https://samples.mameworld.info/. The \"Current Samples\" link contains all the required samples for the latest version of MAME.\n", style=styles.info)
        elif use_samples.lower() == "y":
            console.print("Ok\n", style=styles.success)
            samples_folder_prompt = Text("Enter the file folder location where your samples are stored (or \"back\" to go back)", style=styles.prompt)
            samples_folder_info = "Info: It’s the folder that holds all the samples! A MAME sample is a collection of audio files used to reproduce sounds that the MAME emulator (Multiple Arcade Machine Emulator) cannot generate accurately due to limitations or inaccuracies in the emulation of certain arcade hardware. MAME samples are typically in WAV format and are organized in folders corresponding to specific games. They can be downloaded here: https://samples.mameworld.info/. The \"Current Samples\" link contains all the required samples for the latest version of MAME.\n"
            while True:
                samples_folder = Prompt.ask(samples_folder_prompt, default="info", show_default=False)
                samples_folder = samples_folder.strip("'")
                
                if Path(samples_folder).is_dir():
                    console.print(f"location validated!\n", style=styles.success)
                    break
                elif samples_folder.lower() == "info":
                    console.print(samples_folder_info, style=styles.info)    
                elif samples_folder.lower() == "back":
                    print("\n")
                    break
                else:
                    console.print(f"Invalid directory! Please provide a valid samples directory.\n", style=styles.error)
            if Path(samples_folder).is_dir():
                break
        elif use_samples.lower() == "n":
            console.print("Ok\n", style=styles.success)
            samples_folder = "none"
            break
        else:
            console.print(f"Please select one of available options\n", style=styles.error)

    def prettify(elem):
        rough_string = ET.tostring(elem, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")

    # Prompt text for saving file and folder locations
    save_prompt = Text("Would you like to save your file and folder locations to use next time you run Curator? (y/n/info)", style=styles.prompt)
    save_info = "This saves your folder and file locations to file_folder_loc.xml, which can be imported the next time you run Curator.\n"

    while True:
        save_decision = Prompt.ask(save_prompt, choices=["y", "n", "info"], show_choices=False, show_default=False, default="info")

        if save_decision == "y":
            # Create XML structure
            root = ET.Element("locations")
            ET.SubElement(root, "mame_exe").text = mame_exe
            ET.SubElement(root, "rebuilder_exe").text = rebuilder_exe
            ET.SubElement(root, "catver_file").text = catver_file
            ET.SubElement(root, "languages_file").text = languages_file
            ET.SubElement(root, "roms_folder").text = roms_folder
            ET.SubElement(root, "chd_folder").text = chds_folder
            ET.SubElement(root, "samples_folder").text = samples_folder

            # Convert XML structure to a pretty-printed string
            pretty_xml = prettify(root)

            # Save the pretty-printed XML string to a file
            try:
                with open(file_folder_loc, 'w') as f:
                    f.write(pretty_xml)
                console.print("Saved file and folder locations successfully.\n", style=styles.success)
            except IOError as e:  # Handle file-related errors
                console.print(f"Error saving file and folder locations: {e}", style=styles.error)
                input("Press Enter to continue...")

            combine_xml_data(mame_exe, catver_file, rebuilder_exe, languages_file, roms_folder, chds_folder, samples_folder)
            
        elif save_decision == "info":
            console.print(save_info, style=styles.info)
        elif save_decision == "n":
            console.print("Ok\n", style=styles.success)
            combine_xml_data(mame_exe, catver_file, rebuilder_exe, languages_file, roms_folder, chds_folder, samples_folder)
