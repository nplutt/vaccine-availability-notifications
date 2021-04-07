import os

import jinja2


def render_template(tpl_path: str, context: dict) -> str:
    path, filename = os.path.split(tpl_path)
    return (
        jinja2.Environment(
            loader=jinja2.FileSystemLoader(path or "./"),
        )
        .get_template(filename)
        .render(context)
    )
