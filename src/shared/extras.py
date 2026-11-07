"""Registry of optional regression variables shared by all regressions."""

from dataclasses import dataclass
from typing import Callable
import pandas as pd

from src.shared.config import LANGUAGE_FILE, WVS_FILE
from src.home_bias.language_proximity import add_language_proximity
from src.shared.national_pride import add_national_pride


@dataclass
class Extra:
    columns: list[str]
    add: Callable[[pd.DataFrame], pd.DataFrame]


EXTRAS = {
    "language_proximity": Extra(
        columns=["language_proximity"],
        add=lambda df: add_language_proximity(df, LANGUAGE_FILE),
    ),

    "national_pride": Extra(
        columns=["national_pride", "survey_responses"],
        add=lambda df: add_national_pride(df, WVS_FILE),
    ),
}