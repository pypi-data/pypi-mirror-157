import re
import itertools

from .syntax import *
from .tokens import *
from .compilerexception import CompilerException, UnexpectedException
from .compilerutil import *
from .compilerutil import IndexingPlaceholder
from .programdatabase import ProgramDatabase


blocksyntax = (ForSyntax, WhileSyntax, IfSyntax, AsmSyntax)
assignment_operators = ["=", "+=", "-=", "*=", "/=", "%=", "&&=" ,"||="]

def create_asm_code(code, btype, start = 0, end = None, /, *, database = None, handle_blocks = True):
    if not database:
        database = ProgramDatabase(len(code))
    if not end:
        end = len(code)
    asm_code = ""
    if handle_blocks:
        database.start_block(start, btype)  # initiate new block, context manager for this would be overkill
    idx = start
    while(idx<end):
        line = code[idx]
        ProgramDatabase.set_compiler_position(idx)
        if not line:  # blank line
            idx+=1
            continue
        for gen in code_generators:
            if gen.match_gen(line):
                code_gen = gen(database, code, idx)
                asm_code+= code_gen.get_code()
                idx = code_gen.get_end()
                break
        else:
            raise CompilerException(f"Can't match line \"" + "".join([t.get_rawstring() for t in line.get_token_family()]) + "\" to any code generator.") 
    aliases = ""
    if handle_blocks:
        devices = list(filter(lambda n: n.ntype == ProgramDatabase.NType.Device, database.get_names()))  # must be before block end 
        # batch_devices = list(filter(lambda n: n.ntype == ProgramDatabase.NType.Batch_Device, database.get_names()))  # must be before block end 
        database.end_block(end)  # end block
        for d in sorted(devices, key=lambda d:database.get_device(d.name)[1]):  # just needed, that screws are labeled
            value = database.get_device(d.name)[1]
            aliases+=f"alias {d.name} d{value}\n"
        # for d in batch_devices:
        #     value = database.get_device(d.name)[1]
        #     aliases+=f"define {d.name} {value:#x}\n"
    return aliases + ("" if start != 0 else "j main\n") + asm_code


class CodeGen:
    _init_syntax = None

    def __init__(self, _context, _start_line):
        _context.set_compiler_position(_start_line)
        self._start_line = _start_line
        self._end_line = _start_line+1
        self._code = ""
        self._context = _context  # the ProgramDatabase object

    @classmethod
    def match_gen(Cls, _syntax):
        return isinstance(_syntax, Cls._init_syntax)

    def get_bounds(self):
        return (self._start_line, self._end_line)

    def get_code(self):
        return self._code[:]
    
    def get_end(self):
        return self._end_line
    
    def get_start(self):
        return self._start_line
    
    def get_span(self):
        return (self._start_line, self._end_line)


class EndCode(CodeGen):
    _init_syntax = EndSyntax

    def __init__(self, _context, _code, _idx_line):
        raise CompilerException("Stray end statement.")


class AlternativeCode(CodeGen):
    _init_syntax = IfSyntax

    def __init__(self, _context, _code, _idx_line):
        super().__init__(_context, _idx_line)
        if not isinstance(_code[_idx_line], IfSyntax):
            raise CompilerException("Alternative-subcode must be initiated by an if-syntax.")
        alternatives = []  # Format: (condition, [codelines])
        else_case = None  # Format: [codelines]
        condition = _code[_idx_line].get_condition()
        start_idx = 0
        under_blocks = 1
        for i, syntax in enumerate(_code[_idx_line+1:]):
            if isinstance(syntax, blocksyntax):
                under_blocks+=1
            if isinstance(syntax, ElifSyntax):
                if under_blocks>1: continue
                if not condition:
                    raise CompilerException("elif statement can't follow an else statement.")
                alternatives.append((
                    condition,
                    (start_idx+_idx_line+1, i+_idx_line+1)
                ))
                condition = syntax.get_condition()
                start_idx = i+1
            elif isinstance(syntax, ElseSyntax):
                if under_blocks>1: continue
                if not condition:
                    raise CompilerException("Can't have multiple else statements.")
                alternatives.append((
                    condition,
                    (start_idx+_idx_line+1, i+_idx_line+1)
                ))
                condition = None
                start_idx = i+1
            elif isinstance(syntax, EndSyntax):
                if under_blocks>1: 
                    under_blocks-=1
                    continue
                if not condition:
                    else_case = (start_idx+_idx_line+1, i+_idx_line+1)
                else:
                    alternatives.append((
                        condition,
                        (start_idx+_idx_line+1, i+_idx_line+1)
                    ))
                self._end_line = i+1+_idx_line+1
                break
        else:
            raise CompilerException("if syntax without closing statement.")
        self._code = ""
        self._conditions = []
        self._codeblocks = []
        self._elseblock = None

        # only one block will be executed and all conditions before therefore state resets with revert_state

        alternative_id = _context.generate_block_id(ProgramDatabase.BType.If_)
        snapshot_start = _context.make_snapshot()
        for i, (cond, body) in enumerate(alternatives):
            _context.set_compiler_position(body[0]-1)
            self._conditions.append(ExpressionCode(_context, [cond], 0, body[0]-1, _must_return_override=True))
            snapshot_after_condition = _context.make_snapshot()
            body_asm = create_asm_code(_code, ProgramDatabase.BType.If_, *body, database=_context)
            self._codeblocks.append(body_asm)
            self._code+=ProgramDatabase.annotate("# if " if i==0 else "# elif " + f"{{{self._conditions[-1].get_rawexpr()}}}\n") + self._conditions[-1].get_code()
            self._code+=f"beqz r{self._conditions[-1].get_result_reg()} end_if_{alternative_id}_block_{i}\n"
            self._code+=self._codeblocks[-1]
            snapshot_end = _context.make_snapshot()
            revert_asm = _context.revert_state(snapshot_start, snapshot_end)
            if revert_asm:
                self._code+=ProgramDatabase.annotate("# Revert State to that before this block.\n")
            self._code+=revert_asm
            self._code+=f"j end_if_{alternative_id}\n"
            self._code+=f"end_if_{alternative_id}_block_{i}:\n"
            _context.overwrite_memory(snapshot_after_condition)  # will be seen when other conditions executed (only one if, elif, else clause will be executed all conditions see the state with all previous conditions evaluated)
        if else_case:
            self._elseblock = create_asm_code(_code, ProgramDatabase.BType.If_, *else_case, database=_context)
            self._code+=ProgramDatabase.annotate("# else\n") + self._elseblock 
            snapshot_end = _context.make_snapshot()
            revert_asm = _context.revert_state(snapshot_start, snapshot_end)
            if revert_asm:
                self._code+=ProgramDatabase.annotate("# Revert State to that before this block.\n")
            self._code += revert_asm
        self._code+=f"end_if_{alternative_id}:\n"
        _context.overwrite_memory(snapshot_start)  # due to state reverts same state as before


class WhileLoopCode(CodeGen):
    _init_syntax = WhileSyntax

    def __init__(self, _context, _code, _idx_line):
        super().__init__(_context, _idx_line)
        if not isinstance(_code[_idx_line], WhileSyntax):
            raise CompilerException(
                "while-subcode must be initiated by an while-syntax.")
        condition = _code[_idx_line].get_condition()
        snapshot_start = _context.make_snapshot()
        self._condition_code = ExpressionCode(_context, [condition], 0, _idx_line, _must_return_override=True)
        snapshot_after_condition = _context.make_snapshot()
        
        _context.current_loop_break_snapshot.append(snapshot_after_condition)  # for break
        _context.current_loop_continue_snapshot.append(snapshot_start)  # for continue
        
        start_idx = 0
        body = None
        under_blocks = 1
        for i, syntax in enumerate(_code[_idx_line+1:]):
            if isinstance(syntax, blocksyntax):
                under_blocks+=1
            if isinstance(syntax, EndSyntax):
                if under_blocks>1:
                    under_blocks-=1
                    continue
                break
        else:
            raise CompilerException("while loop never ended.")
        
        while_loop_id = _context.generate_block_id(ProgramDatabase.BType.While_)
        self._block_code = create_asm_code(_code, ProgramDatabase.BType.While_, start_idx+_idx_line+1, i+_idx_line+1, database=_context)
        snapshot_end = _context.make_snapshot()
        revert_asm = _context.revert_state(snapshot_start, snapshot_end)
        _context.current_loop_break_snapshot.pop()  # for break
        _context.current_loop_continue_snapshot.pop()  # for continue
        _context.overwrite_memory(snapshot_after_condition)
        self._end_line = i+1+_idx_line+1
        self._code = ProgramDatabase.annotate(f"# while {{{self._condition_code.get_rawexpr()}}}\n")
        self._code += f"while_{while_loop_id}_start:\n"
        self._code += self._condition_code.get_code()
        self._code += f"beqz r{self._condition_code.get_result_reg()} while_{while_loop_id}_end\n"
        self._code += self._block_code
        if revert_asm:
            self._code += ProgramDatabase.annotate("# Revert state of program to that before the loop.\n")
        self._code += revert_asm
        self._code += f"j while_{while_loop_id}_start\n"
        self._code += f"while_{while_loop_id}_end:\n"

