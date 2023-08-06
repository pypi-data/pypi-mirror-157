#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import time

from .tokens import resolve_tokens
from .syntax import syntactic_analysis
from .codegen import create_asm_code
from .compilerexception import CompilerException, UnexpectedException
from .programdatabase import ProgramDatabase
from .postprocess import PostProcessor

# todo:
# reference parameters
# arrays with constant length

# somehow check that nothing comes after finished syntaxes only problem for expressions?
# too short syntaxes create python errormessages since access to non existing token also too many tokens, tokens come after expression syntax are errors too (just check if non expression token in expression and dont find end of the expression)

# reagant function with lr


if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Compile to IC10 assembler.')
    parser.add_argument("source", help="Source File.", metavar="source_file")
    parser.add_argument("-o", "--out_file", default=None, help="File with IC10 assembler code.", metavar="out_file")
    parser.add_argument("-c", "--copy", action="store_true", help="Copy IC10 assembler code into clipboard.")
    parser.add_argument("-s", "--varstackoffset", default=400, type=int, help="Offset of the part of the stack which will be used for Variables.", metavar="offset_varstack")
    parser.add_argument("-l", "--varstacklength", default=100, type=int, help="Length of the part of the stack which will be used for Variables.", metavar="length_varstack")
    parser.add_argument("-a", "--annotate", action="store_true", help="Annotate IC10 assembler code with comments.")
    parser.add_argument("-p", "--print_output", action="store_true", help="Prints compiled IC10 assembler to the standard output.")
    parser.add_argument("--no_optimization", action="store_false", help="Ommits replacement of pointless lines.")
    parser.add_argument("--no_post_processing_optimization", action="store_true", help="Do not remove garbage from code after compilation complete.")
    parser.add_argument("--display_emulator_stats", action="store_true", help="Shows statistic about emulator works.")
    parser.add_argument("--silent", action="store_true", help="No output to console except code with -p key.")

    parse = parser.parse_args()

    orgprint = print
    if parse.silent:
        print = lambda *a: None

    try:
        ProgramDatabase.VAR_STACK_LENGTH = parse.varstacklength
        ProgramDatabase.VAR_STACK_OFFSET = parse.varstackoffset
        ProgramDatabase.ANNOTATE = parse.annotate
        ProgramDatabase.CODE_OPTIMIZATION = parse.no_optimization
        ProgramDatabase.PP_OPTIMIZATION = not parse.no_post_processing_optimization

        if ProgramDatabase.VAR_STACK_OFFSET+ProgramDatabase.VAR_STACK_LENGTH>=512:
            raise CompilerException("Stacklength not high enough to support varstackoffset and varstacklength configuration.")

        try:
            with open(parse.source, "r") as source_file:
                program = "".join(source_file.readlines()).split("\n")
        except FileNotFoundError:
            raise CompilerException("The file you are trying to open does not exist.")
        code = []  # Format: string, True:raw code False:syntax for code generation
        compile_time = time.time()
        for i, line in enumerate(program):
            ProgramDatabase.set_compiler_position(i)
            tokens = resolve_tokens(line)
            syntax = syntactic_analysis(tokens)
            code.append(syntax)
        pd = ProgramDatabase(len(code))
        asm_code = create_asm_code(code, ProgramDatabase.BType.Global_, database=pd)[:-1]  # ommit final newline
        if not pd.has_main():
            raise CompilerException("No main block.")

        compile_time = time.time() - compile_time
        n_lines_bo = n_lines_fin = asm_code.count("\n") - 1

        print(f"Successfully compiled on {n_lines_bo} lines in {compile_time:.2f} seconds.")
        if ProgramDatabase.CODE_OPTIMIZATION:
            optimize_time = time.time()
            print("Making base optimizations...")
        
            asm_code = asm_code.replace("move ra sp\nmove sp ra\n", "")  # can't always be handled within a single expression
            asm_code = asm_code.replace("move sp ra\nmove ra sp\n", "")  # can't always be handled within a single expression
            asm_code = asm_code.replace("j main\nmain:\n", "")
            
            if ProgramDatabase.PP_OPTIMIZATION:
                pp = PostProcessor(pd, asm_code)
                # iterate over optimizations due lines count decreasing
                for i in range(11):
                    if not pp.iterate():
                        break
                    n_lines_fin = pp.get_lines_count()
                    print(f"Post process optimization iteration: {i + 1}, lines: {n_lines_fin}...")
                if not pp.finalize():
                    print("Notify: maybe optimizator cant remove some garbage from code")
                asm_code = pp.get_final_code()

                if parse.display_emulator_stats:
                    print("Emulator stats:")
                    print("max depth:", PostProcessor.SimpleVM.Stats.max("depth"))
                    print("max totalsteps-fail:", PostProcessor.SimpleVM.Stats.max("totalsteps-fail"))
                    print("max totalsteps-found:", PostProcessor.SimpleVM.Stats.max("totalsteps-found"))
                    print("avg totalsteps-fail:", PostProcessor.SimpleVM.Stats.avg("totalsteps-fail"))
                    print("avg totalsteps-found:", PostProcessor.SimpleVM.Stats.avg("totalsteps-found"))

                    print("max localsteps-fail:", PostProcessor.SimpleVM.Stats.max("localsteps-fail"))
                    print("max localsteps-found:", PostProcessor.SimpleVM.Stats.max("localsteps-found"))
                    print("avg localsteps-fail:", PostProcessor.SimpleVM.Stats.avg("localsteps-fail"))
                    print("avg localsteps-found:", PostProcessor.SimpleVM.Stats.avg("localsteps-found"))

            n_lines_fin = asm_code.count("\n") - 1
            percent_removed = 100 - (100 / n_lines_bo * n_lines_fin)
            optimize_time = time.time() - optimize_time
            print(f"Optimized from {n_lines_bo} to {n_lines_fin} lines in {optimize_time:.2f} seconds. {percent_removed:.0f}% of code removed.")

        # adding header to output file
        txtheader = []
        # add script description from first line of sourcecode
        if program[0] and program[0][0] == "#":
            txtheader.append(program[0])

        # add source filename
        txtheader.append(f"# Source file: {parse.source}")
        # add information about compiler
        txtheader.append("# Compiled by compic10, gitlab.com/smpkdev/compic10")

        n_lines_free = 127 - n_lines_fin
        asm_code = (("\n".join(txtheader[:n_lines_free]) + "\n") if n_lines_free > 0 else "") + asm_code

        n_lines_fin = asm_code.count("\n") - 1
        if n_lines_fin>127:
            print(f"Warning: IC10-assembler is too long. At most 127 lines are allowed.")
        if parse.print_output:
            orgprint(asm_code)
        if parse.copy:
            try:
                import clipboard
            except ModuleNotFoundError:
                raise CompilerException("The 'clipboard' package is needed for the '-c'/'--copy' option you can install it"
                                        "by running 'python -m pip install clipboard' (if there is no 'python' command try 'python3' instead).")

            clipboard.copy(asm_code)
        
        if parse.out_file:
            try:
                with open(parse.out_file, "w") as out_file:
                    out_file.writelines(asm_code)
            except:
                raise CompilerException(
                "Can't save to file.")
    
    except CompilerException as ce:
        print(str(ce))
    except UnexpectedException as ue:
        print(str(ue))
    except Exception as e:
        print(f"Unknown Exception at line {ProgramDatabase.line}")
        raise e

    
