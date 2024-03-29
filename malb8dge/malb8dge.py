from itertools import zip_longest
from typing import Any
import random
import argparse
import os
import json


os.system("")  # enables colors
RED = "\x1b[0;31m"
CYAN = "\x1b[0;36m"
GREEN = "\x1b[0;32m"
GRAY = "\x1b[0;90m"
RESET = "\x1b[0;39m"

SHELL = False
DEBUG_MODE = False

functions = []
stack = [{"type": "normal", "variables": {}}]

after_operators = (  # can't have any of these in binary_operators
    '`', '^^', '##', '#$', '_', '``', '$$', '@@', '..',  # string stuff
    '$', '\'',                                           # number stuff
)

binary_operators = (  # already sorted by operator precedence
    '#', '^',                                                      # string stuff
    '??', '@',                                                     # misc stuff
    '^*', '.*', '**', '/%', '+-', '/.', '/', '*', '-', '+', '%',   # arithmetic stuff
    '>', '<', '>>', '<<', '==', '-?', '!=', '&', '|', '&&', '||',  # logic stuff
)

unary_operators = (
    '.', '..', '`', '``',                            # string stuff
    '-', '@', '^', '^^', '#', '!', '\'', '*', '??',  # misc stuff
)

misc_combined_symbols = (
    '++', '--', '%%',
)

operators = after_operators + binary_operators + unary_operators + misc_combined_symbols


# Helper functions
def _str(x):
    if isinstance(x, bool):
        return str(x).lower()
    elif isinstance(x, list):
        return "[" + ", ".join(f'"{add_escapes(y)}"' if isinstance(y, str) else "null" if y is null else _str(y) for y in x) + "]"
    return str(x)


def add_escapes(s):
    new = ""
    for c in s:
        if c == "\n":
            new += "\\n"
        elif c == "\t":
            new += "\\t"
        elif c in "\"\\{}":
            new += "\\" + c
        else:
            new += c
    return new


def isnum(s):
    return all(c in "0123456789" for c in s) and bool(s)


def isalphanum(s):
    return all(c in "0123456789" or c.isalpha() for c in s) and bool(s)


# Helper classes
class Character:

    def __init__(self, value: str, line: int, col: int):
        self.value = value
        self.pos = line, col

    def __eq__(self, other):
        return self.value == other

    def __repr__(self):
        return f"Character(char='{self.value}', {self.pos[0]}:{self.pos[1]})"

    @staticmethod
    def from_lines(_lines, start_line=1, start_col=1):
        return [Character(char, lineno, colno)
                for lineno, line in [(a + start_line, b) for a, b in enumerate(_lines)]
                for colno, char in [(a + start_col if lineno == start_line else a + 1, b) for a, b in enumerate(line)]]

    @staticmethod
    def from_str(_str, start_line=1, start_col=1):
        return Character.from_lines(_str.split("\n"), start_line=start_line, start_col=start_col)


Character.none = Character(" ", 0, 0)


class Replace:

    def __init__(self, pairs: list[tuple[list[tuple[bool, str]], list[tuple[bool, str]]]], replace_mode: str):
        self.pairs = pairs
        self.replace_mode = replace_mode

    def __str__(self):
        return "<replace expression>"

    def __repr__(self):
        return f"""mode: '{self.replace_mode}'; pairs: \\{', '.join(': '.join(map(lambda x: f"'{''.join(f'{{{f[1]}}}' if f[0] else f[1] for f in x)}'", p)) for p in self.pairs)}\\"""


class String:

    def __init__(self, fragments: list[tuple[int, str]]):
        self.fragments = fragments

    def __repr__(self):
        return f'"{"".join(f"{{{f[1]}}}" if f[0] else add_escapes(f[1]) for f in self.fragments)}"'


class Token:

    def __init__(self, _type: str, value, pos: tuple[int, int]):
        self.type = _type
        self.value = value  # this may be changed
        self.init_value = value  # this must not be changed
        self.pos = pos

    def __eq__(self, other):
        """ Returns False if self.type == "number" """
        if self.type == "number":
            return False
        elif isinstance(other, Token):
            return self.type == other.type and self.value == other.value
        return isinstance(other, str) and self.value == other

    def is_one_of(self, others):
        return any(self == o for o in others)

    def __repr__(self):
        return f"Token(type={self.type}, {repr(self.value)} {f'({repr(self.init_value)})' if self.init_value != self.value else ''}, {self.pos[0]}:{self.pos[1]})"


Token.none = Token("", None, (0, 0))


class func:

    def __init__(self, index, arguments, defaults):
        self.index = index
        self.arguments = arguments
        self.defaults = defaults

    def __repr__(self):
        return f"<func({', '.join(('*' if d is not None else '') + a for a, d in zip(self.arguments, self.defaults))}) index={self.index}>"


class null:

    def __repr__(self):
        return ""

    def __bool__(self):
        return False


null = null()
global_var = null


class ContinueShell(Exception):
    ...


def debug(*args):
    if DEBUG_MODE:
        print(f"{CYAN}[DEBUG] {' '.join(str(a) for a in args)}{RESET}")


def run_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        lines = f.readlines()
    run(os.path.abspath(filename), lines)