class ForLoopCode(CodeGen):
    _init_syntax = ForSyntax

    def __init__(self, _context, _code, _idx_line):
        super().__init__(_context, _idx_line)
        if not isinstance(_code[_idx_line], ForSyntax):
            raise CompilerException(
                "for-subcode must be initiated by an for-syntax.")
        (_, init_expr), (_, condition), (_, iter_expr) = _code[_idx_line].get_loopparameters()
        start_idx = 0
        body = None
        under_blocks = 1
        if type(init_expr) == Expression:
            self._init_code = ExpressionCode(_context, [init_expr], 0, _idx_line)
        else:
            self._init_code = VariableDeclarationCode(_context, [init_expr], 0, _idx_line)
        snapshot_start = _context.make_snapshot()
        self._iter_code = ExpressionCode(_context, [iter_expr], 0, _idx_line)
        snapshot_after_iter = _context.make_snapshot()
        self._condition_code = ExpressionCode(_context, [condition], 0, _idx_line, _must_return_override=True)
        snapshot_after_condition = _context.make_snapshot()
       
        _context.current_loop_break_snapshot.append(snapshot_after_condition)  # for break
        _context.current_loop_continue_snapshot.append(snapshot_start)  # for continue

        for i, syntax in enumerate(_code[_idx_line+1:]):
            if isinstance(syntax, blocksyntax):
                under_blocks += 1
            if isinstance(syntax, EndSyntax):
                if under_blocks > 1:
                    under_blocks -= 1
                    continue
                break
        else:
            raise CompilerException("for loop never ended.")
        
        for_loop_id = _context.generate_block_id(ProgramDatabase.BType.For_)
        _context.start_block(_idx_line+1, ProgramDatabase.BType.For_)
        # can't automatically handle blocks since itervariable needed (would be unbound otherwise)
        self._loop_body = create_asm_code(_code, ProgramDatabase.BType.For_, start_idx+_idx_line+1, i+_idx_line+1, database=_context, handle_blocks=False)
        self._end_line = i+1+_idx_line+1
        _context.set_compiler_position(self._end_line-1)
        _context.end_block(self._end_line-1)
        snapshot_end = _context.make_snapshot()
        revert_asm = _context.revert_state(snapshot_start, snapshot_end)
        entry_asm = _context.revert_state(snapshot_after_iter, snapshot_start)
        _context.current_loop_break_snapshot.pop()  # for break
        _context.current_loop_continue_snapshot.pop()  # for continue
        _context.overwrite_memory(snapshot_after_condition)
        # body code must be compiled to maybe indented

        self._code = ProgramDatabase.annotate("# for {" + (self._init_code.get_rawexpr() if type(self._init_code) is ExpressionCode else self._init_code.get_rawdecl()) + f", {self._condition_code.get_rawexpr()}, {self._iter_code.get_rawexpr()}}}\n")
        self._code += self._init_code.get_code()
        if entry_asm:
            self._code += ProgramDatabase.annotate("# Revert state of program to that after iter-expression.\n")
        self._code += entry_asm
        self._code += f"j for_{for_loop_id}_start\n"
        self._code += f"for_{for_loop_id}_iter:\n"
        self._code += self._iter_code.get_code()
        self._code += f"for_{for_loop_id}_start:\n"
        self._code +=self._condition_code.get_code()
        self._code += f"beqz r{self._condition_code.get_result_reg()} for_{for_loop_id}_end\n"
        self._code += self._loop_body
        if revert_asm:
            self._code += ProgramDatabase.annotate("# Revert state of program to that before the loop.\n")
        self._code += revert_asm
        self._code += f"j for_{for_loop_id}_iter\n"
        self._code += f"for_{for_loop_id}_end:\n"


