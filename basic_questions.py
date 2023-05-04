from rich.console import Console
from rich.text import Text
import re
import os

from year_questions import year
import styles

console = Console()


def questions(mame_tree, mame_root, rebuilder_exe, roms_folder, chds_folder, samples_folder):

    # Function to eliminate elements based on condition
    def eliminate_elements(temp_root, condition):
        removed_count = 0
        for machine in temp_root.findall('machine'):
            if condition(machine):
                temp_root.remove(machine)
                removed_count += 1
        return removed_count

    # Function to print and handle prompts
    def prompt_handler(prompt, info_text, condition):
        valid_responses = ['y', 'n', 'info']
        while True:
            response = console.input(prompt).lower()
            if response in valid_responses:
                if response == 'info':
                    element_count = sum(1 for machine in mame_root.findall('machine') if condition(machine))
                    console.print(Text(f"{info_text} If you proceed, {element_count} machines will be removed.\n", style=styles.info))
                else:
                    if response == 'y':
                        removed_count = eliminate_elements(mame_root, condition)
                        console.print(Text(f"Success! {removed_count} games have been filtered out of your collection. You now have {len(mame_root)} games.\n", style=styles.success))
                    else:
                        console.print("Ok\n", style=styles.success)
                    break
            else:
                console.print("Please select one of the available options.\n", style=styles.error)

    # Remove mechanical devices
    prompt_handler(
        Text("Remove mechanical devices? (y/n/info):", style=styles.prompt),
        "Info: Strongly Reccomended. Mechanical or electro-mechanical games are those that rely on physical components and mechanisms to operate, such as pinball machines, arcade shooting galleries, or older gambling machines. These games often involve moving parts, gears, or other mechanical elements, and may also incorporate electronic components, such as lights, sound, or basic circuitry. MAME doesn't simulate the physical aspects of these devices.",
        lambda machine: machine.attrib.get('ismechanical', '') == 'yes'
    )

    # Remove games MAME is unable to run
    prompt_handler(
        Text("Remove games MAME is unable to run? (y/n/info):", style=styles.prompt),
        "Info: Strongly Reccomended. These games cannot be executed or played directly within the emulator. These are typically components of other machines (processors, interfaces, printers, etc.)",
        lambda machine: machine.attrib.get('runnable', '') == 'no'
    )

    # Remove BIOSes
    prompt_handler(
        Text("Remove BIOSes? (y/n/info):", style=styles.prompt),
        "Info: Strongly Recommended. A BIOS (Basic Input/Output System) is the firmware or software that powers the basic hardware operations of an arcade machine. (Recommended)",
        lambda machine: machine.attrib.get('isbios', '') == 'yes'
    )

    # Remove devices
    prompt_handler(
        Text("Remove devices? (y/n/info):", style=styles.prompt),
        "Info: Strongly Recommended. Devices refer to hardware components or peripherals that can be connected to an arcade machine. These devices can include various types of controllers, memory expansion units, storage devices, or any other hardware that enhances the functionality of the system or adds new features. (Recommended)",
        lambda machine: machine.attrib.get('isdevice', '') == 'yes'
    )

    # Remove games without a display
    prompt_handler(
        Text("Remove games that do not have a display (y/n/info):", style=styles.prompt),
        "Info: Strongly Recommended. These arcade games do not have a display associated with them and will not display anything on screen when run in MAME.",
        lambda machine: machine.find('display') is None
    )

    # Remove bootleg games
    prompt_handler(
        Text("Remove bootleg games? (y/n/info):", style=styles.prompt),
        "Info: Recommended. The most accurate definition in relation to arcade games is 'unauthorized pirate version'. Usually this word is used to refer to the games that are hacked or ported to different hardware by someone other than the game manufacturer. Often this is coupled with removing the copy protection, and the bootleggers may also have modified the game itself. Frequently the game is also degraded to run on lower-cost hardware, increasing the bootlegger's profits. Amusingly, many bootlegs include their own new protection scheme to prevent other bootleggers from using it.",
        lambda machine: any(word.lower() == 'bootleg' for word in re.findall(r"[\w']+|[.,!?;]", machine.find('description').text or '') + re.findall(r"[\w']+|[.,!?;]", machine.find('manufacturer').text or ''))
    )

    # Remove hacked games
    prompt_handler(
        Text("Remove hacked games? (y/n/info):", style=styles.prompt),
        "Info: Recommended. A hack typically refers to a modified version of the original game's code that has been altered to change the gameplay, graphics, or other aspects of the game by individuals or groups other than the original developers. These modifications can range from simple cosmetic changes to significant alterations of the game mechanics, levels, or characters, and are not sanctioned or created by the game's original developers. Many MAME bootlegs are also referred to as hacks.",
        lambda machine: any(word.lower() == 'hack' for word in re.findall(r"[\w']+|[.,!?;]", machine.find('description').text or '') + re.findall(r"[\w']+|[.,!?;]", machine.find('manufacturer').text or ''))
    )

    # Remove PlayChoice-10 Games
    prompt_handler(
        Text("Remove PlayChoice-10 Games? (y/n/info):", style=styles.prompt),
        "Info: Recommended for players who emulate NES roms through another emulator. PlayChoice-10 games are a type of arcade game system that was developed and released by Nintendo in the late 1980s. The PlayChoice-10 system was essentially a modified version of the Nintendo Entertainment System (NES) that was designed to be used in arcade settings. The games are the same as their NES counterparts.",
        lambda machine: machine.get('sourcefile') == "nintendo/playch10.cpp"
    )

    # Remove Nintendo Super System Games
    prompt_handler(
        Text("Remove Nintendo Super System Games? (y/n/info):", style=styles.prompt),
        "Info: Recommended for players who emulate SNES roms through another emulator. The Nintendo Super System (NSS) was an arcade system developed and released by Nintendo in 1991. It was designed to bring Super Nintendo Entertainment System (SNES) games to the arcade environment. The NSS was essentially a modified SNES console that allowed operators to install multiple game cartridges simultaneously, giving arcade-goers the opportunity to play a selection of popular SNES titles. The games are the same as their NES counterparts.",
        lambda machine: machine.get('sourcefile') == "nintendo/nss.cpp"
    )

    # Remove games that require a CHD
    prompt_handler(
        Text("Remove games that require a CHD? (y/n/info):", style=styles.prompt),
        "Info: Recommended for players without any CHDs. CHD stands for Compressed Hunks of Data, and refers to a type of file format that is used in some arcade games and other retro gaming systems. CHD files are typically used to store large amounts of data, such as game graphics, audio, and video, in a more efficient and compressed format. Select this if you don't have any .CHD files.",
        lambda machine: machine.find('disk') is not None
    )

    # Remove games featuring nudity
    prompt_handler(
        Text("Remove games featuring nudity? (y/n/info):", style=styles.prompt),
        "Info: This uses a 3rd party list to filter out games that are categorized as mature, but it does not filter out games that feature strong language, violence, drug abuse, or other adult themes. It only filters out games containing nudity.",
        lambda machine: machine.find('category') is not None and "* Mature *" in machine.find('category').text

    )

    # Remove non arcade games
    prompt_handler(
        Text("Remove non arcade games? (y/n/info):", style=styles.prompt),
        "Info: Recommended. This removes anything without a coin slot or bill acceptor. Slot machines and other gambling devices will still remain, but you can remove these by category in a later question.",
        lambda machine: machine.find('input') is None or 'coins' not in machine.find('input').attrib
    )

    # Game compatibility
    compatability_prompt_text = f"[{styles.prompt}]MAME lists three levels of compatibility for each of their games: preliminary, imperfect, and good. Enter the lowest level of compatibility you would like to include in your collection:[/{styles.prompt}]\n[not bold white]1. Preliminary: Games may not run properly or could have significant issues. Emulation is incomplete, and users should expect a subpar experience. (For advanced users or those willing to accept potentially unplayable games)\n2. Imperfect: Highly recommended. Games are mostly functional, but may have minor issues with graphics, sound, or gameplay. Still enjoyable, but not perfect.\n3. Good: Games run well and are fully functional with accurate emulation.\n(1/2/3):[/not bold white]"
    valid_responses = ['1', '2', '3']
    while True:
        response = console.input(compatability_prompt_text)
        if response in valid_responses:
            initial_count = len(mame_root)
            if response == '1':
                console.print("Ok", style=styles.success)
            elif response == '2':
                mame_root[:] = [machine for machine in mame_root if machine.find('driver').get('status') != 'preliminary']
            else:
                mame_root[:] = [machine for machine in mame_root if machine.find('driver').get('status') == 'good']
            
            removed_count = initial_count - len(mame_root)
            console.print(Text(f"Success! {removed_count} games have been filtered out of your collection. You now have {len(mame_root)} games.\n", style=styles.success))
            break
        else:
            console.print("Please select one of the available options.\n", style=styles.error)

    # Prototypes
    proto_prompt_text = Text("Remove some or all prototypes? (y/n/info):", style=styles.prompt)
    info_text = "Info: Prototypes are early or pre-release versions of arcade games that were used for testing or demonstration purposes. These versions can have unfinished or missing features, different game mechanics, or alternate graphics and sounds. Prototypes can provide an interesting look at the development process of a game, but may not be as enjoyable or polished as the final release."
    valid_responses = ['y', 'n', 'info']
    exit_flag = False

    while True:
        response = console.input(proto_prompt_text).lower()
        if response in valid_responses:
            if response == 'info':
                console.print(info_text + "\n", style=styles.info)
            elif response == 'n':
                console.print("Ok\n", style=styles.success)
                break
            else:
                keep_text = Text("Keep final prototype version for unreleased arcade games? (y/n)", style=styles.prompt)
                valid_responses_keep = ['y', 'n']
                while True:
                    response = console.input(keep_text).lower()
                    if response in valid_responses_keep:
                        if response == 'n':
                            condition = lambda machine: any(word.lower() in ['proto', 'prototype'] for word in re.findall(r"[\w']+|[.,!?;]", machine.find('description').text or ''))
                        elif response == 'y':
                            condition = lambda machine: 'cloneof' in machine.attrib and any(word.lower() in ['proto', 'prototype'] for word in re.findall(r"[\w']+|[.,!?;]", machine.find('description').text or ''))
                        removed_count = eliminate_elements(mame_root, condition)
                        console.print(Text(f"Success! {removed_count} prototypes have been filtered out of your collection. You now have {len(mame_root)} games.\n", style=styles.success))
                        exit_flag = True
                        break
                    else:
                        console.print("Please select one of the available options.\n", style=styles.error)
                if exit_flag:
                    break
        else:
            console.print("Please select one of the available options.\n", style=styles.error)

    # Samples
    sample_prompt_text = Text("Remove games requiring samples that you don't have? (y/n/info):", style=styles.prompt)
    info_text = "Info: This will remove any games that call for samples that are not in your samples folder. If you did not identify a samples folder, this will remove all games requiring samples."
    valid_responses = ['y', 'n', 'info']
    while True:
        response = console.input(sample_prompt_text).lower()
        if response in valid_responses:
            if response == 'info':
                sample_files = os.listdir(samples_folder)
                machines_to_remove = 0
                for machine in mame_root.findall('machine'):
                    sampleof_attribute = machine.get('sampleof')
                    if sampleof_attribute and f"{sampleof_attribute}.zip" not in sample_files:
                        machines_to_remove += 1
                console.print(Text(f"If you proceed, {machines_to_remove} games will be removed.\n", style=styles.info))
            elif response == 'n':
                console.print("Ok\n", style=styles.success)
            else:
                sample_files = os.listdir(samples_folder)
                removed_count = 0
                for machine in mame_root.findall('machine'):
                    sampleof_attribute = machine.get('sampleof')
                    if sampleof_attribute and f"{sampleof_attribute}.zip" not in sample_files:
                        mame_root.remove(machine)
                        removed_count += 1
                console.print(Text(f"Success! {removed_count} games have been filtered out of your collection. You now have {len(mame_root)} games.\n", style=styles.success))
                break
        else:
            console.print("Please select one of the available options.\n", style=styles.error)

    year(mame_tree, mame_root, rebuilder_exe, roms_folder, chds_folder, samples_folder)

