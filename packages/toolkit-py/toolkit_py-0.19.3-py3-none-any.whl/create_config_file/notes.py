"""
Date: 2022.02.06 16:43
Description: Omit
LastEditors: Rustle Karl
LastEditTime: 2022.02.06 16:43
"""
import os
import time
from pathlib import Path
from typing import Union

from project_scaffold.notes import TEMPLATE_ARTICLE_CONTENT, TEMPLATE_ARTICLE_SETTINGS

NOTE_HEADER_SEPARATOR = "---\n"

NOTE_HEADER_CREATOR = f"""\
date: {time.strftime("%Y-%m-%dT%H:%M:%S+08:00")}
author: "Rustle Karl"
"""

NOTE_HEADER_TITLE = """\
title: "{title}"
url:  "{url}"  # 永久链接
"""


def generate_notes_header(path, only_header=False):
    cwd = os.path.abspath(os.getcwd())
    prefix = os.path.basename(cwd)

    uri = os.path.splitext(path)[0]
    title = os.path.basename(uri)
    url = os.path.normpath("/".join(["posts", prefix, uri])).replace("\\", "/")

    template_article = (
        NOTE_HEADER_SEPARATOR
        + NOTE_HEADER_CREATOR
        + "\n"
        + NOTE_HEADER_TITLE.format(title=title, url=url)
    )

    if os.path.isfile(TEMPLATE_ARTICLE_SETTINGS.file):
        with open(TEMPLATE_ARTICLE_SETTINGS.file, encoding="utf-8") as fp:
            content = fp.read()
            if content:
                template_article += content
            else:
                template_article += TEMPLATE_ARTICLE_SETTINGS.content

    template_article += NOTE_HEADER_SEPARATOR + "\n"

    if not only_header and os.path.isfile(TEMPLATE_ARTICLE_CONTENT.file):
        with open(TEMPLATE_ARTICLE_CONTENT.file, encoding="utf-8") as fp:
            content = fp.read()
            if content:
                template_article += (content + "\n\n") * 5
            else:
                template_article += (TEMPLATE_ARTICLE_CONTENT.content + "\n\n") * 5

    return template_article


def notes(path):
    if os.path.exists(path):
        return

    parent = os.path.dirname(path)
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)

    template_article = generate_notes_header(path)

    with open(path, "w", encoding="utf-8", newline="\n") as fp:
        fp.write(template_article)


def notes_append_header(path: Union[Path, str]):
    """添加到已存在的笔记"""

    path = Path(path)

    if not path.exists():
        return

    if path.is_dir():
        for entry in path.iterdir():
            notes_append_header(entry)
    elif path.suffix == ".md":
        if path.open().read(3) == "---":
            return

        template_article = generate_notes_header(path, only_header=True)
        old_content = path.read_text(encoding="utf-8")

        with open(path, "w", encoding="utf-8", newline="\n") as fp:
            fp.write(template_article + old_content)