class ExpressionCode(CodeGen):
    _init_syntax = Expression

    pointless_lines = [
        (r"\t*move\s+(r[0-9a]{1,2}|(?:sp))\s+\1.*\n", ""),
        (r"\t*push\s+(r[0-9a]{1,2}|(?:sp)).*\n\s*pop\s+\1.*\n", ""),
        (r"\t*push\s+(r[0-9a]{1,2}|(?:sp)).*\n\s*pop\s+(r[0-9a]{1,2}|(?:sp)).*\n", r"move \2 \1\n"),
        (r"\t*pop\s+(r[0-9a]{1,2}|(?:sp)).*\n\s*push\s+\1.*\n", ""),
    ]

    @staticmethod
    def function_call(_context, _fncname, _res, _params, _must_return, _reserved_registers, reserve_hook):
        
        # builtinprefix suffix must be removed!!!
        
        builtin_prefix = ""
        builtin_suffix = ""
        res_code = ""
        if _fncname == "abs":
            if len(_params)!=1:
                raise CompilerException("\"abs\" functions requires exactly one parameter.")
            res_code += builtin_prefix+f"abs {_res} {_params[0]}\n"+builtin_suffix
        elif _fncname == "acos":
            if len(_params)!=1:
                raise CompilerException("\"acos\" functions requires exactly one parameter.")
            res_code += builtin_prefix+f"acos {_res} {_params[0]}\n"+builtin_suffix
        elif _fncname == "asin":
            if len(_params)!=1:
                raise CompilerException("\"asin\" functions requires exactly one parameter.")
            res_code += builtin_prefix+f"asin {_res} {_params[0]}\n"+builtin_suffix
        elif _fncname == "atan":
            if len(_params)!=1:
                raise CompilerException("\"atan\" functions requires exactly one parameter.")
            res_code += builtin_prefix+f"atan {_res} {_params[0]}\n"+builtin_suffix
        elif _fncname == "ceil":
            if len(_params)!=1:
                raise CompilerException("\"ceil\" functions requires exactly one parameter.")
            res_code += builtin_prefix+f"ceil {_res} {_params[0]}\n"+builtin_suffix
        elif _fncname == "cos":
            if len(_params)!=1:
                raise CompilerException("\"cos\" functions requires exactly one parameter.")
            res_code += builtin_prefix+f"cos {_res} {_params[0]}\n"+builtin_suffix
        elif _fncname == "exp":
            if len(_params)!=1:
                raise CompilerException("\"exp\" functions requires exactly one parameter.")
            res_code += builtin_prefix+f"exp {_res} {_params[0]}\n"+builtin_suffix
        elif _fncname == "floor":
            if len(_params)!=1:
                raise CompilerException("\"floor\" functions requires exactly one parameter.")
            res_code += builtin_prefix+f"floor {_res} {_params[0]}\n"+builtin_suffix
        elif _fncname == "log":
            if len(_params)!=1:
                raise CompilerException("\"log\" functions requires exactly one parameter.")
            res_code += builtin_prefix+f"log {_res} {_params[0]}\n"+builtin_suffix
        elif _fncname == "rand":
            if len(_params)!=0:
                raise CompilerException("\"rand\" functions requires exactly zero parameters.")
            res_code += builtin_prefix+f"rand {_res} {_params[0]}\n"+builtin_suffix
        elif _fncname == "round":
            if len(_params)!=1:
                raise CompilerException("\"round\" functions requires exactly one parameter.")
            res_code += builtin_prefix+f"round {_res} {_params[0]}\n"+builtin_suffix
        elif _fncname == "sin":
            if len(_params)!=1:
                raise CompilerException("\"sin\" functions requires exactly one parameter.")
            res_code += builtin_prefix+f"sin {_res} {_params[0]}\n"+builtin_suffix
        elif _fncname == "sqrt":
            if len(_params)!=1:
                raise CompilerException("\"sqrt\" functions requires exactly one parameter.")
            res_code += builtin_prefix+f"sqrt {_res} {_params[0]}\n"+builtin_suffix
        elif _fncname == "tan":
            if len(_params)!=1:
                raise CompilerException("\"tan\" functions requires exactly one parameter.")
            res_code += builtin_prefix+f"tan {_res} {_params[0]}\n"+builtin_suffix
        elif _fncname == "trunc":
            if len(_params)!=1:
                raise CompilerException("\"trunc\" functions requires exactly one parameter.")
            res_code += builtin_prefix+f"trunc {_res} {_params[0]}\n"+builtin_suffix
        elif _fncname == "max":
            if len(_params)<2:
                raise CompilerException("\"max\" functions requires at least two parameters.")
            res = f"max {_res} {_params[0]} {_params[1]}\n"
            for i in range(2, len(_params)):
                res += f"max {_res} {_res} {_params[i]}\n"
            res_code += builtin_prefix+res+builtin_suffix
        elif _fncname == "min":
            if len(_params)<2:
                raise CompilerException("\"min\" functions requires at least two parameters.")
            res = f"min {_res} {_params[0]} {_params[1]}\n"
            for i in range(2, len(_params)):
                res += f"min {_res} {_res} {_params[i]}\n"
            res_code += builtin_prefix+res+builtin_suffix
        elif _fncname == "sleep":
            if _must_return:
                raise CompilerException("\"sleep\" does not return.")
            if len(_params) != 1:
                raise CompilerException(
                    "\"sleep\" procedure requires exactly one parameter.")
            res_code += builtin_prefix+f"sleep {_params[0]}\n"+builtin_suffix
        elif _fncname == "yield":
            if _must_return:
                raise CompilerException("\"yield\" does not return.")
            if len(_params) != 0:
                raise CompilerException(
                    "\"yield\" procedure requires exactly zero parameters.")
            res_code += builtin_prefix+f"yield\n"+builtin_suffix
        elif _fncname == "hcf":
            if _must_return:
                raise CompilerException("\"hcf\" does not return.")
            if len(_params) != 0:
                raise CompilerException(
                    "\"hcf\" procedure requires exactly zero parameters.")
            res_code += builtin_prefix+f"hcf\n"+builtin_suffix
        elif _fncname == "select":
            if len(_params)!=3:
                raise CompilerException("\"select\" functions requires exactly three parameters.")
            res_code += builtin_prefix+f"select {_res} {_params[0]} {_params[1]} {_params[2]}\n"+builtin_suffix
        
        # dynamic device access (also batch (expression as hashnumber) and reagent!)
        # elif _fncname.startswith("set_"):

        # not builtin function
        else:
            # call method to get asm to push all used registers (occupied and for variables here)
            (blid, nparams, defaults), returns = _context.get_callable_info(_fncname, _must_return)  # must return is True only for now must be parameter for this function here and only be False for id expressions
            res_code=ProgramDatabase.annotate(f"# call {_fncname}\n")  # first line of function must push ra since its used for the return value
            
            if not ((nparams <= (len(_params)+len(defaults))) and (nparams>=len(_params))):
                raise CompilerException(f"Wrong amount of parameters for function \"{_fncname}\".")

            # push registers used by caller
            res_code+=ProgramDatabase.annotate("# Save used registers that are used\n# within the current block and the called function.\n")
            res_code+=f"$placeholder_push_{len(reserve_hook)}\n"
            # current position + 1 will be pushed by function (in ra before that at the beginning due to jal)  
            # push parameters (make sure those dont get saved before with _reserved_registers)
            for p in _params+defaults[:nparams-len(_params)]:
                res_code+=f"push {p}\n"

            # actual call
            res_code+=f"jal callable_{blid}\n"
            
            if returns:
                # pop result in ra
                res_code+="pop ra\n"

            # pop registers used by caller
            res_code+=ProgramDatabase.annotate("# Recover registers.\n")
            res_code += f"$placeholder_pop_{len(reserve_hook)}\n"
            if returns:
                # move result from ra to result register
                res_code+=f"move {_res} ra\n"
            reserve_hook.append((_reserved_registers, blid, _res if returns else None))  # are placeholder registerslots
        return res_code

    @staticmethod
    def op_add(_res, _param1, _param2=None, *, returns):
        if _param2:
            return f"add {_res} {_param1} {_param2}\n"
        else:
            return f"move {_res} {_param1}\n"

    @staticmethod
    def op_sub(_res, _param1, _param2=None, *, returns):
        if _param2:
            return f"sub {_res} {_param1} {_param2}\n"
        else:
            return f"sub {_res} 0 {_param1}\n"

    @staticmethod
    def op_div(_res, _param1, _param2, *, returns):
        return f"div {_res} {_param1} {_param2}\n"

    @staticmethod
    def op_mul(_res, _param1, _param2, *, returns):
        return f"mul {_res} {_param1} {_param2}\n"
    
    @staticmethod
    def op_or(_res, _param1, _param2, *, returns):
        return f"or {_res} {_param1} {_param2}\n"

    @staticmethod
    def op_and(_res, _param1, _param2, *, returns):
        return f"and {_res} {_param1} {_param2}\n"

    @staticmethod
    def op_not(_res, _param1, *, returns):
        return f"nor {_res} 0 {_param1}\n"

    @staticmethod
    def op_xor(_res, _param1, _param2, *, returns):
        return f"xor {_res} {_param1} {_param2}\n"
    
    @staticmethod
    def op_eq(_res, _param1, _param2, *, returns):
        return f"seq {_res} {_param1} {_param2}\n"

    @staticmethod
    def op_neq(_res, _param1, _param2, *, returns):
        return f"sne {_res} {_param1} {_param2}\n"

    @staticmethod
    def op_lt(_res, _param1, _param2, *, returns):
        return f"sgt {_res} {_param2} {_param1}\n"

    @staticmethod
    def op_gt(_res, _param1, _param2, *, returns):
        return f"sgt {_res} {_param1} {_param2}\n"
    
    @staticmethod
    def op_lte(_res, _param1, _param2, *, returns):
        return f"sge {_res} {_param2} {_param1}\n"

    @staticmethod
    def op_gte(_res, _param1, _param2, *, returns):
        return f"sge {_res} {_param1} {_param2}\n"

    @staticmethod
    def op_mod(_res, _param1, _param2, *, returns):
        return f"mod {_res} {_param1} {_param2}\n"

    @staticmethod
    def op_asg(_res, _param1, _param2, *, returns):
        if (_res != _param1):
            res = f"move {_param1} {_param2}\n"
            if returns: res+=f"move {_res} {_param2}\n"
            return res
        else:
            return  f"move {_res} {_param2}\n"
    
    @staticmethod
    def op_addasg(_res, _param1, _param2, *, returns):
        res =  f"add {_param1} {_param1} {_param2}\n"
        if returns: res+=f"move {_res} {_param1}\n"
        return res
            
    @staticmethod
    def op_subasg(_res, _param1, _param2, *, returns):
        res =  f"sub {_param1} {_param1} {_param2}\n"
        if returns: res+=f"move {_res} {_param1}\n"
        return res

    @staticmethod
    def op_mulasg(_res, _param1, _param2, *, returns):
        res =  f"mul {_param1} {_param1} {_param2}\n"
        if returns: res+=f"move {_res} {_param1}\n"
        return res

    @staticmethod
    def op_divasg(_res, _param1, _param2, *, returns):
        res =  f"div {_param1} {_param1} {_param2}\n"
        if returns: res+=f"move {_res} {_param1}\n"
        return res
    
    @staticmethod
    def op_modasg(_res, _param1, _param2, *, returns):
        res =  f"mod {_param1} {_param1} {_param2}\n"
        if returns: res+=f"move {_res} {_param1}\n"
        return res

    @staticmethod
    def op_andasg(_res, _param1, _param2, *, returns):
        res =  f"and {_param1} {_param1} {_param2}\n"
        if returns: res+=f"move {_res} {_param1}\n"
        return res
    
    @staticmethod
    def op_orasg(_res, _param1, _param2, *, returns):
        res =  f"or {_param1} {_param1} {_param2}\n"
        if returns: res+=f"move {_res} {_param1}\n"
        return res
    
    @staticmethod
    def op_shl(_res, _param1, _param2, *, returns):
        raise CompilerException("Shift Operations are not implemented in Stationeers")
    
    @staticmethod
    def op_shr(_res, _param1, _param2, *, returns):
        raise CompilerException("Shift Operations are not implemented in Stationeers")
    
    @staticmethod
    def op_neg(_res, _param1, _param2, *, returns):
        raise CompilerException("Bitwise Operations are not implemented in Stationeers")
    
    @staticmethod
    def op_bwand(_res, _param1, _param2, *, returns):
        raise CompilerException("Bitwise Operations are not implemented in Stationeers")
    
    @staticmethod
    def op_bwor(_res, _param1, _param2, *, returns):
        raise CompilerException("Bitwise Operations are not implemented in Stationeers")
    
    @staticmethod
    def op_bwxor(_res, _param1, _param2, *, returns):
        raise CompilerException("Bitwise Operations are not implemented in Stationeers")
    
    @staticmethod
    def op_inc(_res, _param1, *, returns):
        res = f"add {_param1} {_param1} 1\n"
        if returns: res+=f"move {_res} {_param1}\n"
        return res

    @staticmethod
    def op_dec(_res, _param1, *, returns):
        res = f"sub {_param1} {_param1} 1\n"
        if returns: res+=f"move {_res} {_param1}\n"
        return res

    @staticmethod
    def op_id(_res, _param1, *, returns):
        if not returns: return ""
        return f"move {_res} {_param1}\n"

    @staticmethod
    def op_dot(*_, returns):
        raise UnexpectedException("Called op_dot.")
        # return ""  # is'nt supposed to do anything
    
    class DeviceAccessData:
        def __init__(self, dev_name=None, prop=None, slot=None, func=None, dynamic=False):
            func_choices_batch = ["Average", "Sum", "Minimum", "Maximum"]
            func_choices_reagent = ["Contents", "Required", "Recipe"]
            self.batch = False
            self.reagent = False
            if func: 
                if func in func_choices_batch:
                    self.batch = True
                elif prop in func_choices_reagent:  # other way around for reagents like somedev.Contents.Iron
                    self.reagent = True
                else:
                    choice_str = str(func_choices_batch+func_choices_reagent)[1:-1].replace('\'', '')
                    raise CompilerException(f"Batch/Reagent mode {func} doesn't exist. Choices: {choice_str}")
            self.dev_name = dev_name
            self.prop = prop
            self.slot = slot
            self.func = func
            self.dynamic = dynamic


        def get_asm(self, reg, write_to_name, read_from_name = True):
            if (self.slot is not None) and self.func:
                raise CompilerException("Batch device access with slots is not supported by Stationeers.")
            prefix = ""
            suffix = ""
            if read_from_name:
                if self.batch:
                    prefix = f"lb $r{reg} $name_r{self.dev_name} {self.prop} {self.func}\n"
                elif self.reagent:
                    prefix = f"lr $r{reg} d$name_r{self.dev_name} {self.prop} {self.func}\n"
                else:
                    if self.slot is not None:
                        # special case slot is constant must be handled
                        prefix = f"ls $r{reg} d$name_r{self.dev_name} {self.slot} {self.prop}\n"
                    else:
                        if self.prop == "DeviceIsSet":
                            prefix = f"sdse $r{reg} d$name_r{self.dev_name}\n"
                        else:
                            prefix = f"l $r{reg} d$name_r{self.dev_name} {self.prop}\n"
                
            if write_to_name:
                if self.batch or self.reagent:
                    raise CompilerException("Can't use batch/reagent function when writing.")
                else:
                    if self.slot is not None:
                        raise CompilerException("Can't write to slot.")
                    else:
                        if self.prop == "DeviceIsSet":
                           raise CompilerException("Can't write to DeviceIsSet.")
                        suffix = f"$device_set{self.dev_name} $device_set_prefix{self.dev_name}$name_r{self.dev_name} {self.prop} $r{reg}\n"  # device set must be subsituded with s for normal device and sb for batch devices

            return prefix, suffix
        

    def full_dependence_solver(self, expr, graph):
        # This function builds compilerutil.ExprGraph graph from data yielded by Expression-Syntax expr including subexpressions

        # calls is list with tuples ("operator_name", [parameterlist...]) already in the correct evaluation order
        # parameterlist consists out of the Tokens that get combined in the operation or an int which is the id of a previous result
        calls = expr.get_calls()

        # used to spot unconnected parts of expression e.g. 1+1 1+1 second 1+1 would be unconnected (unreachable von graph)
        used_tokens = set()
        tokens_in_calls = set(itertools.chain(*list(map(lambda c: c[1], calls)))) | set(map(lambda c: c[2], calls))
        tokens_in_calls = set(filter(lambda e: type(e) is not int, tokens_in_calls))

        def crawler(calls, idx):
            # rekursive function used to build graph works on free variable graph

            # add node to graph of operation and move to it
            graph.append(calls[idx][0])
            
            # mark token as used
            used_tokens.add(calls[idx][2])

            instance_root = graph.get_iterator()  # the node in the graph of the current operation

            # iterate over parameters of operation
            for p in calls[idx][1]:
                # reset iterator to current operation
                graph.set_iterator(instance_root)

                # previous operation
                if type(p) is int:
                    # continue building at this operation
                    crawler(calls, p)
                
                # operation in braces
                elif isinstance(p, Braces):
                    # mark token as used
                    used_tokens.add(p)

                    subexpr = find_by_index(expr.get_subsyntaxes(), 0, p)
                    if subexpr == -1:
                        raise CompilerException("Unresolved subsyntax of type Braces.")
                    # create subexpression-branch
                    self.full_dependence_solver(expr.get_subsyntaxes()[subexpr][1], graph)
                
                # indexing operation
                elif isinstance(p, Indexing):
                    # mark token as used
                    used_tokens.add(p)

                    subexpr = find_by_index(expr.get_subsyntaxes(), 0, p)
                    if subexpr == -1:
                        raise CompilerException("Unresolved subsyntax of type Indexing.")
                    graph.append(IndexingPlaceholder(p.get_name()))
                    # create subexpression-branch
                    self.full_dependence_solver(expr.get_subsyntaxes()[subexpr][1], graph)
                
                # function call
                elif isinstance(p, FunctionCall):
                    # mark token as used
                    used_tokens.add(p)

                    subexpr = find_by_index(expr.get_subsyntaxes(), 0, p)
                    if subexpr == -1:
                        raise CompilerException("Unresolved subsyntax of type FunctionCall.")

                    # create temporary ExprGraph for functioncall and safe result in designated register of the current node graph.get_iterator().reg
                    # sub_graph = ExprGraph(graph.get_iterator().reg, expr.get_subsyntaxes()[subexpr][0], d_level=0, hull=graph.get_iterator().hull+1)
                    sub_graph = ExprGraph(expr.get_subsyntaxes()[subexpr][0])
                    sub_graph.append(expr.get_subsyntaxes()[subexpr][0])  # append FunctionCall token
                    func_root = sub_graph.get_iterator()
                    if expr.get_subsyntaxes()[subexpr][1]:  # function has nonempty parameterlist
                        # iterate over parameterlist of function
                        for _, e in expr.get_subsyntaxes()[subexpr][1].get_parameter_syntaxes():  
                            # for each of the parameters attach parameter-expression branch to function node
                            self.full_dependence_solver(e, sub_graph)
                            sub_graph.set_iterator(func_root)
                    
                    # add temporary graph (with the functioncall) to the main graph
                    graph.append_graph(sub_graph)
                
                # Literal-Token
                else:
                    # mark token as used
                    used_tokens.add(p)

                    # just added and graph-branch ends there
                    graph.append(p)
        
        crawler(calls, -1)  # start from last element because thats the last operation executed and therefore the root of the ExprGraph
        if not used_tokens == tokens_in_calls:
            raise CompilerException("Stray atoms in expression.")
        # go to root of graph
        graph.reset_iterator()
        return graph

    def __init__(self, _context, _code, _idx_line, _actual_line = None, _must_return_override = False):
        # _actual_line used for _context and maybe error messages
        if not _actual_line:
            _actual_line = _idx_line
        super().__init__(_context, _idx_line)
        _context.set_compiler_position(_actual_line)
        self.func_dict = {
            "+": ExpressionCode.op_add,
            "-": ExpressionCode.op_sub,
            "*": ExpressionCode.op_mul,
            "/": ExpressionCode.op_div,
            "||": ExpressionCode.op_or,
            "&&": ExpressionCode.op_and,
            "!": ExpressionCode.op_not,
            "^": ExpressionCode.op_bwxor,
            "~": ExpressionCode.op_neg,
            "|": ExpressionCode.op_bwor,
            "&": ExpressionCode.op_bwand,
            "==": ExpressionCode.op_eq,
            "!=": ExpressionCode.op_neq,
            "<": ExpressionCode.op_lt,
            ">": ExpressionCode.op_gt,
            "<=": ExpressionCode.op_lte,
            ">=": ExpressionCode.op_gte,
            "%": ExpressionCode.op_mod,
            "++": ExpressionCode.op_inc,
            "--": ExpressionCode.op_dec,
            "=": ExpressionCode.op_asg,
            "+=": ExpressionCode.op_addasg,
            "-=": ExpressionCode.op_subasg,
            "*=": ExpressionCode.op_mulasg,
            "/=": ExpressionCode.op_divasg,
            "%=": ExpressionCode.op_modasg,
            "&&=": ExpressionCode.op_andasg,
            "||=": ExpressionCode.op_orasg,
            "id": ExpressionCode.op_id,
            ".": ExpressionCode.op_dot
        }
        self._end_line = _idx_line+1
        if not isinstance(_code[_idx_line], Expression):
            raise CompilerException("expression-subcode must be initiated by an expression syntax.")

        expr = _code[_idx_line]
        expr_graph = self.full_dependence_solver(expr, ExprGraph("root"))
        expr_graph.reset_iterator()
        expr_graph.eval_registers()
        expr_graph.move_forward(0)
        name_request_data = []

        complete_code = ""

        reserve_hook = []  # for function/procedure calls

        def crawler_fnc(node, _):
            nonlocal complete_code
            if isinstance(node.op, FunctionCall) or (type(node.op) is str) and (node.op!="."):
                # parameter handling
                op_params = []  # parameters for function/operator are either register placeholders like $r# variable register placeholders like $name_r# or plain numbers
                placeholders_prefix = []  # used for loading variables from var_stack executed directly before operation asm (not before whole expression!)
                placeholders_suffix = []  # used for setting variables in var_stack executed directly before operation asm (not after whole expression!)
                operator_code = ""
                for j, p in enumerate(node.params):
                    if isinstance(p.op, IndexingPlaceholder):
                        raise CompilerException("Not allowed device access.")
                    
                    if isinstance(p.op, NumberLiteral):  # plain number parameter
                        if (j == 0) and (type(node.op) is str) and (node.op in assignment_operators):  # first parameter of assignment operations can't be numbers (can't assign to numbers)
                            raise CompilerException("Can't write to number literals.")
                        op_params.append(f"{p.op.get_value():.16f}".rstrip("0"))  # append plain number parameter must be fixed point not scientific (or general that could result in scientific) notation
                    
                    elif (type(p.op) is str) and (p.op == "."):
                        if (type(node.op) is str) and (node.op == "."): 
                            continue  # not root
                        
                        write_to_name = False
                        read_from_name = True
                        if (j==0) and (type(node.op) is str) and (node.op in assignment_operators):  # determine if to variable is written (in case of assignments since then requires setting variables in var_stack after evaluation)
                            write_to_name = True
                            if node.op == "=":  # only for normal assignment
                                read_from_name = False
                        
                        # DeviceAccessData first parameter is replacement value in $name_r[replacement value] replacement value = next added element index in name_request_data
                        # DeviceAccessData(replacement_value, attribute, slot, function)

                        if isinstance(p.params[0].op, VarName):
                            if isinstance(p.params[1].op, VarName):
                                # normal device access device.attribute which means either Device or also Batch Device if written to
                                dev_acc = ExpressionCode.DeviceAccessData(len(name_request_data), p.params[1].op.get_name(), None, None)
                                if write_to_name:
                                    name_request_data.append((p.params[0].op.get_name(), False, None, None, (ProgramDatabase.NType.Device, ProgramDatabase.NType.Batch_Device, ProgramDatabase.NType.Variable, ProgramDatabase.NType.Constant)))
                                else:
                                    name_request_data.append((p.params[0].op.get_name(), False, None, None, (ProgramDatabase.NType.Device, ProgramDatabase.NType.Variable, ProgramDatabase.NType.Constant)))  # reading from batch device requires func

                            else:
                                raise CompilerException("Not allowed device access.")
                        
                        # must also allow batch devices
                        elif isinstance(p.params[0].op, IndexingPlaceholder):
                            if isinstance(p.params[1].op, VarName):
                                # slot access device[slot].attribute
                                if isinstance(p.params[0].reg, VarName):  # in case slot is constant and not integer
                                    # access with constant +1 in first parameter important to note
                                    dev_acc = ExpressionCode.DeviceAccessData(len(name_request_data)+1, p.params[1].op.get_name(), f"$name_r{len(name_request_data)}", None)
                                    name_request_data.append((p.params[0].reg.get_name(), False, None, None, ProgramDatabase.NType.Constant))
                                else:
                                    dev_acc = ExpressionCode.DeviceAccessData(len(name_request_data), p.params[1].op.get_name(), p.params[0].reg, None)
                                name_request_data.append((p.params[0].op.get_name(), False, None, None, (ProgramDatabase.NType.Device, ProgramDatabase.NType.Variable, ProgramDatabase.NType.Constant)))
                            else:
                                raise CompilerException("Not allowed device access.")
                        
                        elif (type(p.params[0].op) is str) and (p.params[0].op == "."):
                            if isinstance(p.params[1].op, VarName) and isinstance(p.params[0].params[0].op, VarName) and isinstance(p.params[0].params[1].op, VarName):
                                # batch device access batch_device.attribute.function or reagent (only reading in both cases)
                                dev_acc = ExpressionCode.DeviceAccessData(len(name_request_data), p.params[0].params[1].op.get_name(), None, p.params[1].op.get_name())
                                if dev_acc.batch:
                                    name_request_data.append((p.params[0].params[0].op.get_name(), False, None, None, ProgramDatabase.NType.Batch_Device))
                                elif dev_acc.reagent:
                                    name_request_data.append((p.params[0].params[0].op.get_name(), False, None, None, (ProgramDatabase.NType.Device, ProgramDatabase.NType.Variable, ProgramDatabase.NType.Constant)))
                                else:
                                    raise CompilerException("This shouldn't happen.")
                            elif isinstance(p.params[1].op, VarName) and isinstance(p.params[0].params[0].op, IndexingPlaceholder) and isinstance(p.params[0].params[1].op, VarName):
                                raise CompilerException("Slotted batch-device access not possible through IC10 assembler yet. This is just an placeholder.")
                                # batch device access batch_device.attribute.function or reagent (only reading in both cases)
                                if isinstance(p.params[0].params[0].reg, VarName):  # in case slot is constant and not integer
                                    # access with constant +1 in first parameter important to note
                                    dev_acc = ExpressionCode.DeviceAccessData(len(name_request_data)+1, p.params[0].params[1].op.get_name(), f"$name_r{len(name_request_data)}", p.params[1].op.get_name())
                                    name_request_data.append((p.params[0].reg.get_name(), False, None, None, ProgramDatabase.NType.Constant))
                                else:
                                    dev_acc = ExpressionCode.DeviceAccessData(len(name_request_data), p.params[0].params[1].op.get_name(), p.params[0].params[0].reg, p.params[1].op.get_name())
                                
                                if dev_acc.batch:
                                    name_request_data.append((p.params[0].params[0].op.get_name(), write_to_name, None, None, ProgramDatabase.NType.Batch_Device))
                                elif dev_acc.reagent:
                                    raise CompilerException("Can't use batch reagent access.")
                                else:
                                    raise CompilerException("This shouldn't happen.")
                            else:
                                raise CompilerException("Not allowed device access.")

                        else:
                            raise CompilerException("Not allowed device access.")
                        
                        
                        acc_asm = dev_acc.get_asm(p.reg, write_to_name, read_from_name) 
                        
                        placeholders_prefix.append(acc_asm[0])
                        placeholders_suffix.append(acc_asm[1])
                        op_params.append(f"$r{p.reg}")
                    
                    elif isinstance(p.op, VarName):  
                        # variable name
                        write_to_name = False
                        if (j==0) and (type(node.op) is str) and (node.op in assignment_operators):  # determine if to variable is written (in case of assignments since then requires setting variables in var_stack after evaluation)
                            write_to_name = True
                        
                        if ((type(node.op) is str) and node.op == "."):
                            continue  # part of device access
                        else:
                            op_params.append(f"$name_r{len(name_request_data)}")  # placeholder for variable register (replaced by data from ProgramData::name_acess)
                            if not( isinstance(node.op, str) and (node.op == "=") and (j==0)):  # not needed for assignments a=0 -> don't need to load a
                                placeholders_prefix.append(f"$get_name{len(name_request_data)}\n")  # placeholder for loading from variable stack operations
                            if write_to_name:
                                placeholders_suffix.append(f"$set_name{len(name_request_data)}\n")  # placeholder for writing to variable stack operations (only needed for variables where it is written to)
                            
                            # name use for determining variable with knowledge of current blockid (programmdatabase state determines that)
                            # write_to_name required since those variables are prioritized for living in reserved registers
                            # p.reg in case no reserved registers available (from varstack will be written into p.reg)
                            # node.reg in case no reserved registers available (into varstack will be written from node.reg since there is the result) 
                            name_request_data.append((p.op.get_name(), write_to_name, p.reg, node.reg, (ProgramDatabase.NType.Variable, ProgramDatabase.NType.Constant, ProgramDatabase.NType.Device, ProgramDatabase.NType.Batch_Device)))  # data for ProgramData::name_acess 
                    else:
                        if (j == 0) and (type(node.op) is str) and (node.op in assignment_operators):  # first parameter of assignment operations can't be expressions (can't assign to expressions)
                            raise CompilerException("Can't write to expressions.")
                        op_params.append(f"$r{p.reg}")  # simple reserved register for expression placeholder parameter
                
                operator_code += "".join(placeholders_prefix)  # add prefix

                if node.root is None:
                    must_return = _must_return_override
                else: 
                    must_return = not((node.root.op == "root") or (node.root.op == "id") and (node.root.root.op == "root")) or  _must_return_override  # procedures (must_return == False) can only be part of id operations (final part of the expression is procedure like foo(x+y,1,a) not like 1+foo(...))
                # nuances when using functions
                if isinstance(node.op, FunctionCall):
                    # functions need to allways clean stack therefore no operations can be ommitted even if not return needed
                    operator_code += ExpressionCode.function_call(_context, node.op.get_name(), "$r"+str(node.reg), op_params, must_return, node.reserved_registers, reserve_hook)
                
                # default (operator)
                else:
                    operator_code += self.func_dict[node.op]("$r"+str(node.reg), *op_params, returns=must_return)  # normal operator asm

                operator_code+="".join(placeholders_suffix)  # add suffix
                
                complete_code+=operator_code
        expr_graph.reversed_crawler(crawler_fnc, expr_graph.get_iterator())  # don't start at root

        register_translation = _context.occupy_registers(expr_graph.used_registers())
        self._return_reg = register_translation[0][0]  # always first entry
        self.__rawexpr = "".join([t.get_rawstring() for t in _code[_idx_line].get_token_family()])
        
        name_access_tbl, init_asm = _context.name_access(name_request_data)  # Format: list of (reg, set_asm, get_asm) index is the number in placeholders
        
        self._code = init_asm + complete_code
        self._code = ProgramDatabase.annotate(f"# expression: r{self.get_result_reg()}={{" + self.get_rawexpr() + "}\n") + register_translation[1] + self._code  # add initialization of used registers
        
        for i, (reserved_reg, blid, rr) in enumerate(reserve_hook):
            # all regs in from reserve_hook pre replacement
            reserved_reg = set(register_translation[0][r] for r in reserved_reg)
            if rr is not None:
                rr = register_translation[0][int(rr[2:])]  # will start with $r
            before_code, after_code = _context.prepare_jump(blid, reserved_reg, rr)
            self._code = re.sub(r"\$placeholder_push_" + str(i)+"(?!\d+)" + "\n", before_code, self._code)
            self._code = re.sub(r"\$placeholder_pop_" + str(i)+"(?!\d+)" + "\n", after_code, self._code)
        
        _context.free_registers()

        
        # replace $name_r# with registers as well as the placeholders
        for i, (reg, set_asm, get_asm, name_type) in enumerate(name_access_tbl):
            # if any(name_type[1:]):  # is device
            self._code = re.sub(r"\$device_set"+str(i)+"(?!\d+)", "sb" if name_type[2] else "s", self._code)
            self._code = re.sub(r"\$device_set_prefix"+str(i)+"(?!\d+)", "" if name_type[2] else "d", self._code)
            self._code = re.sub(r"\$name_r"+str(i)+"(?!\d+)", reg, self._code)
            self._code = re.sub(r"\$get_name" + str(i)+"(?!\d+)" + "\n", get_asm, self._code)
            self._code = re.sub(r"\$set_name" + str(i)+"(?!\d+)" + "\n", set_asm, self._code)
        
        for i, reg in enumerate(register_translation[0]):
            self._code = re.sub(r"\$r"+str(i)+"(?!\d+)", f"r{reg}", self._code)
        
        # optimize code by replacing pointless lines
        if ProgramDatabase.CODE_OPTIMIZATION:
            for pat, repl in ExpressionCode.pointless_lines:
                newcode = re.sub(pat, repl, self._code)
                while self._code!=newcode:
                    self._code = newcode
                    newcode = re.sub(pat, repl, newcode)

    def get_result_reg(self):
        return self._return_reg

    def get_rawexpr(self):
        return self.__rawexpr

