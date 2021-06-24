from typing import List
from pprint import pprint
import re
import logging

from . import html_generators


def filter_func(line: str) -> bool:
    # ? filter out all-whitespace lines
    if re.match(r'^\s+$', line):
        return False

    # ? filter out and --- 341, 341---
    elif re.match(r'-{3,}\s', line):
        return False

    return True


def is_separation_line(line: str) -> bool:
    # ? ********* will be caught
    if not re.match(r'\*{4,}\s*', line):
        return False
    return True


def determine_type_of_group_and_create_html_if_possible(diff: List[str], page) -> List[str]:
    """
    Known groups are:
    '!' modification of the existing line
    '-' deletion of the existing line
    '+' adding of the new line

    Diff group will contain one of these as a first character in some line
    """

    for line in diff:
        if line[0:2] == '! ':
            return html_generators.create_html_for_line_changed_group(diff)

        if (page == 1): # ignore removal if not first page
            if line[0:2] == '- ':
                return html_generators.create_html_for_line_removed_group(diff)

        if (page == 1): # ignore additions if not first page
            if line[0:2] == '+ ':
                return html_generators.create_html_for_line_added_group(diff)

    # logging.warning('Cannot determine type for current group')
    return ''


def create_html_from_diff_groups(list_of_diff_groups: List[List[str]], page) -> List[str]:
    final_html = ''

    for diff in list_of_diff_groups:
        final_html += determine_type_of_group_and_create_html_if_possible(diff, page)

    return final_html


def make_html_from_context_diff(context_diff: List[str], page):
    # ? Add another separation line to the context_diff, since there isn't any on top
    # ? separation line basically splits the diff into smaller logical pieces,
    # ? each piece between 2 separation lines needs to be processed in order to determine what exactly is
    # ? '!' represents a change, and data comes in pairs (context, new, context) similar for the old
    # ? '-' represents a deletion
    # ? there are probably some more
    context_diff.append('***************')
    indexes_of_separation_lines = []

    filtered_context_diff = list(filter(filter_func, context_diff))

    for idx, line in enumerate(filtered_context_diff):
        if is_separation_line(line):
            indexes_of_separation_lines.append(idx)

    list_of_diff_groups = []

    n = len(indexes_of_separation_lines)
    i = 0
    j = 1
    while j != n:
        # ? +2 ignores first two elementts since slices we are getting have the following structure:
        # ? ['***************\n', '*** 335,338 ****\n', '! def main():', '!      # Configure the option parser', '      usage = "usage: %prog [options] fromfile tofile"',
        # ? '! def caasdasda():', '!      # asdasdasdthe option parser', '      usage = "usage: %prog [options] fromfile tofile"']
        # ? and we dont want those

        start = indexes_of_separation_lines[i]
        end = indexes_of_separation_lines[j]

        list_of_diff_groups.append(filtered_context_diff[start + 2: end])

        i += 1
        j += 1

    generated_content = create_html_from_diff_groups(list_of_diff_groups, page)

    return generated_content


