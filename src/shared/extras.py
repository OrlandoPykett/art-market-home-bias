"""Registry of optional regression variables shared by all regressions."""

from dataclasses import dataclass
from typing import Callable
import pandas as pd

from src.shared.config import LANGUAGE_FILE
from src.home_bias.language_proximity import add_language_proximity


@dataclass
class Extra:
    columns: list[str]
    add: Callable[[pd.DataFrame], pd.DataFrame]


EXTRAS = {
    "language_proximity": Extra(
        columns=["language_proximity"],
        add=lambda df: add_language_proximity(df, LANGUAGE_FILE),
    ),
}