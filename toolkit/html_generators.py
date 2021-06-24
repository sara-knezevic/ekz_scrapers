from typing import List

from bs4 import BeautifulSoup
from html2text import html2text

def create_html_for_line_changed_group(diff: List[str]) -> str:
    html = '<div class="singleDiff">Promenjeno na sajtu<br><div class="separator">\n'
    change_flag = False

    # ? These kind of changes always come with a duplicated text which
    # ? makes it easer to see what was actually modified
    # ? because of that we are calculating old_changes_end_idx
    old_changes_end_idx = len(diff) // 2

    old_slice = diff[:old_changes_end_idx]
    new_slice = diff[old_changes_end_idx:]

    for line in new_slice:
        line = BeautifulSoup(line, "lxml").text
        if line[0:2] == '! ':
            if (line[1:].strip() != ''):
                html += '<p><span class="newText">' + line[1:] + '</span></p>\n'
                change_flag = True
        # else:
        #     html += '<p>{}</p>\n'.format(line)

    html += '</div>\n'

    for line in old_slice:
        line = BeautifulSoup(line, "lxml").text
        if line[0:2] == '! ':
            if (line[1:].strip() != ''):
                html += '<p><span class="oldText">' + line[1:] + '</span></p>\n'
                change_flag = True
        # else:
        #     html += '<p>{}</p>\n'.format(line)

    html += '</div>\n'

    if (change_flag):
        return html
    else:
        return ''


def create_html_for_line_removed_group(diff: List[str]) -> str:
    html = '<div class="singleDiff">Izbrisano sa sajta // Na sledećoj strani<br>\n'
    change_flag = False

    for line in diff:
        line = BeautifulSoup(line, "lxml").text
        if line[0:2] == '- ':
            if (line[1:].strip() != ''):
                html += '<p><span class="deletedText">' + line[1:] + '</span></p>\n'
                change_flag = True
        # else:
        #     html += '<p>{}</p>\n'.format(line)

    html += '</div>\n'

    if (change_flag):
        return html
    else:
        return ''


def create_html_for_line_added_group(diff: List[str]) -> str:
    html = '<div class="singleDiff">Dodato na sajt<br>\n'
    change_flag = False

    for line in diff:
        line = BeautifulSoup(line, "lxml").text

        if line[0:2] == '+ ':
            if (line[1:].strip() != ''):
                html += '<p><span class="newText">' + line[1:] + '</span></p>\n'
                change_flag = True
        # else:
        #     html += '<p>{}</p>\n'.format(line)

    html += '</div>\n'

    if (change_flag):
        return html
    else:
        return ''
