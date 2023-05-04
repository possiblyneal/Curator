import re
from rich.console import Console
from rich.text import Text

from control_questions import control
import styles

def year(mame_tree, mame_root, rebuilder_exe, roms_folder, chds_folder, samples_folder):

    console = Console()

    def get_year_range(mame_root):
        years = []
        for machine in mame_root.findall('.//machine'):
            year = machine.find('year')
            if year is not None:
                year_text = year.text.strip()
                if re.fullmatch(r'\d{4}', year_text):
                    years.append(int(year_text))
        return min(years), max(years)


    def filter_machines_by_year(mame_root, start_year, end_year):
        machines_to_remove = []
        for machine in mame_root.findall('.//machine'):
            year = machine.find('year')
            if year is not None:
                year_text = year.text.strip()
                if re.fullmatch(r'\d{4}', year_text):
                    if int(year_text) < start_year or int(year_text) > end_year:
                        machines_to_remove.append(machine)
                else:
                    machines_to_remove.append(machine)
            else:
                machines_to_remove.append(machine)
        
        if not machines_to_remove:
            return 0, len(mame_root.findall('.//machine'))
        
        num_removed = len(machines_to_remove)
        for machine in machines_to_remove:
            mame_root.remove(machine)
        
        num_remaining = len(mame_root.findall('.//machine'))
        return num_removed, num_remaining


    while True:
        user_input_prompt = Text("Would you like to skip games released in certain years? (y/n/info):", style=styles.prompt)
        user_input = console.input(user_input_prompt).lower()

        if user_input == "n":
            console.print("Ok\n", style=styles.success)
            break
        elif user_input == "info":
            info_text = Text("Info: Allows you to create collections from different eras. 80's, 90's, '79-'83 The Golden Age, etc. Could also help limit demanding games that your hardware can't run.\n", style=styles.info)
            console.print(info_text)
        elif user_input == "y":
            console.print("Ok\n", style=styles.success)
            min_year, max_year = get_year_range(mame_root)

            text_min_year_part1 = Text("Earliest release year availible: ", style=styles.info)
            text_min_year_part2 = Text(f"{min_year}", style=styles.info)
            text_min_year = text_min_year_part1 + text_min_year_part2
            console.print(text_min_year)

            text_max_year_part1 = Text("Latest release year availible: ", style=styles.info)
            text_max_year_part2 = Text(f"{max_year}", style=styles.info)
            text_max_year = text_max_year_part1 + text_max_year_part2
            console.print(text_max_year)
    
            while True:
                try:
                    start_year_prompt = Text("What is the earliest release year you would like to include in your collection? ", style=styles.prompt)
                    start_year = int(console.input(start_year_prompt))
                    if len(str(start_year)) != 4:
                        raise ValueError
                    break
                except ValueError:
                    console.print("Please enter a 4-digit year.", style=styles.error)

            while True:
                try:
                    end_year_prompt = Text("What is the latest release year you would like to include in your collection? ", style=styles.prompt)
                    end_year = int(console.input(end_year_prompt))
                    if len(str(end_year)) != 4 or end_year <= start_year:
                        raise ValueError
                    break
                except ValueError:
                    console.print("Please enter a 4-digit year. Must come after the beginning of your specified time frame.", style=styles.error)
                    
            try:
                num_removed, num_remaining = filter_machines_by_year(mame_root, start_year, end_year)
                update_text = Text(f"Success! {num_removed} games removed from database. Your collection now has {num_remaining} games.", style=styles.success)
                console.print(update_text)
                print("\n")
            except Exception as e:
                console.print("An error occurred while filtering games:", e, style=styles.error)
                break

            filter_machines_by_year(mame_root, start_year, end_year)
            break
        else:
            console.print("Invalid input. Please enter 'y', 'n', or 'info'.", style=styles.error)
            continue

    control(mame_tree, mame_root, rebuilder_exe, roms_folder, chds_folder, samples_folder)