class VariableDeclarationCode(CodeGen):
    _init_syntax = VariableDeclarationSyntax

    def __init__(self, _context, _code, _idx_line, _actual_line = None):
        if not _actual_line:
            _actual_line = _idx_line
        super().__init__(_context, _idx_line)
        _context.set_compiler_position(_actual_line)
        if not isinstance(_code[_idx_line], VariableDeclarationSyntax):
            raise CompilerException("Variable-subcode must be initiated by an variable declaration syntax.")
        self._code = ""
        init = _code[_idx_line].get_init_expr()
        add_name_data = _context.add_name(_code[_idx_line].get_name(), ProgramDatabase.NType.Variable) # Format: register, var_stacklocation, init_code
        self._code += add_name_data[2]
        if add_name_data[0] is not None:
            self._code = ProgramDatabase.annotate(f"# init new var{{{_code[_idx_line].get_name()}}}, blk{{{_context._block_iter.blid}}} in r{add_name_data[0]}\n") + self._code
        else:
            self._code = ProgramDatabase.annotate(f"# init new var{{{_code[_idx_line].get_name()}}}, blk{{{_context._block_iter.blid}}} in stack[{add_name_data[1]}]\n") + self._code
        if init:
            init_expr = ExpressionCode(_context, [init], 0, _actual_line, _must_return_override=True)  # otherwise id expression -> procs would be allowed
            self._code+=init_expr.get_code()
            if add_name_data[0] is not None:
                self._code += f"move r{add_name_data[0]} r{init_expr.get_result_reg()}\n"
            else:  # if global variable automatically this (through ProgramDatabase.add_name)
                self._code += ProgramDatabase.annotate(f"# prep sp for var{{{_code[_idx_line].get_name()}}}\n")
                self._code += "move ra sp\n"
                self._code += f"move sp {add_name_data[1]}\n" 
                self._code += f"push r{init_expr.get_result_reg()}\n"
                self._code += "move sp ra\n"
        self._end_line = _idx_line+1
        self.__rawdecl = " ".join([t.get_rawstring() for t in _code[_idx_line].get_token_family()])

        if _context._block_iter.blid == 0:  # is global
            _context._globals_init.append(self._code)
            self._code = ""  # because won't be executed anyway

    def get_rawdecl(self):
        return self.__rawdecl


