
arg.py
Version 0.0.1
Https://GitHub.com/techeditorsrc/arg

This module for managing application arguments or custom arguments from string.

Output is dictionary:

self.arg_list={
        "args":[],
        "options":[]
        }

Items from list "args" is dictionary:
{
    "type":"item type",
    "src":"source data",
    "value":"parsed data"
}

Items from list "options" is string values what begin from "-" character

Item types can be:
    "option": where string begin from "-" character
    "list": where string converted to an array
    "data": where not matched as an "option" or a "list"

Parsing parameters is dictionary with keys:
    "case_sensetive" for values with type "option"
    "list" for values with other type from "option" can be converted to an array
    "list_by" is default character for conversion "value" to an array
    "args" is string with custom arguments, it will select for parsing if not empty


