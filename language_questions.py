import xml.etree.ElementTree as ET
from collections import Counter
from rich import print
from rich.table import Table
from rich.text import Text
from rich.console import Console

import styles
from clone_questions import clone

console=Console()

def language(mame_tree, mame_root, rebuilder_exe, roms_folder, chds_folder, samples_folder):

    def parse_and_count_languages(mame_root):
        language_counter = Counter()
        for child in mame_root:
            language = child.find("language")
            if language is not None:
                language_counter[language.text] += 1
        return language_counter

    def display_table(language_counter):
        sorted_languages = sorted(language_counter.items(), key=lambda x: x[0])
        table = Table(title="Number of Games by Language in Collection", title_style=styles.info)

        table.add_column("Row", justify="right")
        table.add_column("Language")
        table.add_column("Number of Games")

        for i, (language, count) in enumerate(sorted_languages, start=1):
            table.add_row(str(i), language, str(count))

        print(table)
        return sorted_languages

    while True:
        language_counter = parse_and_count_languages(mame_root)
        sorted_languages = display_table(language_counter)

        while True:
            input_text = Text("Which language(s) would you like to remove from your collection? Enter the row number to remove the"
                            " associated genre. You may enter multiple numbers separated by a comma. Enter 'done' to continue: "
                            , style=styles.prompt)
            user_input = console.input(input_text)

            if user_input.lower() == "done":
                break

            rows = user_input.split(',')
            rows_to_remove = []
            invalid_input = False

            for row in rows:
                row = row.strip()
                if row.isdigit():
                    row_num = int(row)
                    if 1 <= row_num <= len(sorted_languages):
                        rows_to_remove.append(row_num)
                    else:
                        invalid_input = True
                        break
                else:
                    invalid_input = True
                    break

            if invalid_input:
                error_text = Text("Error: Invalid input. Please enter a valid number or 'done' to continue.\n", style=styles.error)
                console.print(error_text)
            else:
                break

        if user_input.lower() == "done":
            console.print("Ok\n", style=styles.success)
            break

        languages_to_remove = [sorted_languages[row - 1][0] for row in rows_to_remove]

        removed_machines = 0
        for child in mame_root.findall("machine"):
            language = child.find("language")
            if language is not None and language.text in languages_to_remove:
                mame_root.remove(child)
                removed_machines += 1

        success_text = Text(f"Success! {removed_machines} games have been filtered out of your collection. You now have {len(mame_root)} games.\n", style=styles.success)
        console.print(success_text)

    clone(mame_tree, mame_root, rebuilder_exe, roms_folder, chds_folder, samples_folder)
