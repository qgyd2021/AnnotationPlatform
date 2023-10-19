#!/usr/bin/python3
# -*- coding: utf-8 -*-
# https://blog.csdn.net/qq_44910516/article/details/89813355


_escape_table = [chr(x) for x in range(128)]
_escape_table[ord("/")] = "//"
_escape_table[ord("'")] = "''"
_escape_table[ord("[")] = "/["
_escape_table[ord("]")] = "/]"
_escape_table[ord("%")] = "/%"
_escape_table[ord("&")] = "/&"
_escape_table[ord("_")] = "/_"
_escape_table[ord("(")] = "/("
_escape_table[ord(")")] = "/)"


def escape_string(value, mapping=None):
    """escapes *value* without adding quote.

    Value should be unicode
    """
    return value.translate(_escape_table)


if __name__ == '__main__':
    pass