class ConstantDeclarationCode(CodeGen):
    _init_syntax = ConstantDeclarationSyntax

    def __init__(self, _context, _code, _idx_line):
        super().__init__(_context, _idx_line)
        if not isinstance(_code[_idx_line], ConstantDeclarationSyntax):
            raise CompilerException("constant-subcode must be initiated by a constant declaration syntax.")
        self._code = ProgramDatabase.annotate(f"# new const{{{_code[_idx_line].get_name()}}}={_code[_idx_line].get_value()}\n")
        add_name_data = _context.add_name(_code[_idx_line].get_name(), ProgramDatabase.NType.Constant, _code[_idx_line].get_value())


class DeviceDeclarationCode(CodeGen):
    _init_syntax = DeviceDeclarationSyntax

    def __init__(self, _context, _code, _idx_line):
        super().__init__(_context, _idx_line)
        if not isinstance(_code[_idx_line], DeviceDeclarationSyntax):
            raise CompilerException("device-subcode must be initiated by a device declaration syntax.")
        self._code = ProgramDatabase.annotate(f"# new device{{{_code[_idx_line].get_name()}}}=d{_code[_idx_line].get_value()}\n")
        add_name_data = _context.add_name(_code[_idx_line].get_name(), ProgramDatabase.NType.Device, _code[_idx_line].get_value())


