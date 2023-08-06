"""PJScript C++ code compiler"""

import os
from pjscript.syntax.lexer import Lexer
from pjscript.syntax.parser import Parser


class CXXCompiler:         # pylint: disable=too-few-public-methods # (it's more than enough)

    """This class will compile a project"""

    _project: str

    def __init__(self, project: str) -> None:

        """Instantiate CXXCompiler"""

        self._project = self._normalize(project)

    @staticmethod
    def _normalize(path) -> str:

        """Returns normalized path"""

        return path if not path.endswith('/') else path[:-1]

    @staticmethod
    def _generate_sh_ctx(binary: str) -> str:

        """This will generate <project>.sh context"""

        return f'#!/usr/bin/env bash\n'\
               f'#macOS uses its own linker variable name\n'\
               f'export LD_LIBRARY_PATH=runtime/cxx/build\n'\
               f'DYLD_LIBRARY_PATH=$LD_LIBRARY_PATH {binary}'

    @staticmethod
    def _generate_main_ctx() -> str:

        """This will generate <project>.cpp context"""

        return '#include "startup.tjs-to.hpp"\n'\
               'int main(int argc, char* argv[])\n'\
               '{\n'\
               'Environment* environment = new Environment();\n'\
               'startup(environment);\n'\
               'return 0;\n'\
               '}\n'

    def compile(self) -> None:                              # pylint: disable=too-many-locals

        """Compile given project"""

        # TODO: for now we only compile './startup.tjs`, and do not take into account others!

        startup = os.path.join(self._project, 'startup.tjs')
        assert os.path.exists(startup), "CXXCompiler: each project should have 'startup.tjs'"

        with open(startup, 'r', encoding='utf-8') as startup_f_rdr:
            hpp_, cpp_ = Parser(Lexer(startup_f_rdr.read()).lexed()).parsed().ctxs('startup')

        if not os.path.exists(os.path.join(self._project, 'built')):
            os.mkdir(os.path.join(self._project, 'built'))  # <------------- make 'built' dir
        if not os.path.exists(os.path.join(self._project, 'generated')):
            os.mkdir(os.path.join(self._project, 'generated'))  # <----- make 'generated' dir

        st_hpp = os.path.join(self._project, 'generated', 'startup.tjs-to.hpp')   # .hpp file
        st_cpp = os.path.join(self._project, 'generated', 'startup.tjs-to.cpp')   # .cpp file

        with open(st_hpp, 'w', encoding='utf-8') as st_hpp_w:
            st_hpp_w.write(hpp_)  # <------ write down generated .hpp context for startup.tjs
        with open(st_cpp, 'w', encoding='utf-8') as st_cpp_w:
            st_cpp_w.write(cpp_)  # <------ write down generated .cpp context for startup.tjs

        f_mask = os.path.basename(self._project)  # <------- get the base name of the project
        script = os.path.join(self._project, f_mask + '.sh')  # <--- get launcher script path
        binary = os.path.join(self._project, 'built', f_mask + '.bin')  # <-- get binary path
        main_f = os.path.join(self._project, 'generated', f_mask + '.cpp')  # <-- script path

        with open(script, 'w', encoding='utf-8') as sh_f_w:
            sh_f_w.write(self._generate_sh_ctx(binary))  # <- write down <project>.sh context
        with open(main_f, 'w', encoding='utf-8') as main_f_w:
            main_f_w.write(self._generate_main_ctx())   # <- write down <project>.cpp context

        cmd = f'clang++ --std=c++20 ' \
              f'-I. -I{self._project} {st_cpp} {main_f} ' \
              f'-Lruntime/cxx/build -lpjscript -o {binary}'   # <- generate a clang++ command

        print(cmd)  # <-- print cmd so user can copy it and use separately (useful for debug)
        os.system(cmd)  # <------------------------------------- invoke cmd using os.system()

        os.system(f'chmod +x {script}')  # <---- change mode of launcher script to executable
        print('Use this to run compiled project:', f'./{script}')  # <--- print a useful hint