def run(filename, lines):

    def print_error(msg: str, pos=None):
        nonlocal lines
        print(RED, end="")

        if SHELL:
            if pos is None:
                print(f"Error in file {filename}")

            else:
                if isinstance(pos, tuple):
                    line, col = pos
                else:
                    line, col = pos, -1

                dashes = "─" * (5 + max(30, len(lines[line - 1])))
                max_line = len(str(line))

                print(f"Error in file {filename}:{line}")
                print(f"  {'':>{max_line}} ┌" + dashes)
                print(f"> {line} │   {lines[line - 1]}")

                if col != -1:
                    print(f"  {'':>{max_line}} │   {' ' * (col - 1)}^")

                print(f"  {'':>{max_line}} └" + dashes)

            print(msg.replace("\n", "\\n"))
            print(RESET, end="")
            raise ContinueShell

        else:
            if pos is None:
                print(f"Error in file {filename}")

            else:
                lines = [_.rstrip("\n") for _ in lines]

                if isinstance(pos, tuple):
                    line, col = pos
                else:
                    line, col = pos, -1

                dashes = "─" * (5 + max(30, len(max(lines[0 if line - 1 < 1 else line - 1:line + 2], key=len))))
                max_line = len(str(line if line == len(lines) else line + 1))

                print(f"Error in file {filename}:{line}")
                print(f"  {'':>{max_line}} ┌" + dashes)

                if line == 2:
                    print(f"  {line - 1:>{max_line}} |   {lines[line - 2]}")
                elif line > 2:
                    print(f"  {'':>{max_line}} :   ...")
                    print(f"  {line - 1:>{max_line}} :   {lines[line - 2]}")

                print(f"> {line:>{max_line}} │   {lines[line - 1]}")
                if col != -1:
                    print(f"  {'':>{max_line}} │   {' ' * (col - 1)}^")

                if line == len(lines) - 1:
                    print(f"  {line + 1:>{max_line}} │   {lines[line]}")
                if line < len(lines) - 1:
                    print(f"  {line + 1:>{max_line}} :   {lines[line]}")
                    print(f"  {'':>{max_line}} :   ...")

                print(f"  {'':>{max_line}} └" + dashes)

            print(msg.replace("\n", "\\n"))
            print(RESET, end="")
            exit(1)

    try:

        # -------------------------------------------------- Lexing -------------------------------------------------- #
        def lex(chars: list[Character]) -> list:
            _tokens = []

            t = -1
            char = Character.none

            def _next():
                nonlocal t
                t += 1
                update_t()

            def prev():
                nonlocal t
                t -= 1
                update_t()

            def update_t():
                nonlocal t, char
                if t < len(chars):
                    char = chars[t]
                else:
                    char = Character.none

            def lex_identifier():
                iden = ""
                while True:
                    _next()
                    if char.value.isalpha() or (iden and isnum(char.value)):
                        iden += char.value
                    else:
                        prev()
                        _tokens.append(Token("identifier", iden, char.pos))
                        return

            def lex_replace():
                step = 0  # 0 = char mode, 1 = find pattern, 2 = replace pattern
                char_mode = False  # only used for lexing
                pattern = []
                find_pattern = []  # used to store the find pattern so that the replace pattern can be written to the pattern list
                replace_mode = ""
                value = ""  # value in this case is the value of the fragment that is currently being lexed
                fragments = []
                escape = False
                braces = 0
                start = char.pos  # used for unclosed replace EOF error
                frag_start = 0, 0  # will be set later if needed

                def finish_value():
                    nonlocal value, fragments

                    if value:
                        fragments.append((False, value))
                    if fragments:
                        pattern.append(fragments)
                    value = ""
                    fragments = []

                while t + 1 < len(chars):

                    _next()

                    # Lex char mode
                    if step == 0:
                        step = 1
                        if char == "\\":
                            char_mode = True
                            continue

                    # Escape characters handling
                    if escape:
                        if not braces and char.value in "`\\|!@{},":
                            to_add = char.value
                        else:
                            to_add = "`" + char.value

                        if char_mode:
                            for c in to_add:
                                pattern.append([(False, c)])
                        else:
                            value += to_add

                        escape = False

                    elif char == "`":
                        escape = True

                    # End replace
                    elif step == 2 and char == "\\" and not braces:
                        if replace_mode == "|" and not pattern and not fragments and not value:
                            print_error("SyntaxError: replace pattern cannot be empty with swap replace mode", char.pos)

                        finish_value()
                        if replace_mode == "|" and len(pattern) != len(find_pattern):
                            print_error("SyntaxError: different amount of values in swap patterns", char.pos)
                        elif len(pattern) > len(find_pattern):
                            print_error("SyntaxError: more replace values than find values", char.pos)

                        _tokens.append(Token("replace", Replace(list(zip_longest(
                            find_pattern,
                            pattern,
                            fillvalue=[(False, "")]
                        )), replace_mode), char.pos))
                        return

                    # End current value
                    elif not char_mode and char == "," and not braces:
                        finish_value()

                    # End first pattern and lex replace mode
                    elif step == 1 and char.value in "\\|!@" and not braces:
                        step = 2

                        if not pattern and not fragments and not value:
                            print_error("SyntaxError: find pattern in replace cannot be empty", char.pos)

                        finish_value()
                        find_pattern = pattern
                        pattern = []
                        replace_mode = char.value

                    # Continue replace
                    else:
                        if char == "{" and not escape and not char_mode:
                            if not braces:
                                if value:
                                    fragments.append((False, value))
                                    value = ""
                                frag_start = chars[t + 1].pos
                            else:
                                value += "{"
                            braces += 1

                        elif char == "}" and not escape and not char_mode:
                            if braces:
                                braces -= 1
                                if not braces:
                                    fragments.append((True, value, frag_start))
                                    value = ""
                                else:
                                    value += "}"
                            else:
                                # print_error("SyntaxError: unescaped '}' in replace", char.pos)
                                value += "}"

                        else:
                            if char_mode:
                                pattern.append([(False, char.value)])  # append value with a single fragment
                            else:
                                value += char.value

                else:
                    print_error("SyntaxError: unclosed replace", start)

            def lex_string():
                value = ""
                fragments = []
                escape = False
                braces = 0
                start = char.pos  # used for unclosed string EOF error
                frag_start = 0, 0  # will be set later if needed

                while t + 1 < len(chars):

                    _next()

                    # Escape characters handling
                    if escape:
                        if not braces:
                            if char == "n":
                                value += "\n"
                            elif char == "t":
                                value += "\t"
                            elif char.value in "\"\\{}":
                                value += char.value
                            else:
                                value += "\\" + char.value
                        else:
                            value += "\\" + char.value
                        escape = False

                    elif char == "\\":
                        escape = True

                    # End string
                    elif char == "\"" and not braces:
                        fragments.append((False, value))
                        _tokens.append(Token("string", String(fragments), char.pos))
                        return

                    # Continue string
                    else:
                        if char == "{" and not escape:
                            if not braces:
                                fragments.append((False, value))
                                value = ""
                                frag_start = chars[t + 1].pos
                            else:
                                value += "{"
                            braces += 1

                        elif char == "}" and not escape:
                            if braces:
                                braces -= 1
                                if not braces:
                                    fragments.append((True, value, frag_start))
                                    value = ""
                                else:
                                    value += "}"
                            else:
                                # print_error("SyntaxError: unescaped '}' in string", char.pos)
                                value += "}"

                        else:
                            value += char.value

                else:
                    print_error("SyntaxError: unclosed string", start)

            def lex_number():
                value = ""
                floating_point = False

                def add_number_token():
                    if floating_point:
                        _tokens.append(Token("number", float(value), char.pos))
                    else:
                        _tokens.append(Token("number", int(value), char.pos))

                while t + 1 < len(chars):

                    _next()

                    # Floating-point number handling
                    if char == "." and not floating_point_override:

                        # Double point
                        if floating_point:
                            print_error("SyntaxError: more than one decimal point in number", char.pos)

                        else:
                            floating_point = True
                            value += char.value
                            continue

                    # End number
                    elif not isnum(char.value):
                        prev()

                        if value[-1] == ".":
                            prev()
                            floating_point = False
                            value = value[:-1]

                        add_number_token()
                        return

                    # Continue number
                    else:
                        value += char.value

                else:
                    add_number_token()
                    return

            def lex_symbol():
                nonlocal floating_point_override

                symbol = ""
                while True:
                    _next()
                    if (
                        # make sure it's not a space because that splits symbols
                        char.value != " " and (
                            # continue the symbol if it's either...
                            # - the first character in the symbol
                            not symbol
                            # - or it's a combined symbol that exists in the operators list
                            or symbol + char.value in operators
                            # - or the current symbol is a binary or after operator and the character is an equals sign (augmented assignment)
                            or (symbol in binary_operators + after_operators and char == '=')
                        )
                    ):
                        symbol += char.value

                    elif symbol + char.value == "###":  # comment
                        while char != "\n" and t < len(chars):
                            _next()
                        prev()
                        return

                    else:
                        prev()
                        floating_point_override = symbol == "."

                        _tokens.append(Token("symbol", symbol, char.pos))
                        return

            floating_point_override = False

            while t + 1 < len(chars):
                _next()

                # Identifier
                if char.value.isalpha():
                    prev()
                    lex_identifier()

                # Replace
                elif char == "\\":
                    lex_replace()

                # String
                elif char == "\"":
                    lex_string()

                # Number
                elif isnum(char.value):
                    prev()
                    lex_number()

                # Stop using tabs for indentation!
                elif char == "\t":
                    print_error("SyntaxError: stop using tabs for indentation!", char.pos)

                # Symbol
                elif char != " ":
                    prev()
                    lex_symbol()

            return _tokens

        lexed_tokens = lex(Character.from_lines([lines[-1]], start_line=len(lines)) if SHELL else Character.from_lines(lines))

        # Debugging information
        if DEBUG_MODE and not SHELL:
            with open(f"{filename}-tokens.txt", "w", encoding="utf-8") as f:
                f.write("\n".join([f"{_.type:>20} | {_.pos[0]:>2}:{_.pos[1]:<3} | {repr(_.value)}" for _ in lexed_tokens]))

        # -------------------------------------------------- Parsing ------------------------------------------------- #
        def parse(tokens: list[Token]) -> list[dict]:
            statements = []

            t = -1
            token = Token.none

            class BracketManager:

                def __init__(self, bm=None, bracket='', *separators):
                    """
                    Put stuff in seperators if you want them to do something
                    else in the current scope other than just ending it

                    Create new BracketManager if you are adding a bracket,
                    else get current bm and use bm.add(*separators)
                    """
                    self.in_func = bm.in_func if bm is not None else False
                    self.in_loop = bm.in_loop if bm is not None else False

                    self.bracket = bracket
                    self.bracket_pos = token.pos
                    self.sep = separators

                def add(self, *s):
                    """
                    Call bm.add() when there is still parsing to do before returning
                    """
                    if s:
                        return BracketManager(self, self.bracket, *self.sep, *s)
                    else:
                        return BracketManager(self, self.bracket, *self.sep, '')

                def func(self):
                    self.in_func = True
                    return self

                def loop(self):
                    self.in_loop = True
                    return self

                def is_closing(self):
                    if token == self.bracket:
                        if self.sep:  # when unclosed scopes before opening bracket
                            prev()
                        return True

                    elif token.is_one_of(self.sep):  # symbols used for other reasons in outer scopes
                        prev()
                        return True

                    elif not self.bracket and token == '\n':
                        prev()
                        return True

                    return False

            def _next():
                nonlocal t
                t += 1
                update_t()

            def prev():
                nonlocal t
                t -= 1
                update_t()

            def update_t():
                nonlocal t, token
                if t < len(tokens):
                    token = tokens[t]
                else:
                    token = Token.none

            def add_ast_pos(fn):
                """
                Manually call ``set_ast_pos(dict)`` in:

                * loops
                * dictionaries that aren't immediately returned
                * manually created nested dictionaries
                """

                def inner(*args, **kwargs):
                    ret = fn(*args, **kwargs)
                    set_ast_pos(ret)
                    return ret

                return inner

            def set_ast_pos(d: dict):
                if isinstance(d, dict) and "pos" not in d:
                    d["pos"] = (token if t < len(tokens) else tokens[-1]).pos

            def ungroup(v: dict):
                return v["inner"] if v.get("type") == "group" else v

            @add_ast_pos
            def parse_statement(bm) -> dict:
                _next()

                statement = {}

                if token.is_one_of(('<', '%', '>', '%%')):
                    if token == '<':
                        if bm.in_func:
                            statement = {
                                "type": "keyword",
                                "name": "return",
                                "value": parse_expression(bm, optional=True)
                            }
                        else:
                            print_error("SyntaxError: return statement not in function", token.pos)

                    elif token == '%':
                        if bm.in_loop:
                            statement = {
                                "type": "keyword",
                                "name": "break",
                                "value": parse_expression(bm, optional=True)
                            }
                        else:
                            print_error("SyntaxError: break not in loop", token.pos)

                    elif token == '>':
                        if bm.in_loop:
                            statement = {
                                "type": "keyword",
                                "name": "continue",
                                "value": parse_expression(bm, optional=True)
                            }
                        else:
                            print_error("SyntaxError: continue not in loop", token.pos)

                    elif token == '%%':
                        _next()
                        temp = token
                        prev()

                        statement = {
                            "type": "keyword",
                            "name": "exit",
                            "msg": {} if temp == ';' else parse_expression(bm, optional=True)
                        }

                elif token != '\n':
                    prev()
                    statement = parse_expression(bm)

                else:
                    return statement

                _next()
                if token == ';':
                    prev()
                elif not bm.is_closing() and token != Token.none:
                    print_error(f"SyntaxError: expected end of statement, found '{token.init_value}'", token.pos)

                return statement

            @add_ast_pos
            def parse_list(bm, existing_expr=None, unpack=False) -> dict:
                values = [] if existing_expr is None else [existing_expr]
                sep = (',', '=') if unpack else (',',)

                while t + 1 < len(tokens):
                    _next()

                    # check for closing things
                    if bm.is_closing():
                        return {
                            "type": "list",
                            "values": values
                        }

                    elif token == '\n':
                        continue  # try again until there is a value

                    # start with first expression
                    elif not values:
                        prev()
                        values.append(parse_expression(bm.add(*sep)))

                    elif token == ',':
                        values.append(parse_expression(bm.add(*sep)))

                    # unpacking
                    elif token == '=' and unpack:
                        for v in values:
                            if v.get("type") not in ("get", "index"):
                                print_error("SyntaxError: invalid target for assignment", tokens[t - 1].pos)

                        expr = parse_expression(bm)
                        if len(values) == 1:
                            expr = [expr]

                        return {
                            "type": "set multiple",
                            "targets": values,
                            "values": expr
                        }

                    else:
                        print_error(f"SyntaxError: expected a comma or a newline, found '{token.init_value}'", token.pos)

                else:
                    if bm.bracket:
                        print_error(f"SyntaxError: missing '{bm.bracket}'", bm.bracket_pos)

                    else:
                        return {
                            "type": "list",
                            "values": values
                        }

            @add_ast_pos
            def parse_expression(bm, optional=False) -> dict:
                expr = {}

                while t + 1 < len(tokens):
                    _next()

                    # ignore newlines in brackets
                    if token == '\n' and bm.bracket:
                        continue

                    # start with first value
                    elif not expr:
                        prev()
                        expr = parse_value(bm.add(), optional=optional)
                        if optional and not expr.get("type"):
                            return expr

                    # check for closing things
                    elif bm.is_closing():
                        return expr

                    # unparenthesized list
                    elif token == ',':
                        prev()
                        expr = parse_list(bm.add(), existing_expr=expr, unpack=True)

                    # loop
                    elif token == '~':
                        expr = parse_loop(bm.add(), expr)

                    # if statement:
                    elif token.is_one_of(('?', '!')):
                        expr = parse_if(bm.add(), expr)

                    # binary operators
                    elif token.is_one_of(binary_operators):
                        _expr = expr

                        # operator precedence
                        while (
                                _expr["type"] == "binary operator"
                                and binary_operators.index(token.value) < binary_operators.index(_expr["operator"])
                                and "fixed" not in _expr
                        ):
                            _expr = _expr["b"]

                        inner = _expr.copy()
                        _expr.clear()
                        _expr.update({
                            "type": "binary operator",
                            "operator": token.value,
                            "a": inner,
                            "b": parse_value(bm.add())
                        })
                        set_ast_pos(_expr)

                    # normal assignment
                    elif token == '=':
                        expr = ungroup(expr)

                        if expr.get("type") == "get":
                            expr = {
                                "type": "set",
                                "id": expr["id"],
                                "args": parse_expression(bm.add())
                            }

                        elif expr.get("type") == "index":
                            expr = {
                                "type": "set index",
                                "target": expr["target"],
                                "index": expr["index"],
                                "args": parse_expression(bm.add())
                            }

                        elif expr.get("type") == "list":
                            for v in expr["values"]:
                                if v.get("type") not in ("get", "index"):
                                    print_error("SyntaxError: invalid target for assignment", tokens[t - 1].pos)

                            expr = {
                                "type": "set multiple",
                                "targets": expr["values"],
                                "values": parse_expression(bm.add())
                            }

                        else:
                            print_error("SyntaxError: invalid target for assignment", tokens[t - 1].pos)

                        set_ast_pos(expr)

                    # augmented assignment
                    elif token.type == 'symbol' and token.value[:-1] in binary_operators and token.value[-1] == '=':
                        inner = {
                            "type": "binary operator",
                            "operator": token.value[:-1],
                            "a": expr,
                            "b": parse_expression(bm.add())
                        }

                        if expr.get("type") == "get":
                            expr = {
                                "type": "set",
                                "id": expr["id"],
                                "args": inner
                            }

                        elif expr.get("type") == "index":
                            expr = {
                                "type": "set index",
                                "target": expr["target"],
                                "index": expr["index"],
                                "args": inner
                            }

                        else:
                            print_error("SyntaxError: invalid target for augmented assignment", tokens[t - 1].pos)

                        set_ast_pos(expr["args"])

                    elif token.value == ';' and not bm.bracket:
                        # run through loop again but treat it as a newline to end statement
                        token.value = '\n'
                        prev()

                    else:
                        print_error(f"SyntaxError: expected an operator or {'a closing bracket' if bm.bracket else 'a newline'}, found '{token.init_value}'", token.pos)

                else:
                    if bm.bracket:
                        print_error(f"SyntaxError: missing '{bm.bracket}'", bm.bracket_pos)

                    elif not expr and not optional:
                        print_error(f"SyntaxError: expected an expression", (token.pos[0], token.pos[1] + 1))

                    else:
                        return expr

            @add_ast_pos
            def parse_group(bm) -> dict:
                _next()

                if bm.is_closing():
                    return {
                        "type": "list",
                        "values": []
                    }

                else:
                    prev()
                    inner = parse_list(bm)
                    if len(inner["values"]) == 1:
                        return {
                            "type": "group",
                            "inner": inner["values"][0]
                        }
                    return inner

            @add_ast_pos
            def parse_value(bm, optional=False, mult_shortcut=False) -> dict:
                _next()

                value = {}

                if mult_shortcut and not (
                    token == '(' or
                    token.type == "string" or
                    (token.type == "identifier" and not token.is_one_of(("true", "false", "null")))
                ):
                    prev()
                    return value

                temp = token
                if bm.is_closing():
                    if temp == '!':
                        _next()
                    else:
                        if not optional:
                            print_error("SyntaxError: expected a value", token.pos)
                        return value

                if token == '\n':
                    value = parse_value(bm.add())  # try again until there is a value

                elif token == '(':
                    value = parse_group(BracketManager(bm, ')'))

                elif token == '[':
                    value = parse_list(BracketManager(bm, ']'))

                elif token == '{':
                    prev()
                    value = {
                        "type": "block",
                        "statements": parse_block(bm.add())
                    }

                elif token == '?':
                    block = parse_block(bm.add().loop(), needs_colon=False, allow_sum_loop=True)
                    value = {
                        "type": "while loop",
                        "condition": {
                            "type": "keyword",
                            "name": "true"
                        },
                        "statements": block[0],
                        "sum": block[1]
                    }

                elif token.type == "string":
                    value = {
                        "type": "string",
                        "fragments": [parse_fragment(frag) for frag in token.value.fragments]
                    }

                elif token.type == "number":
                    temp = token.value
                    if isinstance(token.value, (int, float)) and (v := parse_value(bm.add(), optional=True, mult_shortcut=True)).get("type"):
                        value = {
                            "type": "binary operator",
                            "operator": '*',
                            "a": {
                                "type": "number",
                                "value": temp
                            },
                            "b": v,
                            "fixed": True
                        }

                    else:
                        value = {
                            "type": "number",
                            "value": token.value
                        }

                elif token.type == "identifier":
                    if token.is_one_of(("true", "false", "null")):
                        value = {
                            "type": "keyword",
                            "name": token.value
                        }

                    else:
                        value = {
                            "type": "get",
                            "id": token.value
                        }

                elif token == '&':
                    value = {
                        "type": "ref"
                    }

                elif token == '~':
                    value = {
                        "type": "loop ref"
                    }

                elif token.is_one_of((';', '/', '|')):
                    value = {
                        "type": "print",
                        "mode": {
                            ";": "normal",
                            "/": "spaces",
                            "|": "no newline"
                        }[token.value],
                        "args": parse_expression(bm.add(), optional=True)
                    }

                elif token.is_one_of(('_', '$', '#$')):
                    value = {
                        "type": "input",
                        "mode": {
                            "_": "string",
                            "$": "number",
                            "#$": "split number"
                        }[token.value],
                        "prompt": {}
                    }

                elif token.is_one_of(('++', '--')):
                    mode = "add" if token == '++' else "subtract"

                    v = parse_value(bm.add())
                    if v["type"] not in ("get", "ref"):
                        print_error(f"SyntaxError: can only use {'increment' if token == '++' else 'decrement'} operator on variables", token.pos)

                    value = {
                        "type": "increment",
                        "target": v,
                        "mode": mode,
                        "position": "before"
                    }

                elif token == ':':  # function with no arguments
                    value = parse_function(bm.add(), {"type": "list", "values": []})

                elif token.is_one_of(unary_operators):
                    value = {
                        "type": "unary operator",
                        "operator": token.value,
                        "target": parse_value(bm.add())
                    }

                elif not optional:
                    if token == Token.none:
                        print_error("SyntaxError: expected a value", (tokens[t - 1].pos[0], tokens[t - 1].pos[1] + 1))

                    else:
                        print_error(f"SyntaxError: expected a value, found '{token.init_value}'", token.pos)

                else:
                    prev()
                    return value

                if mult_shortcut:
                    return value

                set_ast_pos(value)

                while t + 1 < len(tokens):
                    _next()

                    if bm.is_closing():
                        return value

                    elif token == '(':
                        if value["type"] == "input" and not value["prompt"]:
                            value["prompt"] = parse_expression(BracketManager(bm, ')'))

                        else:
                            value = {
                                "type": "call",
                                "target": value,
                                "args": parse_list(BracketManager(bm, ')'))
                            }

                    elif token == '[':
                        value = parse_index(BracketManager(bm, ']'), value)

                    elif token == '.':
                        value = {
                            "type": "index",
                            "target": value,
                            "index": parse_value(bm.add('.'))
                        }

                    elif token == '{':
                        value = parse_brace_syntax(BracketManager(bm, '}'), value)

                    elif token == ':':
                        value = parse_function(bm.add(), value)

                    elif token.is_one_of(after_operators):
                        value = {
                            "type": "after operator",
                            "operator": token.value,
                            "target": value
                        }

                    elif token.is_one_of(('++', '--')):
                        if value["type"] not in ("get", "ref"):
                            print_error(f"SyntaxError: can only use {'increment' if token == '++' else 'decrement'} operator on variables", token.pos)

                        value = {
                            "type": "increment",
                            "target": value,
                            "mode": "add" if token == '++' else "subtract",
                            "position": "after"
                        }

                    elif token.type == "replace":
                        value = parse_replace(value)

                    elif token.value == ';' and not bm.bracket:
                        # run through loop again but treat it as a newline to end statement
                        token.value = '\n'
                        prev()

                    else:
                        prev()
                        return value

                    set_ast_pos(value)

                else:
                    return value

            def parse_fragment(frag: tuple[bool, str]) -> list[dict]:
                return parse(lex(Character.from_str(frag[1], start_line=frag[2][0], start_col=frag[2][1]))) if frag[0] else frag[1]

            def parse_index(bm, value) -> dict:  # index, index of, slice
                pos = 0
                isslice = False
                values = [None, None, None]

                first = True  # used to check for index of
                colon_before = False  # used to check if can add index

                while t + 1 < len(tokens):
                    _next()

                    # check for closing ]
                    if token == ']':
                        if isslice:
                            return {
                                "type": "slice",
                                "target": value,
                                "values": values
                            }

                        else:
                            if values[0] is None:
                                print_error(f"SyntaxError: expected a value", token.pos)
                            return {
                                "type": "index",
                                "target": value,
                                "index": values[0]
                            }

                    elif first and token == '+':  # [+expr] - count
                        return {
                            "type": "count",
                            "target": value,
                            "value": parse_expression(BracketManager(bm, ']'))
                        }

                    elif first and token.is_one_of(('?', '!')):  # [?expr] - contains
                        return {
                            "type": "contains",
                            "not": token == '!',
                            "target": value,
                            "value": parse_expression(BracketManager(bm, ']'))
                        }

                    elif first and token == '@':  # [@expr] - index of
                        return {
                            "type": "index of",
                            "target": value,
                            "value": parse_expression(BracketManager(bm, ']'))
                        }

                    elif token == ':':
                        isslice = True
                        pos += 1

                    elif pos == 0 or colon_before:  # first value or after :
                        prev()
                        values[pos] = parse_expression(BracketManager(bm, ']', ':'))

                    else:
                        print("what the heck!!!")
                        exit(25893589)

                    if pos > 2:
                        print_error("SyntaxError: slice expected at most 3 values", token.pos)

                    first = False
                    colon_before = token == ':'

                else:
                    print_error("SyntaxError: missing ']'", bm.bracket_pos)

            def parse_replace(value) -> dict:
                return {
                    "type": "replace",
                    "target": value,
                    "mode": {"\\": "normal", "|": "swap", "!": "first", "@": "last"}[token.value.replace_mode],
                    "pairs": list(zip(
                        [[parse_fragment(f1) for f1 in p[0]] for p in token.value.pairs],
                        [[parse_fragment(f2) for f2 in p[1]] for p in token.value.pairs],
                    ))
                }

            @add_ast_pos
            def parse_function(bm, args) -> dict:
                args = ungroup(args)
                defaults = []

                if args.get("type") == "get":
                    defaults.append(None)
                    args = [args["id"]]

                elif args.get("type") == "set":
                    defaults.append(args["args"])
                    args = [args["id"]]

                elif args.get("type") == "list":
                    args["values"] = [ungroup(a) for a in args["values"]]
                    for a in args["values"]:
                        if a.get("type") not in ("get", "set"):
                            print_error("SyntaxError: invalid argument declaration", token.pos)

                    defaults += [a["args"] if a["type"] == "set" else None for a in args["values"]]
                    args = [a["id"] for a in args["values"]]

                else:
                    print_error("SyntaxError: invalid argument declaration", token.pos)

                bm.in_func = True
                bm.in_loop = False
                functions.append(parse_block(bm, needs_colon=False))

                return {
                    "type": "function",
                    "arguments": args,
                    "defaults": defaults,
                    "index": len(functions) - 1  # index of this function in the functions list
                }

            @add_ast_pos
            def parse_loop(bm, expr) -> dict:
                bm.in_loop = True

                _next()

                if token == '?':
                    block = parse_block(bm, needs_colon=False, allow_sum_loop=True)
                    return {
                        "type": "while loop",
                        "condition": expr,
                        "statements": block[0],
                        "sum": block[1]
                    }

                elif token.is_one_of((':', '+', '{', '[')):
                    prev()
                    block = parse_block(bm, allow_sum_loop=True)
                    return {
                        "type": "for loop",
                        "list": expr,
                        "vars": None,
                        "statements": block[0],
                        "sum": block[1]
                    }

                else:
                    prev()
                    var = ungroup(parse_expression(bm.add(':', '+', '{', '[')))
                    if var.get("type") == "list":
                        for v in var["values"]:
                            if v.get("type") != "get":
                                print_error("SyntaxError: invalid target for assignment", token.pos)

                    elif var.get("type") != "get":
                        print_error("SyntaxError: invalid target for assignment", token.pos)

                    block = parse_block(bm, allow_sum_loop=True)
                    return {
                        "type": "for loop",
                        "list": expr,
                        "vars": var,
                        "statements": block[0],
                        "sum": block[1]
                    }

            @add_ast_pos
            def parse_if(bm, condition) -> dict:
                invert = token == '!'

                on_true = parse_block(bm.add('!'), needs_colon=False)
                on_false = None

                _next()

                if token == '!':
                    on_false = parse_block(bm, needs_colon=False)
                else:
                    prev()

                return {
                    "type": "if",
                    "condition": condition,
                    "invert": invert,
                    "true": on_true,
                    "false": on_false
                }

            def parse_block(bm, needs_colon=True, allow_sum_loop=False) -> list[dict]:
                _next()

                if token == ':' or (allow_sum_loop and token == '+'):
                    sum_loop = token == '+'
                    statement = parse_statement(bm)
                    if statement.get("type"):
                        return ([statement], sum_loop) if allow_sum_loop else [statement]
                    else:
                        print_error("SyntaxError: expected statement", token.pos)

                elif token == '{' or (allow_sum_loop and token == '['):
                    stmts = []
                    bracket_pos = token.pos
                    sum_loop = token == '['
                    closing = ']' if sum_loop else '}'

                    while t + 1 < len(tokens):
                        _next()

                        if token == closing:
                            return (stmts, sum_loop) if allow_sum_loop else stmts
                        else:
                            prev()
                            statement = parse_statement(BracketManager(bm, '', closing))
                            if statement.get("type"):
                                stmts.append(statement)

                    else:
                        print_error(f"SyntaxError: missing '{closing}'", bracket_pos)

                elif not needs_colon:
                    prev()
                    statement = parse_statement(bm)
                    if statement.get("type"):
                        return ([statement], False) if allow_sum_loop else [statement]
                    else:
                        print_error("SyntaxError: expected statement", token.pos)

                else:
                    if token == Token.none:
                        print_error(f"SyntaxError: expected statement block", (tokens[t - 1].pos[0], tokens[t - 1].pos[1] + 1))
                    print_error(f"SyntaxError: expected ':', '+', '[' or '{{', found '{token.init_value}'", token.pos)

            @add_ast_pos
            def parse_brace_syntax(bm, value) -> dict:
                _next()

                if token.is_one_of(('+', '-', '*', '/', '/.', '&', '|', '&&', '||', '=', '!', '<', '>', '.', '^', '#')):
                    op = token.value

                    _next()

                    if bm.is_closing():
                        key = None

                    else:
                        prev()
                        key = parse_expression(bm)

                    return {
                        "type": "brace syntax",
                        "op": op,
                        "target": value,
                        "key": key
                    }

                elif bm.is_closing() or token == Token.none:
                    print_error(f"SyntaxError: expected mode specifier", (tokens[-1] if token == Token.none else token).pos)

                else:
                    print_error(f"SyntaxError: unknown mode '{token.init_value}'", token.pos)

            while t + 1 < len(tokens):
                if (stmt := parse_statement(BracketManager())).get("type"):
                    statements.append(stmt)

            return statements

        ast: dict = {
            "statements": parse(lexed_tokens)
        }

        # Debugging information
        if DEBUG_MODE and not SHELL:
            with open(f"{filename}-ast.json", "w") as f:
                json.dump(ast, f, indent=2)
            with open(f"{filename}-functions.json", "w") as f:
                json.dump(dict(enumerate(functions)), f, indent=2)

        # -------------------------------------------------- Running ------------------------------------------------- #
        _continue = None
        _break = None
        _return = None

        def run_recursive(inner, default_return_value: Any = null, try_no_paren_call=False):
            global global_var
            nonlocal _continue, _break, _return

            # Helper functions
            def to_num(n):
                if isinstance(n, (int, float)):
                    return n
                elif n is null:
                    return 0
                try:
                    n = int(n)
                except ValueError:
                    try:
                        n = float(n)
                    except ValueError:
                        print_error(f"ValueError: cannot convert '{n}' to number", inner["pos"])
                return n

            def run_binary_operator(a, operator, b):

                # Join operator
                if operator == '^':
                    if isinstance(b, str):
                        if isinstance(a, list):
                            return b.join(map(_str, a))
                        elif isinstance(a, str):
                            return b.join(a)
                        else:
                            print_error(f"TypeError: cannot use join on type '{a.__class__.__name__}'", inner["pos"])
                    else:
                        print_error(f"TypeError: cannot use type '{b.__class__.__name__}' on right side of join operator", inner["pos"])

                # Split operator
                elif operator == '#':
                    if isinstance(a, str):
                        if isinstance(b, str):
                            if not b:
                                return list(a)
                            return a.split(b)
                        else:
                            print_error(f"TypeError: cannot use type '{b.__class__.__name__}' as a delimiter for split", inner["pos"])
                    else:
                        print_error(f"TypeError: cannot split type '{a.__class__.__name__}'", inner["pos"])

                # Random integer operator
                elif operator == '??':
                    if isinstance(a, int):
                        if isinstance(b, int):
                            return random.randint(a, b)
                        else:
                            print_error(f"TypeError: cannot use binary random operator with type '{b.__class__.__name__}'", inner["pos"])
                    else:
                        print_error(f"TypeError: cannot use binary random operator with type '{a.__class__.__name__}'", inner["pos"])

                # Convert to and from base
                elif operator == '@':
                    if isinstance(b, int):
                        if b > 36 or b < 2:
                            print_error(f"ValueError: base must be <= 36 and >= 2, found {b}", inner["pos"])

                        # int a to str in base b
                        if isinstance(a, int):
                            result = ""
                            while a:
                                result += "0123456789abcdefghijklmnopqrstuvwxyz"[a % b]
                                a //= b
                            return result[::-1] or "0"

                        # str a in base b to int
                        elif isinstance(a, str):
                            try:
                                return int(a, b)
                            except ValueError:
                                print_error(f"TypeError: cannot interpret '{a}' as a base {b} int", inner["pos"])

                        else:
                            print_error(f"TypeError: cannot convert type '{a.__class__.__name__}' to base {b} int", inner["pos"])

                    else:
                        print_error(f"TypeError: cannot use type '{b.__class__.__name__}' for base conversion", inner["pos"])

                # Power operator
                elif operator == '**':
                    if isinstance(a, (int, float)):
                        if isinstance(b, (int, float)):
                            return to_num(a ** b)
                        else:
                            print_error(f"TypeError: cannot use type '{b.__class__.__name__}' in exponent", inner["pos"])
                    else:
                        print_error(f"TypeError: cannot raise type '{a.__class__.__name__}' to a power", inner["pos"])

                elif operator == '/%':
                    try:
                        if isinstance(a, (float, int)):
                            if isinstance(b, (float, int)):
                                return [to_num(a // b), to_num(a % b)]
                            else:
                                print_error(f"TypeError: cannot divide type '{a.__class__.__name__}' by type '{b.__class__.__name__}'", inner["pos"])
                        else:
                            print_error(f"TypeError: cannot divide type '{a.__class__.__name__}'", inner["pos"])
                    except ZeroDivisionError:
                        print_error(f"MathError: cannot divide by zero", inner["pos"])

                elif operator == '+-':
                    if isinstance(a, (float, int)) and isinstance(b, (float, int)):
                        return [to_num(a + b), to_num(a - b)]
                    else:
                        print_error(f"TypeError: cannot use +- operator on types '{a.__class__.__name__}' and '{b.__class__.__name__}'", inner["pos"])

                elif operator in ('/', '/.'):
                    try:
                        if isinstance(a, (float, int)):
                            if isinstance(b, (float, int)):
                                return to_num(a / b if operator == '/' else a // b)
                            else:
                                print_error(f"TypeError: cannot divide type '{a.__class__.__name__}' by type '{b.__class__.__name__}'", inner["pos"])
                        else:
                            print_error(f"TypeError: cannot divide type '{a.__class__.__name__}'", inner["pos"])
                    except ZeroDivisionError:
                        print_error(f"MathError: cannot divide by zero", inner["pos"])

                elif operator == '*':
                    if isinstance(a, float):
                        if isinstance(b, (float, int)):
                            return to_num(a * b)
                        else:
                            print_error(f"TypeError: cannot multiply type '{a.__class__.__name__}' by type '{b.__class__.__name__}'", inner["pos"])
                    elif isinstance(a, int):
                        if isinstance(b, (float, int)):
                            return to_num(a * b)
                        elif isinstance(b, (str, list)):
                            return a * b
                        else:
                            print_error(f"TypeError: cannot multiply type '{a.__class__.__name__}' by type '{b.__class__.__name__}'", inner["pos"])
                    elif isinstance(a, (str, list)):
                        if isinstance(b, int):
                            return a * b
                        else:
                            print_error(f"TypeError: cannot multiply type '{a.__class__.__name__}' by type '{b.__class__.__name__}'", inner["pos"])
                    else:
                        print_error(f"TypeError: cannot multiply type '{a.__class__.__name__}'", inner["pos"])

                elif operator == '-':
                    if isinstance(a, (float, int)):
                        if isinstance(b, (float, int)):
                            return to_num(a - b)
                        else:
                            print_error(f"TypeError: cannot subtract type '{b.__class__.__name__}' from type '{a.__class__.__name__}'", inner["pos"])
                    elif isinstance(a, str):
                        if isinstance(b, str):
                            if len(a) != 1 or len(b) != 1:
                                print_error(f"ValueError: expected strings with 1 character each, found {len(a)} and {len(b)} characters", inner["pos"])
                            return "".join(chr(c) for c in range(ord(a), ord(b) + 1))
                        else:
                            print_error(f"TypeError: cannot subtract type '{b.__class__.__name__}' from type '{a.__class__.__name__}'", inner["pos"])
                    else:
                        print_error(f"TypeError: cannot subtract from type '{a.__class__.__name__}'", inner["pos"])

                elif operator == '+':
                    if isinstance(a, (float, int)):
                        if isinstance(b, (float, int)):
                            return to_num(a + b)
                        elif isinstance(b, str):
                            return _str(a) + b
                        else:
                            print_error(f"TypeError: cannot add type '{b.__class__.__name__}' to type '{a.__class__.__name__}'", inner["pos"])
                    elif isinstance(a, str):
                        if isinstance(b, list):
                            return a + "".join(map(_str, b))
                        else:
                            return a + _str(b)
                    elif isinstance(a, list):
                        if isinstance(b, list):
                            return a + b
                        else:
                            return a + [b]
                    else:
                        print_error(f"TypeError: cannot add to type '{a.__class__.__name__}'", inner["pos"])

                elif operator == '%':
                    try:
                        if isinstance(a, (float, int)):
                            if isinstance(b, (float, int)):
                                return to_num(a % b)
                            else:
                                print_error(f"TypeError: cannot modulo type '{a.__class__.__name__}' by type '{b.__class__.__name__}'", inner["pos"])
                        else:
                            print_error(f"TypeError: cannot use modulo on type '{a.__class__.__name__}'", inner["pos"])
                    except ZeroDivisionError:
                        print_error(f"MathError: cannot modulo by zero", inner["pos"])

                elif operator == '^*':
                    return max(a, b)

                elif operator == '.*':
                    return min(a, b)

                elif operator in ('>', '<', '>>', '<<'):
                    try:
                        if operator == '>':
                            return a > b
                        elif operator == '<':
                            return a < b
                        elif operator == '>>':
                            return a >= b
                        elif operator == '<<':
                            return a <= b
                    except TypeError:
                        print_error(f"TypeError: cannot compare type '{a.__class__.__name__}' with type '{b.__class__.__name__}'", inner["pos"])

                elif operator == '==':
                    return a == b

                elif operator == '-?':
                    return 1 if a == b else -1

                elif operator == '!=':
                    return a != b

                elif operator == '&':
                    return a and b

                elif operator == '|':
                    return a or b

                elif operator == '&&':
                    return bool(a and b)

                elif operator == '||':
                    return bool(a or b)

            def run_function_call(_target, _args):
                nonlocal _return

                if not isinstance(_target, func):
                    print_error(f"TypeError: type '{_target.__class__.__name__}' is not callable", inner["pos"])
                elif not _target.arguments and len(_args):
                    print_error(f"ArgumentError: function expected no arguments", inner["pos"])

                elif len(_args) > len(_target.arguments):
                    # *args type thing
                    _args = _args[:len(_target.arguments) - 1] + [_args[len(_target.arguments) - 1:]]

                append_stack("function")
                for n, a in enumerate(_target.arguments):
                    if n >= len(_args):
                        val = _target.defaults[n]
                        if val is None:
                            print_error(f"ArgumentError: argument '{a}' is required", inner["pos"])
                        val = run_recursive(val)
                    else:
                        val = _args[n]
                    set_variable(a, val, force_inner=True)

                _ret: Any = run_recursive(functions[_target.index])
                stack.pop()

                if _return is not None:
                    _r = _return
                    _return = None
                    return _r
                return _ret[-1] if _ret else null

            def concatenate_fragments(fragments: list):
                c = ""
                for frag in fragments:
                    if isinstance(frag, str):
                        c += frag
                    elif val := run_recursive(frag):
                        c += add_escapes(_str(val[-1]))
                return c

            def append_stack(_type):
                stack.append({"type": _type, "variables": {}})

            def get_variable(varname):
                for st in reversed(stack):
                    if varname in st["variables"]:
                        return st["variables"][varname]
                    if st["type"] == "function":
                        for _st in stack:
                            if _st["type"] == "function":
                                break
                            if varname in _st["variables"]:
                                return _st["variables"][varname]
                        break

                print_error(f"UndefinedError: variable '{varname}' is not defined", inner["pos"])

            def set_variable(varname, new_value, force_inner=False):
                st = stack[0]
                if force_inner:
                    st = stack[-1]

                elif varname not in stack[0]["variables"]:
                    for st in reversed(stack):
                        if varname in st["variables"] or st["type"] != "for loop":
                            break

                st["variables"][varname] = new_value
                return new_value

            if isinstance(inner, list):
                ret = []

                for i in range(len(inner)):
                    r = run_recursive(inner[i], try_no_paren_call=True)

                    if _return is not None or _break is not None or _continue is not None:
                        break

                    ret.append(r)

                return ret

            elif inner is None or not inner.get("type"):
                return default_return_value

            # Input statements
            elif inner["type"] == "input":
                mode = inner["mode"]
                prompt = run_recursive(inner["prompt"])
                prompt = "" if prompt is null else _str(prompt)

                if SHELL:
                    prompt = GREEN + prompt + RESET

                _input = input(prompt)

                if mode == "string":
                    return _input

                elif mode == "number":
                    return to_num(_input)

                elif mode == "split number":
                    return list(map(to_num, _input.split()))

            # Print statements
            elif inner["type"] == "print":
                mode = inner["mode"]
                args = run_recursive(inner["args"], default_return_value="")

                output = ""

                if mode in ("normal", "no newline"):
                    if isinstance(args, list):
                        output = "".join(map(_str, args))
                    else:
                        output = _str(args)

                elif mode == "spaces":
                    if isinstance(args, list):
                        output = " ".join(map(_str, args))
                    elif not isinstance(args, str):
                        output = " ".join(_str(args))
                    else:
                        output = " ".join(args)

                if SHELL:
                    print(GREEN + output + RESET, end="" if mode == "no newline" else "\n")
                else:
                    print(output, end="" if mode == "no newline" else "\n")
                return output

            # Keywords
            elif inner["type"] == "keyword":
                name = inner["name"]

                if name == "true":
                    return True
                elif name == "false":
                    return False
                elif name == "null":
                    return null
                elif name == "return":
                    _return = run_recursive(inner["value"])
                elif name == "break":
                    _break = run_recursive(inner["value"])
                elif name == "continue":
                    _continue = run_recursive(inner["value"])
                elif name == "exit":
                    if inner.get("msg"):
                        print(run_recursive(inner["msg"]))
                    exit()

            # Get variable
            elif inner["type"] == "get":
                var = get_variable(inner["id"])

                if try_no_paren_call and isinstance(var, func):
                    return run_function_call(var, [])

                return var

            # Set variable
            elif inner["type"] == "set":
                return set_variable(inner["id"], run_recursive(inner["args"]))

            # Set list index
            elif inner["type"] == "set index":
                target = run_recursive(inner["target"])
                index = run_recursive(inner["index"])
                args = run_recursive(inner["args"])

                if isinstance(index, str):
                    try:
                        index = int(index)
                    except ValueError:
                        print_error(f"ValueError: cannot convert '{index}' to int", inner["pos"])

                try:
                    target[index] = args
                    return target[index]
                except TypeError:
                    print_error(f"TypeError: expected int for index, found type '{target.__class__.__name__}'", inner["pos"])

            # Unpacking
            elif inner["type"] == "set multiple":
                values = run_recursive(inner["values"])

                if not isinstance(values, (str, list)):
                    print_error(f"TypeError: cannot unpack type '{values.__class__.__name__}'", inner["pos"])

                elif len(inner["targets"]) > len(values):
                    print_error(f"ValueError: not enough values to unpack (targets: {len(inner['targets'])}, values: {len(values)})", inner["pos"])

                elif len(inner["targets"]) < len(values):
                    print_error(f"ValueError: too many values to unpack (targets: {len(inner['targets'])}, values: {len(values)})", inner["pos"])

                return_values = []

                for i, v in enumerate(inner["targets"]):
                    # Set variable
                    if v.get("type") == "get":
                        return_values.append(set_variable(v["id"], values[i]))

                    # Set list index
                    elif v.get("type") == "index":
                        target = run_recursive(inner["targets", i, "target"])
                        index = run_recursive(inner["targets", i, "index"])

                        try:
                            target[index] = values[i]
                            return_values.append(target[index])
                        except TypeError:
                            print_error(f"TypeError: cannot assign index of type '{target.__class__.__name__}'", inner["pos"])

                return return_values

            elif inner["type"] == "ref":
                return global_var

            # Unary operators
            elif inner["type"] == "unary operator":
                op = inner["operator"]
                target = run_recursive(inner["target"])

                if op == '-':
                    if isinstance(target, (float, int)):
                        return -target
                    else:
                        print_error(f"TypeError: expected a number for unary minus, found type '{target.__class__.__name__}'", inner["pos"])

                elif op == '@':
                    if isinstance(target, bool):
                        return "".join(reversed(_str(target)))
                    elif isinstance(target, (int, float)):
                        if target >= 0:
                            return to_num("".join(reversed(str(target))))
                        return -to_num("".join(reversed(str(-target))))
                    elif isinstance(target, str):
                        return "".join(reversed(target))
                    elif isinstance(target, list):
                        return list(reversed(target))
                    else:
                        print_error(f"TypeError: cannot use reverse operator on type '{target.__class__.__name__}'", inner["pos"])

                elif op == '^':
                    if isinstance(target, int):
                        return list(range(target))
                    elif isinstance(target, list):
                        if len(target) > 3:
                            print_error(f"TypeError: expected at most 3 values for range, found {len(target)}", inner["pos"])
                        elif len(target) < 1:
                            print_error(f"TypeError: expected at least 1 value for range, found {len(target)}", inner["pos"])
                        else:
                            for v in target:
                                if not isinstance(v, int):
                                    print_error(f"TypeError: expected int for range values, found type '{v.__class__.__name__}'", inner["pos"])
                            if len(target) == 3 and target[2] == 0:
                                print_error(f"ValueError: third value for range cannot be zero", inner["pos"])
                            return list(range(*target))
                    else:
                        print_error(f"TypeError: expected int or list of ints for range, found type '{target.__class__.__name__}'", inner["pos"])

                elif op == '^^':
                    if isinstance(target, (str, list)):
                        return list(list(x) for x in enumerate(target))
                    else:
                        print_error(f"TypeError: expected str or list for enumerating, found type '{target.__class__.__name__}'", inner["pos"])

                elif op == '#':
                    if isinstance(target, (float, int)):
                        return abs(target)
                    else:
                        print_error(f"TypeError: expected a number for absolute value, found type '{target.__class__.__name__}'", inner["pos"])

                elif op == '!':
                    return not target

                elif op == '\'':
                    if isinstance(target, int):
                        if target > 1114111 or target < 0:
                            print_error(f"ValueError: char must be <= 1114111 and >= 0, found {target}", inner["pos"])
                        return chr(target)
                    elif isinstance(target, str):
                        if len(target) != 1:
                            print_error(f"ValueError: expected string with 1 character, found {len(target)} characters", inner["pos"])
                        return ord(target)
                    elif target is null:
                        return "\0"
                    else:
                        print_error(f"TypeError: cannot use char operator on type '{target.__class__.__name__}'", inner["pos"])

                elif op in ('.', '`'):
                    if isinstance(target, str):
                        return target.lower() if op == '.' else target.upper()
                    else:
                        print_error(f"TypeError: expected str for case conversion, found type '{target.__class__.__name__}'", inner["pos"])

                elif op in ('..', '``'):
                    if isinstance(target, str):
                        return target.islower() if op == '..' else target.isupper()
                    else:
                        print_error(f"TypeError: expected str for case check, found type '{target.__class__.__name__}'", inner["pos"])

                elif op == '*':
                    global_var = target
                    return target

                elif op == '??':
                    if isinstance(target, int):
                        return random.randint(1, target)
                    elif isinstance(target, (str, list)):
                        if target:
                            return random.choice(target)
                        else:
                            print_error("ValueError: iterable must contain at least 1 element to pick from", inner["pos"])
                    else:
                        print_error(f"ValueError: cannot use unary random operator on type '{target.__class__.__name__}'", inner["pos"])

            # After operators
            elif inner["type"] == "after operator":
                op = inner["operator"]
                target = run_recursive(inner["target"])

                if op == '$':
                    if isinstance(target, list):
                        return list(map(to_num, target))
                    return to_num(target)

                elif op == '`':
                    if isinstance(target, list):
                        return list(map(_str, target))
                    return _str(target)

                elif op == '^^':
                    if isinstance(target, (str, list)):
                        return " ".join(map(_str, target))
                    else:
                        print_error(f"TypeError: expected str or list for join, found type '{target.__class__.__name__}'", inner["pos"])

                elif op == '##':
                    if isinstance(target, str):
                        return target.split()
                    else:
                        print_error(f"TypeError: expected str for split, found type '{target.__class__.__name__}'", inner["pos"])

                elif op == '#$':
                    if isinstance(target, str):
                        return list(map(to_num, target))
                    else:
                        print_error(f"TypeError: expected str for split, found type '{target.__class__.__name__}'", inner["pos"])

                elif op == '\'':
                    if isinstance(target, (float, int)):
                        return round(target)
                    else:
                        print_error(f"TypeError: expected a number for rounding, found type '{target.__class__.__name__}'", inner["pos"])

                elif op == '_':
                    if isinstance(target, (str, list)):
                        return len(target)
                    else:
                        return len(_str(target))

                elif op in ('``', '$$', '@@', '..'):
                    if isinstance(target, str):
                        if op == '``':
                            return target.isalpha()
                        elif op == '$$':
                            return isnum(target)
                        elif op == '@@':
                            return isalphanum(target)
                        elif op == '..':
                            return target.isspace()
                    else:
                        print_error(f"TypeError: expected str for character check, found type '{target.__class__.__name__}'", inner["pos"])

            # Binary operators
            elif inner["type"] == "binary operator":
                return run_binary_operator(run_recursive(inner["a"]), inner["operator"], run_recursive(inner["b"]))

            # Increment (++ and --)
            elif inner["type"] == "increment":
                var = run_recursive(inner["target"])

                if isinstance(var, int):
                    d = 1 if inner["mode"] == "add" else -1
                    if inner["position"] == "before":
                        if inner["target"]["type"] == "ref":
                            global_var += d
                            return global_var
                        return set_variable(inner["target"]["id"], var + d)

                    elif inner["position"] == "after":
                        if inner["target"]["type"] == "ref":
                            ret = global_var
                            global_var += d
                            return ret
                        set_variable(inner["target"]["id"], var + d)
                        return var
                else:
                    print_error(f"TypeError: cannot {'increment' if inner['mode'] == 'add' else 'decrement'} type '{var.__class__.__name__}'", inner["pos"])

            # Functions
            elif inner["type"] == "function":
                return func(inner["index"], inner["arguments"], inner["defaults"])

            # Function calls
            elif inner["type"] == "call":
                return run_function_call(run_recursive(inner["target"]), run_recursive(inner["args"]))

            # Parentheses (in expressions)
            elif inner["type"] == "group":
                args = run_recursive(inner["inner"])
                return args

            # Blocks (as values)
            elif inner["type"] == "block":
                args = run_recursive(inner["statements"])
                return args[-1] if args else null

            # Lists
            elif inner["type"] == "list":
                args = run_recursive(inner["values"])
                return args

            # Indexing
            elif inner["type"] == "index":
                target = run_recursive(inner["target"])
                index = run_recursive(inner["index"])

                if isinstance(index, str):
                    try:
                        index = int(index)
                    except ValueError:
                        print_error(f"ValueError: cannot convert '{index}' to int", inner["pos"])

                if not isinstance(index, int):
                    print_error(f"TypeError: expected int for index, found type '{index.__class__.__name__}'", inner["pos"])

                try:
                    if isinstance(target, int):
                        target = list(map(int, str(target)))
                    return target[index]
                except IndexError:
                    print_error(f"IndexError: index out of range (index: {index}, length: {len(target)})", inner["pos"])
                except TypeError:
                    print_error(f"TypeError: cannot index type '{target.__class__.__name__}'", inner["pos"])

            # Slicing
            elif inner["type"] == "slice":
                target = run_recursive(inner["target"])
                values = run_recursive(inner["values"])

                for i, v in enumerate(values):
                    if isinstance(v, str):
                        try:
                            v = values[i] = int(v)
                        except ValueError:
                            print_error(f"ValueError: cannot convert '{v}' to int", inner["pos"])

                    if not isinstance(v, int) and v is not null:
                        print_error(f"TypeError: expected int for slice, found type '{v.__class__.__name__}'", inner["pos"])

                    if v is null:
                        values[i] = None

                try:
                    if isinstance(target, int):
                        target = list(map(int, str(target)))
                    return target[slice(*values)]
                except TypeError:
                    print_error(f"TypeError: cannot slice type '{target.__class__.__name__}'", inner["pos"])

            # Get index of element in list
            elif inner["type"] == "index of":
                target = run_recursive(inner["target"])
                value = run_recursive(inner["value"])

                if isinstance(target, str) and not isinstance(value, str):
                    if isinstance(value, int) and not isinstance(value, bool):
                        value = str(value)
                    else:
                        print_error(f"TypeError: expected str for index of str, found type '{value.__class__.__name__}'", inner["pos"])

                try:
                    return target.index(value)
                except AttributeError:
                    print_error(f"TypeError: cannot index type '{target.__class__.__name__}'", inner["pos"])
                except ValueError:
                    return -1

            # Check if element is in list
            elif inner["type"] == "contains":
                target = run_recursive(inner["target"])
                value = run_recursive(inner["value"])

                if isinstance(target, str) and not isinstance(value, str):
                    if isinstance(value, int) and not isinstance(value, bool):
                        value = str(value)
                    else:
                        print_error(f"TypeError: expected str for index of str, found type '{value.__class__.__name__}'", inner["pos"])

                try:
                    return value not in target if inner["not"] else value in target
                except AttributeError:
                    print_error(f"TypeError: cannot index type '{target.__class__.__name__}'", inner["pos"])

            # Count occurences of element in list
            elif inner["type"] == "count":
                target = run_recursive(inner["target"])
                value = run_recursive(inner["value"])

                if isinstance(target, str):
                    if isinstance(value, int) and not isinstance(value, bool):
                        value = str(value)
                    if not isinstance(value, str):
                        print_error(f"TypeError: expected str for count in str, found type '{value.__class__.__name__}'", inner["pos"])

                try:
                    return target.count(value)
                except AttributeError:
                    print_error(f"TypeError: cannot count in type '{target.__class__.__name__}'", inner["pos"])

            # For loop
            elif inner["type"] == "for loop":
                sum_loop = inner["sum"]

                lst = run_recursive(inner["list"])
                if isinstance(lst, int):
                    lst = list(range(lst))
                elif not isinstance(lst, (str, list)):
                    print_error(f"TypeError: cannot iterate over type '{lst.__class__.__name__}'", inner["pos"])

                _vars = inner["vars"]
                return_values = []

                append_stack("for loop")
                for v in lst:
                    if _vars is not None:
                        if _vars["type"] == "list":
                            if not isinstance(v, (list, str)):
                                v = [v]

                            if len(_vars["values"]) > len(v):
                                print_error(f"ValueError: not enough values to unpack (targets: {len(_vars['values'])}, values: {len(v)})", inner["pos"])

                            elif len(_vars["values"]) < len(v):
                                print_error(f"ValueError: too many values to unpack (targets: {len(_vars['values'])}, values: {len(v)})", inner["pos"])

                            for i, _v in enumerate(_vars["values"]):
                                set_variable(_v["id"], v[i], force_inner=True)

                        else:
                            set_variable(_vars["id"], v, force_inner=True)

                    # else:
                    #     loop_var = v  FIXME idfk wtf tf im doing

                    ret = run_recursive(inner["statements"])

                    if _continue is not None:
                        return_values.append(_continue)
                        _continue = None
                        continue

                    elif _break is not None:
                        return_values.append(_break)
                        _break = None
                        break

                    elif _return is not None:
                        return

                    elif ret and ret[-1] is not null:
                        return_values.append(ret[-1])

                stack.pop()
                if sum_loop:
                    ret = return_values[0]
                    for v in return_values[1:]:
                        ret = run_binary_operator(ret, '+', v)
                    return ret
                else:
                    return return_values

            # While loop
            elif inner["type"] == "while loop":
                sum_loop = inner["sum"]

                return_values = []

                while run_recursive(inner["condition"]):
                    ret = run_recursive(inner["statements"])

                    if _continue is not None:
                        return_values.append(_continue)
                        _continue = None
                        continue

                    elif _break is not None:
                        return_values.append(_break)
                        _break = None
                        break

                    elif _return is not None:
                        return

                    elif ret and ret[-1] is not null:
                        return_values.append(ret[-1])

                if sum_loop:
                    ret = return_values[0]
                    for v in return_values[1:]:
                        ret = run_binary_operator(ret, '+', v)
                    return ret
                else:
                    return return_values

            # If statement
            elif inner["type"] == "if":
                cond = run_recursive(inner["condition"])
                ret = run_recursive(inner["true" if (not cond if inner["invert"] else cond) else "false"])
                return ret[-1] if ret else null

            # x{...} syntax
            elif inner["type"] == "brace syntax":
                op = inner["op"]

                target = run_recursive(inner["target"])

                if isinstance(target, int) and not isinstance(target, bool):
                    target = list(map(int, str(target)))

                elif not isinstance(target, (str, list)):
                    print_error(f"TypeError: cannot iterate over type '{target.__class__.__name__}'", inner["pos"])

                elif len(target) == 0:
                    print_error(f"ValueError: brace syntax iterable must have at least one value", inner["pos"])

                key = run_recursive(inner["key"])

                if not isinstance(key, func) and key is not null:
                    print_error(f"TypeError: expected a function, found type '{key.__class__.__name__}'", inner["pos"])

                if key is not null:
                    compare = list(map(lambda x: run_function_call(key, [x]), target))
                else:
                    compare = target

                if op == '<':
                    return list(sorted(target, key=lambda x: compare[target.index(x)]))

                elif op == '>':
                    return list(sorted(target, key=lambda x: compare[target.index(x)], reverse=True))

                elif op == '.':
                    return min(target, key=lambda x: compare[target.index(x)])

                elif op == '^':
                    return max(target, key=lambda x: compare[target.index(x)])

                elif op == '=':
                    return all(x == compare[0] for x in compare)

                elif op == '!':
                    return all(x not in compare[:n] for n, x in enumerate(compare))

                elif op == '#':
                    return max(compare, key=lambda x: compare.count(x))

                else:
                    ret = compare[0]
                    for v in compare[1:]:
                        ret = run_binary_operator(ret, op, v)
                    return ret

            # Strings
            elif inner["type"] == "string":
                return concatenate_fragments(inner["fragments"])

            # Replacing
            elif inner["type"] == "replace":
                target = run_recursive(inner["target"])
                if not isinstance(target, str):
                    print_error(f"TypeError: cannot use replace on type '{target.__class__.__name__}'", inner["pos"])

                for left, right in inner["pairs"]:
                    left = concatenate_fragments(left)
                    right = concatenate_fragments(right)

                    if inner["mode"] == "normal":
                        target = target.replace(left, right)

                    elif inner["mode"] == "swap":
                        target = right.join(left.join(x.split(right)) for x in target.split(left))

                    elif inner["mode"] == "first":
                        target = target.replace(left, right, 1)

                    elif inner["mode"] == "last":
                        target = right.join(target.rsplit(left, 1))

                return target

            # Ints, floats etc.
            elif inner["type"] == "number":
                return inner["value"]

            return null

        try:
            line_return_value = run_recursive(ast["statements"])
            if SHELL and line_return_value and line_return_value[-1] != null:
                out = _str(line_return_value[-1])
                if isinstance(line_return_value[-1], str):
                    out = f'"{add_escapes(out)}"'
                print(CYAN + out + RESET)

        except (KeyboardInterrupt, EOFError):
            print_error("Manually stopped execution")

    except RecursionError:
        print_error("RecursionError: recursion limit reached")


# Command line part
cliargsparser = argparse.ArgumentParser(
    description="malb8dge (thanks bombie) is ANOTHER programming language made by kr8gz who doesn't know how to make programming languages.",
    formatter_class=argparse.RawTextHelpFormatter
)
cliargsparser.add_argument('file', nargs='?', default="", help="The input file")
cliargsparser.add_argument('-d', '--debug', action="store_true", help="Whether to run in Debug Mode")


def main():
    global DEBUG_MODE, SHELL

    cliargs = cliargsparser.parse_args()

    if cliargs.debug:
        DEBUG_MODE = True

    if os.path.isfile(cliargs.file):
        run_file(cliargs.file)

    elif os.path.isfile(cliargs.file + ".mlb8"):
        run_file(cliargs.file + ".mlb8")

    elif cliargs.file:
        print("This file doesn't exist")

    else:
        SHELL = True
        shell_lines = []
        while True:
            _line = ""
            try:
                _line = input(GRAY + ">>> " + RESET)
            except KeyboardInterrupt:
                print()
                continue
            except EOFError:
                exit()
            finally:
                shell_lines.append(_line)

            try:
                run("<shell>", shell_lines)
            except ContinueShell:
                continue


if __name__ == "__main__":
    main()