class BatchDeviceDeclarationCode(CodeGen):
    _init_syntax = BatchDeviceDeclarationSyntax

    def __init__(self, _context, _code, _idx_line):
        super().__init__(_context, _idx_line)
        if not isinstance(_code[_idx_line], BatchDeviceDeclarationSyntax):
            raise CompilerException("batch device-subcode must be initiated by a batch device declaration syntax.")
        self._code = ProgramDatabase.annotate(f"# new batch device{{{_code[_idx_line].get_name()}}}=d{_code[_idx_line].get_value()}\n")
        add_name_data = _context.add_name(_code[_idx_line].get_name(), ProgramDatabase.NType.Batch_Device, _code[_idx_line].get_value())


class BreakCode(CodeGen):
    _init_syntax = BreakSyntax

    def __init__(self, _context, _code, _idx_line):
        super().__init__(_context, _idx_line)
        if not isinstance(_code[_idx_line], BreakSyntax):
            raise CompilerException("break-subcode must be initiated by a break declaration syntax")
        self._code = ProgramDatabase.annotate(f"# break\n")
        bdata = _context.get_current_block()
        while bdata.btype not in (ProgramDatabase.BType.While_, ProgramDatabase.BType.For_):
            bdata = bdata.parent
            if bdata is None:
                raise CompilerException("break can only be placed within a loop.")
        
        snapshot = _context.make_snapshot()
        revert_code = _context.revert_state(_context.current_loop_break_snapshot[-1], snapshot)
        self._code += revert_code

        if bdata.btype == ProgramDatabase.BType.While_:
            self._code+= f"j while_{bdata.info}_end\n"
        elif bdata.btype == ProgramDatabase.BType.For_:
            self._code+= f"j for_{bdata.info}_end\n"


