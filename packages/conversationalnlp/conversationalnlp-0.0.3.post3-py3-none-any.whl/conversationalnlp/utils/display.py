import pandas as pd
import random


def show_random_elements(dataset, num_examples=1):
    assert num_examples <= len(
        dataset), "Can't pick more elements than there are in the dataset."
    picks = []
    for _ in range(num_examples):
        pick = random.randint(0, len(dataset)-1)
        while pick in picks:
            pick = random.randint(0, len(dataset)-1)
        picks.append(pick)

    df = pd.DataFrame(dataset[picks])

    from IPython.display import display, HTML
    display(HTML(df.to_html()))
