import os
from typing import Callable, List, Tuple

import pandas as pd
from jinja2 import Environment, FileSystemLoader

package_directory = os.path.dirname(os.path.abspath(__file__))
templateLoader = FileSystemLoader(
    searchpath=os.path.join(package_directory, "templates")
)
env = Environment(loader=templateLoader)


def format_table_to_hmtl(df: pd.DataFrame, color_fn: Callable = None):
    index_names = {
        "selector": ".index_name",
        "props": "color: darkgrey; font-weight:normal;",
    }
    headers = {
        "selector": "th:not(.index_name)",
        "props": "width: auto; \
            padding: 5px; \
            background-color: darkgrey; \
            color: white; \
            font-size: 13pt; \
            font-family: Arial",
    }
    striped = {"selector": "tr:nth-child(even)", "props": "background-color: #f2f2f2;"}
    output = df.style
    if color_fn is not None:
        output = output.applymap(color_fn)
    output = output.format(precision=3)
    output = output.set_table_styles([index_names, headers, striped])
    output = output.set_properties(
        **{
            "width": "auto",
            "padding": "10px",
            "text-align": "right",
            "font-size": "13pt",
            "font-family": "Arial",
        }
    )
    return output.to_html()


def render_tables(tables: List[Tuple[str, str]]):
    template = env.get_template("tables.html")
    return template.render(tables=tables)
