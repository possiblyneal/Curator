import re
from rich.table import Table
from rich.console import Console
from rich.text import Text

import styles

console = Console()

def joystick_ways(mame_root):
    def remove_machines_by_controls(mame_root, control_to_remove):
        machines_to_remove = []
        for machine in mame_root.findall('machine'):
            for control in machine.findall('.//control'):
                control_type = control.get('type')
                control_ways = control.get('ways')

                if (control_type, control_ways) in control_to_remove:
                    machines_to_remove.append(machine)
                    break

        for machine in machines_to_remove:
            mame_root.remove(machine)

        return len(machines_to_remove)

    def print_control_ways_table():
        control_type_ways_set = set()
        control_combination_count = {}

        if mame_root is not None:
            for machine in mame_root.findall('machine'):
                machine_controls = set()
                for control in machine.findall('.//control'):
                    control_type = control.get('type')
                    control_ways = control.get('ways')

                    if control_type and control_ways:
                        control_type_ways = (control_type, control_ways)
                        control_type_ways_set.add(control_type_ways)
                        machine_controls.add(control_type_ways)

                for control in machine_controls:
                    control_combination_count[control] = control_combination_count.get(control, 0) + 1

        def extract_numeric(value):
            return int(re.search(r'\d+', value).group())

        def sort_control_combinations(control_set):
            sorted_controls = sorted(control_set, key=lambda x: (['joy', 'doublejoy', 'triplejoy'].index(x[0]) if x[0] in ['joy', 'doublejoy', 'triplejoy'] else len(['joy', 'doublejoy', 'triplejoy']), extract_numeric(x[1])))

            return sorted_controls

        def display_table(sorted_combinations, control_combination_count):
            console = Console()
            table = Table(show_header=True, header_style=None)
            table.add_column("No.")
            table.add_column("Type")
            table.add_column("Ways")
            table.add_column("No. of Games")

            for index, combination in enumerate(sorted_combinations, start=1):
                table.add_row(str(index), combination[0], combination[1], str(control_combination_count[combination]))

            console.print(table)

        sorted_combinations = sort_control_combinations(control_type_ways_set)
        display_table(sorted_combinations, control_combination_count)
        return sorted_combinations

    while True:
        sorted_combinations = print_control_ways_table()
        ways_prompt = Text("What control type(s) would you like to remove from your collection? Enter the number in the left column to eliminate the corresponding games from your list. You may enter multiple numbers separated by a comma. Type 'done' to continue:", style=styles.prompt)
        user_input = console.input(ways_prompt)

        if user_input.lower() == 'done':
            console.print("Ok\n", style=styles.success)
            break

        control_indexes = user_input.split(',')
        control_to_remove = set()

        for index in control_indexes:
            try:
                control_index = int(index.strip()) - 1
                control_to_remove.add(sorted_combinations[control_index])
            except (ValueError, IndexError):
                console.print(f"Invalid input: {index.strip()}", style=styles.error)

        removed_machines = remove_machines_by_controls(mame_root, control_to_remove)
        update_text = Text(f"Success! {removed_machines} games have been filtered out of your collection. You now have {len(mame_root)} games.\n", style=styles.success)
        console.print(update_text)

    return mame_root