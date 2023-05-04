from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, RenderableType
from rich.text import Text

import styles

class CustomSpinnerColumn(SpinnerColumn):
    def render(self, task):
        if task.finished:
            self.style = styles.done_processing  # Change color when the progress bar is finished
            return Text("")
        return super().render(task)

class CustomTextColumn(TextColumn):
    def __init__(self, text_format):
        super().__init__(text_format)
    
    def render(self, task):
        text = super().render(task)
        if task.finished:
            text.stylize(styles.done_processing)  # Change color when the progress bar is finished
        elif task.elapsed:
            text.stylize(styles.processing)
        return text

class CustomPercentageColumn(TextColumn):
    def render(self, task):
        if task.finished:
            return Text("Complete!\n", style=styles.done_processing)
        else:
            return Text(f"{task.percentage:>3.0f}%", style=styles.processing)

def loaded_pbar(*args, **kwargs):
    return Progress(
        CustomTextColumn(text_format="{task.description}"),
        BarColumn(complete_style=styles.processing),
        CustomPercentageColumn(text_format=""),
        *args,
        **kwargs
    )

