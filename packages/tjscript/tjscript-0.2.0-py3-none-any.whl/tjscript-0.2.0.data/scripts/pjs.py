#!python

"""PJScript core script"""

import os
import sys
import json
import argparse
from pjscript.syntax.lexer import Lexer
from pjscript.syntax.parser import Parser
from pjscript.compiler import CXXCompiler

parser = argparse.ArgumentParser('PJScript')
parser.add_argument('source', nargs='?', default='')
parser.add_argument('--buildproj', help='Compile project by a given path')
parser.add_argument('--cgen-mode', '-c',
                    help='Generate .cpp, .hpp files', action='store_true')
parser.add_argument('--dump-mode', '-d',
                    help='Prints an AST pseudo code', action='store_true')
parser.add_argument('--json-mode', '-j',
                    help='Serializes an AST to JSON', action='store_true')


def name(path: str) -> str:

    """Returns name by path"""

    return os.path.basename(path).split('.')[0]  # <-- only pjs needs this


if __name__ == '__main__':

    args = parser.parse_args()
    if args.buildproj:
        CXXCompiler(args.buildproj).compile()   # <- compile given project
        sys.exit(0)  # <- exit immediately after (successful?) compilation
    if not args.source:
        print('REPL is not implemented yet; see help for further options')
    with open(args.source,  'r',  encoding='utf-8') as source_code_reader:
        parsed = Parser(Lexer(source_code_reader.read()).lexed()).parsed()
        if args.cgen_mode:
            name = name(args.source)  # <-- get module name from file path
            base = os.path.dirname(args.source)  # <--- get base directory
            mask = os.path.join(
                base, 'generated', os.path.basename(args.source))   # mask
            hpp, cpp = parsed.ctxs(name=name)  # <---- generate .hpp, .cpp
            with open(mask + '-to.hpp', 'w', encoding='utf-8') as hpp_f_w:
                hpp_f_w.write(hpp)  # <----------- write down .cpp context
            with open(mask + '-to.cpp', 'w', encoding='utf-8') as cpp_f_w:
                cpp_f_w.write(cpp)  # <----------- write down .hpp context
        if args.dump_mode:
            print(parsed)  # <-- use built-in string Program serialization
        if args.json_mode:
            print(json.dumps(parsed.to_dict()))  # dumps out a JSON string