class ContinueCode(CodeGen):
    _init_syntax = ContinueSyntax

    def __init__(self, _context, _code, _idx_line):
        super().__init__(_context, _idx_line)
        if not isinstance(_code[_idx_line], ContinueSyntax):
            raise CompilerException("continue-subcode must be initiated by a continue declaration syntax")
        self._code = ProgramDatabase.annotate(f"# continue\n")
        bdata = _context.get_current_block()
        while bdata.btype not in (ProgramDatabase.BType.While_, ProgramDatabase.BType.For_):
            bdata = bdata.parent
            if bdata is None:
                raise CompilerException("break can only be placed within a loop.")
        snapshot = _context.make_snapshot()
        revert_code = _context.revert_state(_context.current_loop_continue_snapshot[-1], snapshot)
        self._code += revert_code
        if bdata.btype == ProgramDatabase.BType.While_:
            self._code+= f"j while_{bdata.info}_start\n"
        elif bdata.btype == ProgramDatabase.BType.For_:
            self._code+= f"j for_{bdata.info}_iter\n"


class ReturnCode(CodeGen):
    _init_syntax = ReturnSyntax

    def __init__(self, _context, _code, _idx_line):

        # return doesn't need to revert state like loops, continue, break and if-statements since var_stack is guranteed to not overlap (never freed after function) and registers get pushed

        super().__init__(_context, _idx_line)
        if not isinstance(_code[_idx_line], ReturnSyntax):
            raise CompilerException(
                "return-subcode must be initiated by a return syntax")
        self._code = ProgramDatabase.annotate(f"# return\n")
        bdata = _context.get_current_block()
        if bdata is None:
            raise CompilerException("Can only return from an function or procedure.")
        
        while bdata.btype not in [ProgramDatabase.BType.Func, ProgramDatabase.BType.Proc]:
            bdata = bdata.parent
            if bdata is None:
                raise CompilerException("Can only return from an function or procedure.")
        
        if bdata.btype == ProgramDatabase.BType.Func:
            if not _code[_idx_line].get_return_expression():
                raise CompilerException("Function must have an return value.")
            ret_expr = ExpressionCode(_context, [_code[_idx_line].get_return_expression()], 0, _idx_line, _must_return_override=True)
            self._code += ret_expr.get_code()
            self._code += "pop ra\n"
            self._code += f"push r{ret_expr.get_result_reg()}\n"
            self._code += "beqz 0 ra\n"
        elif bdata.btype == ProgramDatabase.BType.Proc:
            if _code[_idx_line].get_return_expression():
                raise CompilerException("Procedures can't have an return value.")
            self._code += "pop ra\n"
            self._code += "beqz 0 ra\n"
        else:
            raise CompilerException("return statement not allowed at this position.")


class FuncCode(CodeGen):
    _init_syntax = FuncSyntax

    def __init__(self, _context, _code, _idx_line):
        super().__init__(_context, _idx_line)
        if not isinstance(_code[_idx_line], FuncSyntax):
            raise CompilerException(
                "func-subcode must be initiated by an func-syntax.")
        parameter_names = _code[_idx_line].get_funcparameters()
        defaults = _code[_idx_line].get_defaults()
        # register functionname
        blockid = _context.generate_blid()

        # what is add_name_data???
        add_name_data = _context.add_name(_code[_idx_line].get_name(), ProgramDatabase.NType.Function, (blockid, len(parameter_names), defaults))
        start_idx = _idx_line+1
        under_blocks = 1
        for i, syntax in enumerate(_code[start_idx:]):
            if isinstance(syntax, blocksyntax):
                under_blocks += 1
            if isinstance(syntax, EndSyntax):
                if under_blocks > 1:
                    under_blocks -= 1
                    continue
                self._end_line = i+1+_idx_line+1
                break
        else:
            raise CompilerException("function body never ended.")
        func_block = _context.start_block(start_idx, ProgramDatabase.BType.Func)  # declare paramters as variables within the block
        name_data_params = []
        for param in parameter_names:
            *nd, _ = _context.add_name(param, ProgramDatabase.NType.Variable, revfreg=True)  # last parameter is always ""
            name_data_params.append(nd)
        self._func_body = create_asm_code(_code, ProgramDatabase.BType.Func, start_idx, self._end_line-1, database=_context, handle_blocks=False)
        _context.end_block(self._end_line)
        param_annotate = ','.join([f'r{name_data_params[i][0]}=' + parameter_names[i] for i in range(len(name_data_params))])
        self._code = _context.annotate(f"# func{{{_code[_idx_line].get_name()}}}({param_annotate})\n")
        # branchmarker for function func_id:
        self._code += f"callable_{blockid}:\n" 
        # pop params
        for reg, slot in reversed(name_data_params):  # get recoverd in reversed order like stdcall
            if reg is not None:
                self._code+=f"pop r{reg}\n"
            else:
                raise CompilerException("No register position found for function parameter.")
        self._code+="push ra\n"  # safe return to line (stored in ra which could be used for other purposes in function)
        
        # special considerations for recursive calls (at first there might not be all touched registers known)
        for i, (to_save, already_considered) in enumerate(_context._recursive_call_hook):
            touched_registers = set().union(*list(map(lambda ele: ele[1], func_block.registers)))
            registers = to_save.intersection(touched_registers - already_considered)
            get_asm = ""
            for r in registers:
                get_asm+=f"push r{r}\n"

            set_asm = ""
            for r in reversed(list(registers)):
                set_asm+=f"pop r{r}\n"
            
            self._func_body = re.sub(r"\$recursive_placeholder_push_" + str(i)+"(?!\d+)" + "\n", get_asm, self._func_body)
            self._func_body = re.sub(r"\$recursive_placeholder_pop_" + str(i)+"(?!\d+)" + "\n", set_asm, self._func_body)
        
        # clean up
        _context._recursive_call_hook = []

        self._code+=self._func_body
        self._code += f"s db Setting -1\ns db On 0\n"



class ProcCode(CodeGen):
    _init_syntax = ProcSyntax

    def __init__(self, _context, _code, _idx_line):
        super().__init__(_context, _idx_line)
        if not isinstance(_code[_idx_line], ProcSyntax):
            raise CompilerException(
                "proc-subcode must be initiated by an proc-syntax.")
        parameter_names = _code[_idx_line].get_funcparameters()
        defaults = _code[_idx_line].get_defaults()
        # register functionname
        blockid = _context.generate_blid()
        add_name_data = _context.add_name(_code[_idx_line].get_name(
        ), ProgramDatabase.NType.Procedure, (blockid, len(parameter_names), defaults))
        start_idx = _idx_line+1
        under_blocks = 1
        for i, syntax in enumerate(_code[start_idx:]):
            if isinstance(syntax, blocksyntax):
                under_blocks += 1
            if isinstance(syntax, EndSyntax):
                if under_blocks > 1:
                    under_blocks -= 1
                    continue

                self._end_line = i+1+_idx_line+1
                break
        else:
            raise CompilerException("procedure body never ended.")
        # declare paramters as variables within the block
        func_block = _context.start_block(start_idx, ProgramDatabase.BType.Proc)
        param_codes = []
        name_data_params = []
        for param in parameter_names:
            # last parameter is always ""
            *nd, _ = _context.add_name(param, ProgramDatabase.NType.Variable, revfreg=True) #  revfreg=True generate less garbage pushes when call
            name_data_params.append(nd)
        self._func_body = create_asm_code(
            _code, ProgramDatabase.BType.Proc, start_idx, self._end_line-1, database=_context, handle_blocks=False)
        _context.end_block(self._end_line)
        param_annotate = ','.join([f'r{name_data_params[i][0]}=' + parameter_names[i] for i in range(len(name_data_params))])
        self._code = _context.annotate(
            f"# proc{{{_code[_idx_line].get_name()}}}({param_annotate})\n")
        self._code += f"callable_{blockid}:\n"
        # branchmarker for function func_id:
        # pop params
        for reg, slot in reversed(name_data_params):  # get recoverd in reversed order like stdcall
            if reg is not None:
                self._code += f"pop r{reg}\n"
            else:
                raise CompilerException(
                    "No register position found for procedure parameter.")
        self._code+="push ra\n"  # safe return to line (stored in ra which could be used for other purposes in function)
        # procedure code

        # special considerations for recursive calls
        for i, (to_save, already_considered) in enumerate(_context._recursive_call_hook):
            touched_registers = set().union(
                *list(map(lambda ele: ele[1], func_block.registers)))
            registers = to_save.intersection(touched_registers - already_considered)
            get_asm = ""
            for r in registers:
                get_asm += f"push r{r}\n"

            set_asm = ""
            for r in reversed(registers):
                set_asm += f"pop r{r}\n"

            self._func_body = re.sub(
                r"\$recursive_placeholder_push_" + str(i)+"(?!\d+)" + "\n", get_asm, self._func_body)
            self._func_body = re.sub(
                r"\$recursive_placeholder_pop_" + str(i)+"(?!\d+)" + "\n", set_asm, self._func_body)

        # clean up
        _context._recursive_call_hook = []

        self._code += self._func_body
        self._code += "pop ra\n"
        self._code += "beqz 0 ra\n"
        
class MainCode(CodeGen):
    _init_syntax = MainSyntax

    def __init__(self, _context, _code, _idx_line):
        super().__init__(_context, _idx_line)
        if not isinstance(_code[_idx_line], MainSyntax):
            raise CompilerException(
                "main-subcode must be initiated by an main-syntax.")
        start_idx = _idx_line+1
        under_blocks = 1
        for i, syntax in enumerate(_code[start_idx:]):
            if isinstance(syntax, blocksyntax):
                under_blocks += 1
            if isinstance(syntax, EndSyntax):
                if under_blocks > 1:
                    under_blocks -= 1
                    continue
                self._end_line = i+1+_idx_line+1
                break
        else:
            raise CompilerException("main body never ended.")
        self._func_body = create_asm_code(_code, ProgramDatabase.BType.Main, start_idx, self._end_line-1, database=_context)
        self._code = _context.annotate(f"# main\n")
        self._code += f"main:\n"
        # globals init
        self._code += "".join(_context._globals_init)

        # main code
        self._code += self._func_body


class CommentCode(CodeGen):
    _init_syntax = CommentSyntax

    def __init__(self, _context, _code, _idx_line):
        super().__init__(_context, _idx_line)
        if not isinstance(_code[_idx_line], CommentSyntax):
            raise CompilerException(
                "comment-subcode must be initiated by an comment-syntax.")
        self._code = _context.annotate("#"+_code[_idx_line].get_comment()+"\n")


class AsmCode(CodeGen):
    _init_syntax = AsmSyntax

    def __init__(self, _context, _code, _idx_line):
        # raise CompilerException("asm statements are currently not implemented.")
        super().__init__(_context, _idx_line)
        if not isinstance(_code[_idx_line], AsmSyntax):
            raise CompilerException(
                "asm-subcode must be initiated by an asm-syntax.")
        asm_syntax = _code[_idx_line]
        start_idx = _idx_line+1
        body_asm = ""
        
        clobbers = asm_syntax.get_clobbers()
        associations = asm_syntax.get_associations()
        name_accesses = [(name, True, None, None, ProgramDatabase.NType.Variable) for name, _ in associations]
        clobber_translations, init_asm = _context.occupy_registers(len(clobbers))
        name_translations, init_asm2 = _context.name_access(name_accesses)
        init_asm+=init_asm2
        for i, syntax in enumerate(_code[start_idx:]):
            _context.set_compiler_position(start_idx+i)
            ProgramDatabase.set_compiler_position(start_idx+i)
            if isinstance(syntax, InlineAsmSyntax):
                body_asm += syntax.get_asm()+"\n"
            elif isinstance(syntax, EndSyntax):
                self._end_line = i+1+start_idx
                break
            elif isinstance(syntax, CommentSyntax):
                comment_code = CommentCode(_context, _code, start_idx+i)
                body_asm+=comment_code.get_code()
            else:
                raise CompilerException("Inside of asm statement can only be comments.")  # later just first occurence of end will be searched and everything in between except comments without -a will be added to code
        else:
            raise CompilerException("asm body never ended.")
        _context.set_compiler_position(start_idx+i+1)
        _context.free_registers(_idx_line)

        end_asm = ""
        
        replacements = []
        for repl_reg, actual_reg in zip(clobbers, clobber_translations):
            replacements.append((f"$r{repl_reg}", f"r{actual_reg}"))
        
        for (actual_reg, init, end, _), (_, repl_reg) in zip(name_translations, associations):
            init_asm+=init
            end_asm+=end
            replacements.append((f"$r{repl_reg}", f"{actual_reg}"))
        
        for repl, actual in replacements:
            body_asm = body_asm.replace(repl, actual)
        
        body_asm.replace("move ra sp\nmove sp ra\n", "")
        body_asm.replace("move sp ra\nmove ra sp\n", "")

        self._code = _context.annotate(f"# asm using associated registers {list(map(lambda x: f'r{x}', clobber_translations))} and reserved registers {list(map(lambda x: x[0], name_translations))}.\n")
        self._code += init_asm
        self._code += body_asm
        self._code += end_asm


class InlineAsmCode(CodeGen):
    _init_syntax = InlineAsmSyntax
    def __init__(self, _context, _code, _idx_line):
        super().__init__(_context, _idx_line)
        if not isinstance(_code[_idx_line], InlineAsmSyntax):
            raise CompilerException("inline asm-subcode must be initiated by an inline asm-syntax.")
        # always throw error except within asm code
        self._code = _code[_idx_line].get_asm()+"\n"




code_generators = [
    AlternativeCode, VariableDeclarationCode, ConstantDeclarationCode, 
    AlternativeCode, WhileLoopCode, ForLoopCode, ExpressionCode, 
    BreakCode, ContinueCode, FuncCode, ProcCode, ReturnCode, MainCode, CommentCode, 
    AsmCode, DeviceDeclarationCode, BatchDeviceDeclarationCode, InlineAsmCode, EndCode,
    ]
