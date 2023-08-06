import itertools
import re
import copy
from enum import Enum
from collections import namedtuple

from . import compilerexception
from .compilerexception import CompilerException, UnexpectedException


# for every Block memory snapshot at beginning and end
# for/while loop: at the end of block placeholder which after full evaluation will be replaced with instructions, 
# that reset state which reverts all moved variables to the start positions and frees all registers which were free before
# not touched memory / registers don't get modified there
# register occupation operations
# function calls expect certain state too but this must be snapshot from before the call 
# (line before expression registers are handled seperately but push/pop instructionsshould be removed if not touched by function)


class ProgramDatabase:
    class BType(Enum):
        For_ = 0
        While_ = 1
        If_ = 2
        Func = 3
        Proc = 4
        Main = 5
        Global_ = 6


    Block = namedtuple("Block", ["blid", "bounds", "parent", "depth", "btype", "info", "registers"])  # info is id of statement or id of function
    Name = namedtuple("Name", ["name", "ntype", "blid", "first_occurence"], defaults=None)


    VAR_STACK_OFFSET = 180  # can be changed by start options
    VAR_STACK_LENGTH = 100  # can be changed by start options
    # two variables r14, r15 are needed for loops
    REGISTER_AMOUNT = 14
    CODE_OPTIMIZATION = True
    PP_OPTIMIZATION = True
    ANNOTATE = False
    line = None

    class NType(Enum):
        Constant = 0
        Variable = 1
        Function = 2
        Procedure = 3
        Device = 4
        Batch_Device = 5

    class RegisterState:
        def __init__(self, slot, db):
            self.db = db
            self.slot = slot
            self.occupied = False
            self._name = None
        
        @property
        def name(self):
            if not self._name:
                raise UnexpectedException("Trying to get variable name of register not occupied by an variable.")
            return self._name

        def free(self):
            self.occupied = False
            self._name = None
        
        def is_free(self):
            return not self.occupied
        
        def is_nameless(self):
            return not self._name

        def occupy(self, name=None, write_access=True):
            if write_access:
                self.db.touch_register(self)
                if name and (name.blid==0):  # is global
                    raise UnexpectedException("Register allocated for global variable.")
            self.occupied = True
            self._name = name
            self.line = ProgramDatabase.line

        def use(self, write_access=True):
            if write_access:
                self.db.touch_register(self)
                if self._name and (self._name.blid == 0):  # is global
                    raise UnexpectedException("Register allocated for global variable.")

            self.line = ProgramDatabase.line


    class VarStackState:
        def __init__(self, slot, db):
            self.db = db 
            self.slot = slot  # this way slot is known when filtering Programdatabase._var_stack
            self._name = None
            self.for_callable_reserved = None  # references Block of callable
            self.for_global_reserved = None  # references Name object of global variable

        def free(self):
            self._name = None

        def occupy(self, name):
            calling_block = self.db.block_embedded((ProgramDatabase.BType.Func, ProgramDatabase.BType.Proc))
            
            # spots previously reserved by callables can only be used by this callable
            if self.for_callable_reserved and (calling_block != self.for_callable_reserved):
                raise UnexpectedException("Trying to overwrite an callable reserved Programdatabase._var_stack slot.")
            
            # global variables can only be overwritten by the same global variable
            if self.for_global_reserved and (name != self.for_global_reserved):
                raise UnexpectedException("Trying to overwrite an global reserved Programdatabase._var_stack slot.")
            

            # lock slot to global
            if not self.for_global_reserved and self.db.in_global_block():
                self.for_global_reserved = name
            # lock slot to function (elif because first look if global variable)
            elif (not self.for_callable_reserved) and calling_block:
                self.for_callable_reserved = calling_block
            
            # actual occupation
            self._name = name


        def is_free(self):
            if self._name:
                return False
            
            if self.for_callable_reserved:  # can only be used by same function/procedure
                calling_block = self.db.block_embedded((ProgramDatabase.BType.Func, ProgramDatabase.BType.Proc))
                return calling_block == self.for_callable_reserved
            elif self.for_global_reserved:
                return False

            return True

        @property
        def name(self):
            if not self._name:
                raise UnexpectedException("Trying to get variable name of var_stack slot not occupied by an variable.")
            return self._name       


    def block_embedded(self, query, block=None):
        it = block or self._block_iter
        if not hasattr(query, "__contains__"):
            query = (query, )
        while it is not None:
            if it.btype in query:
                break
            it = it.parent
        else:
            return False
        return it
    
    def in_global_block(self):
        return self._block_iter.btype == ProgramDatabase.BType.Global_

    def find_in_registers(self, name):
        eles = list(filter(lambda r: not r.is_free() and not r.is_nameless() and self.same_name(r.name, name), self._registers))
        if len(eles)>1:
            raise UnexpectedException("Variable occupies more than one register.")
        if not eles:
            return None
        return eles[0]


    def __init__(self, code_len):
        self.blocks = []
        self.names = []
        self._registers = [ProgramDatabase.RegisterState(slot, self) for slot in range(ProgramDatabase.REGISTER_AMOUNT)]
        self._block_iter = None
        self._code_len = code_len
        self._var_stack = [ProgramDatabase.VarStackState(slot+ProgramDatabase.VAR_STACK_OFFSET, self) for slot in range(ProgramDatabase.VAR_STACK_LENGTH)]
        # format: n for, n while, n if, n func, n proc, n main (main can only be there once)
        self._block_counter = [0 for _ in range(len(ProgramDatabase.BType))]
        
        # todo: namedtuples verwenden
        self._constants = []
        self._callables = []  # Format: (name : Name, (blid, n-params, defaults)), ...  blid is used since no block object at point of creation
        self._devices = []  # Format: (name : Name, device id), ...
        self._batch_devices = []  # Format: (name : Name, device id), ...
        self._globals_init = []  # init of globals, always executed at beginning of main (are always in var_stack just in place used never in designated register)
        self._recursive_call_hook = []
        # handled as an stack since could nest loops
        self.current_loop_continue_snapshot = []
        self.current_loop_break_snapshot = []

    def has_main(self):
        return self._block_counter[ProgramDatabase.BType.Main.value] > 0

    def get_callable_info(self, name, must_return = False):
        # returns fncid, n_params
        name = self.get_name(name)
        if name.ntype not in [ProgramDatabase.NType.Function, ProgramDatabase.NType.Procedure]:
            raise CompilerException(f"Name {name.name} is not callable.")
        if (name.ntype == ProgramDatabase.NType.Procedure) and must_return:
            raise CompilerException(f"Name {name.name} is not a function.")
        for fncid in range(len(self._callables)):
            if self._callables[fncid][0] == name:
                return self._callables[fncid][1], self.blocks[self._callables[fncid][1][0]].btype == ProgramDatabase.BType.Func
        raise CompilerException("Callable not registered.")
    
    @classmethod
    def annotate(cls, annotation):
        # used for optional annotation
        if not cls.ANNOTATE: return ""
        res =  [annotation]
        # max 52 characters linewidth
        while len(res[-1])>=52:
            res.append("# "+res[-1][50:])
            res[-2] = res[-2][:50]+"\n"
        return "".join(res)

    @classmethod
    def set_compiler_position(cls, line=None):
        if line is not None:
            cls.line = line

    def generate_block_id(self, btype):  # unique in combination with blocktype is NOT BType.blid
        # amount of blocks in this category + 1
        return self._block_counter[btype.value]

    def generate_blid(self):  # blid of next block to be created
        # always blid of last added block + 1
        return len(self.blocks)

    def get_current_block(self):
        return self._block_iter

    def start_block(self, start, btype):
        if self.get_current_block():
            if self.get_current_block().btype == ProgramDatabase.BType.Global_:
                # special considerations for main block
                if btype not in (
                    ProgramDatabase.BType.Func,
                    ProgramDatabase.BType.Proc,
                    ProgramDatabase.BType.Main,
                ): raise CompilerException(f"{str(btype).replace('BType.', '')} statement is not allowed in the global namespace.")
            else:
                # special considerations outside main block
                if btype not in (
                    ProgramDatabase.BType.For_,
                    ProgramDatabase.BType.While_,
                    ProgramDatabase.BType.If_,
                ): raise CompilerException(f"{str(btype).replace('BType.', '')} statement is not allowed outside the global namespace.")
        elif btype != ProgramDatabase.BType.Global_:
            raise CompilerException("Must start global block first.")

        # used to start new block and set state accordingly (in new block with parent old block)
        info = self._block_counter[btype.value]
        self._block_counter[btype.value] += 1
        if btype == ProgramDatabase.BType.Main:
            if self._block_counter[btype.value] > 1:
                raise CompilerException(
                    "Program can only have one main procedure.")
        if btype == ProgramDatabase.BType.Global_:
            if self._block_counter[btype.value] > 1:
                raise CompilerException(
                    "Program can only have one global block.")
        if not self._block_iter:
            self.blocks.append(ProgramDatabase.Block(
                self.generate_blid(), [start, self._code_len], None, 0, btype, info, []))
            self._block_iter = self.blocks[-1]
        else:
            self.blocks.append(ProgramDatabase.Block(self.generate_blid(), [start, None],
                self._block_iter, self._block_iter.depth+1, btype, info, []))
            self._block_iter = self.blocks[-1]
        return self._block_iter

    def end_block(self, end):
        # leave newly created block and set state accordingly (return to old block)
        if not self._block_iter:
            raise CompilerException("Trying to end block without any blocks.")
        else:
            idx = self.blocks.index(self._block_iter)
            self.blocks[idx].bounds[1] = end
            # invalidate all variable names from block
            names = filter(lambda n: n.blid ==
                           self._block_iter.blid, self.names)
            for name in names:
                if var:=self.find_in_var_stack(name): var.free()
                # potential here to push to register if static variable
                elif reg:=self.find_in_registers(name): reg.free()
            self._block_iter = self._block_iter.parent

    def overwrite_memory(self, snapshot):
        self._registers, self._var_stack = snapshot

    def get_names(self):
        return set(filter(lambda n: n.blid == self._block_iter.blid, self.names))  # only local names from current block

    def make_snapshot(self):
        return ([copy.copy(reg) for reg in self._registers], [copy.copy(var)for var in self._var_stack])

    def revert_state(self, snapshot_start, snapshot_end, tmp_reg1=14, tmp_reg2=15):
        registers_start, var_stack_start = snapshot_start
        registers_end, var_stack_end = snapshot_end

        # registers to var_stack movements
        movements = []
        for reg in registers_start:
            if not reg.is_free() and not reg.is_nameless():  # all others neglected
                for var in var_stack_end: 
                    if var.is_free(): continue
                    if self.same_name(reg.name, var.name):
                        movements.append([(reg.slot, "r"), (var.slot, "v")])
                        break
        
        # var_stack to registers movements
        for var in var_stack_start:
            if var.is_free(): continue
            for reg in registers_end: 
                if not reg.is_free() and not reg.is_nameless():  # all others neglected
                    if self.same_name(var.name, reg.name):
                        movements.append([(var.slot, "v"), (reg.slot, "r")])
                        break
        
        # var_stack to var_stack movements
        for var_s in var_stack_start:
            if var_s.is_free(): continue
            for var_e in var_stack_end:
                if var_e.is_free(): continue
                if self.same_name(var_s.name, var_e.name) and (var_s.slot != var_e.slot):
                    movements.append([(var_s.slot, "v"), (var_e.slot, "v")])
                    break

        # register to register movements
        for reg_s in registers_start:
            if not reg_s.is_free() and not reg_s.is_nameless():  # all others neglected
                for reg_e in registers_end:
                    if not reg_e.is_free() and not reg_e.is_nameless():  # all others neglected
                        if self.same_name(reg_s.name, reg_e.name) and (reg_s.slot != reg_e.slot):
                            movements.append([(reg_s.slot, "r"), (reg_e.slot, "r")])
                            break
        
        def replace_all(i, j):
            for ele in movements:
                # must match index and location (register or var_stack)
                if ele[0] == i: ele[0] = j
                elif ele[0] == j: ele[0] = i
                if ele[1] == i: ele[1] = j
                elif ele[1] == j: ele[1] = i

        # what if tmp_reg1 and tmp_reg2 are part of the moving operation?
        revert_asm = ""
        for target, source in movements:
            if target[1] == source[1] == "r":
                revert_asm+=f"move r{tmp_reg1} r{target[0]}\n"
                revert_asm+=f"move r{target[0]} r{source[0]}\n"
                revert_asm += f"move r{source[0]} r{tmp_reg1}\n"
            elif target[1] == source[1] == "v":
                revert_asm+="move ra sp\n"
                revert_asm+=f"move sp {source[0]+1}\n"
                revert_asm+=f"pop r{tmp_reg1}\n"
                revert_asm+=f"move sp {target[0]+1}\n"
                revert_asm+=f"pop r{tmp_reg2}\n"
                revert_asm+=f"push r{tmp_reg1}\n"
                revert_asm+=f"move sp {source[0]}\n"
                revert_asm+=f"push r{tmp_reg2}\n"
                revert_asm+="move sp ra\n"
            elif (target[1] == "r") and (source[1] == "v"):
                revert_asm+="move ra sp\n"
                revert_asm+=f"move sp {source[0]+1}\n"
                revert_asm+=f"pop r{tmp_reg1}\n"
                revert_asm+=f"push r{target[0]}\n"
                revert_asm+=f"move r{target[0]} r{tmp_reg1}\n"
                revert_asm+="move sp ra\n"
            elif (target[1] == "v") and (source[1] == "r"):
                revert_asm+="move ra sp\n"
                revert_asm+=f"move sp {target[0]+1}\n"
                revert_asm+=f"pop r{tmp_reg1}\n"
                revert_asm+=f"push r{source[0]}\n"
                revert_asm+=f"move r{source[0]} r{tmp_reg1}\n"
                revert_asm+="move sp ra\n"
            else:
                raise CompilerException("This shouldn't happen.")
            replace_all(target, source)
        revert_asm = revert_asm.replace("move sp ra\nmove ra sp\n", "")
        return revert_asm

    def register_usage(self, snapshot):
        registers, _ = snapshot  # don't care about var_stack
        used = set()
        for reg in registers:
            if not reg.is_free():
                used.add(reg.slot)
        return used

    def prepare_jump(self, block_id, registers, rr):
        registers |= self.register_usage((self._registers, None))  # doesn't modify so safe to pass them directly
        if rr is not None:
            registers-={rr,}
        block = self.blocks[block_id]
        touched_registers = set().union(*list(map(lambda ele: ele[1], block.registers)))
        before_code = ""
        after_add = ""
        if in_call:=self.block_embedded(block.btype):
            if in_call.blid == block_id:  # recursive call
                before_code = f"$recursive_placeholder_push_{len(self._recursive_call_hook)}\n"
                after_add = f"$recursive_placeholder_pop_{len(self._recursive_call_hook)}\n"
                self._recursive_call_hook.append((registers, touched_registers))  # already saved registers (get subtracted from the complete set of registers modified in this function before and after this call)
        # registers touched by function AND needed by caller (those must be pushed to stack before the call)
        registers = registers.intersection(touched_registers)
        for r in registers:
            before_code+=f"push r{r}\n"
        after_code = ""
        for r in reversed(list(registers)):
            after_code+=f"pop r{r}\n"
        return before_code, after_code+after_add
        
    reserved_names = [
        "self", "sin", "cos", "tan", "asin", "acos", "atan", "abs",
        "ceil", "exp", "floor", "log", "max", "min", "rand", "round", "sqrt",
        "trunc", "set", "set_batch", "load", "sleep", "yield", "hcf", "select"
    ]

    def add_name(self, name, ntype, value=None, revfreg=False):  # value is constant value for constant or (blid, n_params, defaults) for function
        line = ProgramDatabase.line
        if name in ProgramDatabase.reserved_names:
            raise CompilerException(f"Trying to overwrite the reserved name {name}.")
        if name in list(map(lambda e: e.name, self.get_names())):
            raise CompilerException(f"Trying to declare the already existing name {name}.")
        
        if self.get_current_block().btype == ProgramDatabase.BType.Global_:
            # special considerations for main block
            if ntype not in (
                ProgramDatabase.NType.Function, 
                ProgramDatabase.NType.Procedure,
                ProgramDatabase.NType.Constant,
                ProgramDatabase.NType.Device,
                ProgramDatabase.NType.Batch_Device,
                ProgramDatabase.NType.Variable,
            ): raise CompilerException(f"{str(ntype).replace('NType.', '')} declaration is not allowed in the global namespace.")
            
            global_name = True
        else:
            # special considerations outside main block
            if ntype not in (
                ProgramDatabase.NType.Constant,
                ProgramDatabase.NType.Variable
            ): raise CompilerException(f"{str(ntype).replace('NType.', '')} declaration is not allowed outside the global namespace.")
            
            global_name = False

        self.names.append(ProgramDatabase.Name(name, ntype, self._block_iter.blid, line))
        if ntype == ProgramDatabase.NType.Variable:
            if global_name:  # special considerations for global variables (not assigned to register in init)
                spot = self.first_free_var_stack(self.names[-1])
                if not spot:
                    raise CompilerException("No more free space on variable stack.", line)
                spot.occupy(self.names[-1])
                return (None, spot.slot, "")
            
            free = self.first_free_register(revfreg)
            
            # no free registers for new variable
            if not free:
                to_free = self.least_recently_used_register()
                # cannot free register or register in usage on current line
                if not to_free or (to_free.line == line):
                    spot = self.first_free_var_stack(self.names[-1])
                    if not spot:
                        raise CompilerException("No more free space on variable stack.", line)
                    spot.occupy(self.names[-1])
                    return (None, spot.slot, "")
                
                # assign to cleared register
                sv_name = to_free.name
                spot = self.first_free_var_stack(sv_name)
                if not spot:
                    raise CompilerException("No more free space on variable stack.", line)
                init_asm = "move ra sp\n"
                init_asm += ProgramDatabase.annotate(f"# prep sp for var{{{sv_name.name}}}")+"\n"
                init_asm += f"move sp {spot.slot}\n"
                init_asm += ProgramDatabase.annotate(f"# save var{{{sv_name.name}}}\n")
                init_asm += f"push r{to_free.slot}\n"
                init_asm += "move sp ra\n"
                spot.occupy(sv_name)
                to_free.occupy(self.names[-1])
                return (to_free.slot, None, init_asm)
            
            # assign to free register
            else:
                free.occupy(self.names[-1])
                # Format: register, var_stacklocation, init_code
                return (free.slot, None, "")
        
        elif ntype == ProgramDatabase.NType.Constant:
            self._constants.append((self.names[-1], value))
            return (None, None, "")
        
        elif ntype in [ProgramDatabase.NType.Function, ProgramDatabase.NType.Procedure]:
            self._callables.append((self.names[-1], value))  # block gets started after name reservation
            return (None, None, "")
        
        elif ntype == ProgramDatabase.NType.Device:
            self._devices.append((self.names[-1], value))
        
        elif ntype == ProgramDatabase.NType.Batch_Device:
            self._batch_devices.append((self.names[-1], value))
        
        else:
            raise CompilerException("Unknown name type.")

        return (None, None, "")  # placeholderish for constants and functions?

    def touch_register(self, touched_reg):
        line = ProgramDatabase.line
        it = self._block_iter
        # also touches registers of all embedding blocks
        while it:
            if this_line:=list(filter(lambda e: e[0] == line, it.registers)):
                this_line[0][1].add(touched_reg.slot)
            else:
                it.registers.append((line, {touched_reg.slot, }))
            it = it.parent
    
    def occupy_registers(self, regs):
        line = ProgramDatabase.line
        # occupie a certain amount of registers returns register_translations (actually used registers) and code to save registers to be overwritten
        register_translation = []
        safe_code = ""
        for _ in range(regs):
            free = self.first_free_register()
            if not free:
                break
            free.occupy()
            register_translation.append(free.slot)
        else:
            # enough free ones available
            return (register_translation, safe_code)
        
        for _ in range(len(register_translation), regs):  # remaining registers
            to_free = self.least_recently_used_register()
            if not to_free or (to_free.line == line):
                raise CompilerException("Not enough free registers for operation.", line)
            register_translation.append(to_free.slot)
            name = to_free.name
            to_free.occupy()
            spot = self.first_free_var_stack(name)
            if not spot:
                raise CompilerException("No more free space on variable stack.", line)
            safe_code += "move ra sp\n"
            safe_code += f"move sp {spot.slot}\n"
            safe_code += f"push r{to_free.slot}\n"
            safe_code += "move sp ra\n"
            spot.occupy(name)
        
        return (register_translation, safe_code)

    def name_access(self, name_request_data):
        line = ProgramDatabase.line
        # can also be used to insert constants format name, write to name(True/False), reserved register, result register
        # result register and reserved registers needed for read (only reserved) and write(both) of variables for which no registers are free
        write_to_names = set()
        read_from_names = set()
        write_to_globals = set()
        read_from_globals = set()
        init_asm = ""
        cur_block = self._block_iter
        already_assigned = set()
        AccInfo = namedtuple(
            "AccInfo", ["name", "reg", "set_asm", "get_asm", "is_const", "is_device", "is_batch_device"])
        access_data = []  # list of AccInfo

        # manage database (read / write accesses)
        for name, write, alt_reg, res_reg, type_req in name_request_data:
            if name in ProgramDatabase.reserved_names:  # skip all reserved names (seperate handling at the end of this function)
                continue
            name = self.get_name(name)

            # check name type
            if (type_req is not None) and (((type(type_req) in (tuple, list)) and (name.ntype not in type_req)) or ((type(type_req) not in (tuple, list)) and (name.ntype != type_req))):
                raise CompilerException(f"{name.name} is not of type {str(type_req).replace('NType.', '')}.")

            if name.blid == 0 and name.ntype == ProgramDatabase.NType.Variable:  # is global
                if write:
                    write_to_globals.add(name)
                read_from_globals.add(name)
                continue

            if name.first_occurence > line:
                raise CompilerException("Trying to access an not yet existing name.")
            if write:
                if name.ntype not in [ProgramDatabase.NType.Variable]:
                    raise CompilerException("Trying to write to an non variable.")
                write_to_names.add(name)
            else:
                read_from_names.add(name)

        # assign global variables
        for name in write_to_globals:
            if name in already_assigned:
                continue
            in_stack = self.find_in_var_stack(name)
            before = "move ra sp\n"
            before += f"move sp {in_stack.slot+1}\n"
            before += "pop $rr\n"
            before += "move sp ra\n"
            end = "move ra sp\n"
            end += f"move sp {in_stack.slot}\n"
            end += "push $rr\n"
            end += "move sp ra\n"
            access_data.append(AccInfo(name, None, end, before, False, False, False))
            already_assigned.add(name)
        
        for name in read_from_globals:
            if name in already_assigned:
                continue
            in_stack = self.find_in_var_stack(name)
            before = "move ra sp\n"
            before += f"move sp {in_stack.slot+1}\n"
            before += "pop $rr\n"
            before += "move sp ra\n"
            access_data.append(AccInfo(name, None, "", before, False, False, False))
            already_assigned.add(name)

        # assign devices
        for name in read_from_names|write_to_names:
            if name in already_assigned:
                continue
            if name.ntype == ProgramDatabase.NType.Device:
                for d_name, value in self._devices:
                    if ProgramDatabase.same_name(name, d_name):
                        access_data.append(AccInfo(name, value, "", "", False, True, False))
                        already_assigned.add(name)
                        break
                else:
                    raise CompilerException(f"Unknown device {name.name}.")

        # assign batch devices
        for name in read_from_names|write_to_names:
            if name in already_assigned:
                continue
            if name.ntype == ProgramDatabase.NType.Batch_Device:
                for d_name, value in self._batch_devices:
                    if ProgramDatabase.same_name(name, d_name):
                        access_data.append(AccInfo(name, value, "", "", False, False, True))
                        already_assigned.add(name)
                        break
                else:
                    raise CompilerException(f"Unknown batch device {name.name}.")
        
        # assign constants
        for name in read_from_names:
            if name in already_assigned:
                continue
            if name.ntype == ProgramDatabase.NType.Constant:
                for c_name, value in self._constants:
                    if ProgramDatabase.same_name(name, c_name):
                        access_data.append(AccInfo(name, value, "", "", True, False, False))
                        already_assigned.add(name)
                        break
                else:
                    raise CompilerException(f"Unknown constant {name.name}.")


        # variables management
        
        # find already existing names for write names
        for name in write_to_names:
            if name in already_assigned:
                continue
            if reg:=self.find_in_registers(name):
                access_data.append(AccInfo(name, reg.slot, "", "", False, False, False))
                already_assigned.add(name)
                reg.use()
        
        # assign registers for write/read names when possible
        # assign free ones
        for name in write_to_names:
            if name in already_assigned:
                continue
            # assign until no free ones anymore
            free = self.first_free_register()
            if not free:
                break  # after that can obviously not be any other free registers           
            # load in this register before usage
            in_stack = self.find_in_var_stack(name)
            init_asm += "move ra sp\n"
            init_asm += f"move sp {in_stack.slot+1}\n"
            init_asm += f"pop r{free.slot}\n"
            init_asm += f"move sp ra\n"
            in_stack.free()
            free.occupy(name)            
            already_assigned.add(name)
            access_data.append(AccInfo(name, free.slot, "", "", False, False, False))
        
        # occupy already used ones
        for name in write_to_names:
            if name in already_assigned:
                continue
            
            # until no free ones anymore
            in_stack = self.find_in_var_stack(name)
            to_free = self.least_recently_used_register()
            if not to_free or (to_free.line == line):
                before = "move ra sp\n"
                before += f"move sp {in_stack.slot+1}\n"
                before += "pop $rr\n"
                before += "move sp ra\n"
                end = "move ra sp\n"
                end += f"move sp {in_stack.slot}\n"
                end += "push $rr\n"
                end += "move sp ra\n"
                access_data.append(AccInfo(name, None, end, before, False, False, False))
                already_assigned.add(name)
                continue
            sv_name = to_free.name
            spot = self.first_free_var_stack(sv_name)
            if not spot:
                raise CompilerException("No more free space on variable stack.", line)
            init_asm += "move ra sp\n"
            init_asm += f"move sp {spot.slot}\n"
            init_asm += f"push r{to_free.slot}\n"
            init_asm += f"move sp {in_stack.slot+1}\n"
            init_asm += f"pop r{to_free.slot}\n"
            init_asm += "move sp ra\n"
            spot.occupy(sv_name)
            in_stack.free()
            to_free.occupy(name)
            already_assigned.add(name)
            access_data.append(AccInfo(name, to_free.slot, "", "", False, False, False))

        # same as for write_t_names but for read_from_names

        # find already existing names
        for name in read_from_names:
            if name in already_assigned:
                continue
            if reg:=self.find_in_registers(name):
                access_data.append(AccInfo(name, reg.slot, "", "", False, False, False))
                already_assigned.add(name)
                reg.use(False)  # this is the only place where no writing happens
            
        # assign free ones
        for name in read_from_names:
            if name in already_assigned:
                continue
            free = self.first_free_register()
            if not free:
                break
            in_stack = self.find_in_var_stack(name)
            init_asm += "move ra sp\n"
            init_asm += f"move sp {in_stack.slot+1}\n"
            init_asm += f"pop r{free.slot}\n"
            init_asm += "move sp ra\n"
            in_stack.free()
            free.occupy(name)            
            already_assigned.add(name)
            access_data.append(AccInfo(name, free.slot, "", "", False, False, False))
        
        # occupy already used ones
        for name in read_from_names:
            if name in already_assigned:
                continue
            in_stack = self.find_in_var_stack(name)
            to_free = self.least_recently_used_register()
            if not to_free or (to_free.line == line):
                before = "move ra sp\n"
                before += f"move sp {in_stack.slot+1}\n"
                before += "pop $rr\n"
                before += "move sp ra\n"
                access_data.append(AccInfo(name, None, "", before, False, False, False))
                already_assigned.add(name)
                continue

            sv_name = to_free.name
            spot = self.first_free_var_stack(sv_name)
            if not spot:
                raise CompilerException("No more free space on variable stack.", line)
            init_asm += "move ra sp\n"
            init_asm += f"move sp {spot.slot}\n"
            init_asm += f"push r{to_free.slot}\n"
            init_asm += f"move sp {in_stack.slot+1}\n"
            init_asm += f"pop r{to_free.slot}\n"
            init_asm += "move sp ra\n"
            spot.occupy(sv_name)
            in_stack.free()
            to_free.occupy(name)            
            already_assigned.add(name)
            access_data.append(AccInfo(name, to_free.slot, "", "", False, False, False))

        # create variable assignment table
        var_asg_tbl = []  # Format: (reg, set_asm, get_asm)
        touched_registers = set()
        for name, _, alt_reg, res_reg, type_req in name_request_data:
            access_data_entry = None
            if name not in ProgramDatabase.reserved_names:
                name = self.get_name(name)
                [access_data_entry:= e for e in access_data if e.name == name]
            else:
                if name == "self":
                    var_asg_tbl.append(("b", "", "", (False, True, False)))
                continue
            if not access_data_entry:
                raise CompilerException(f"Variable {name.name} could not be resolved.", line)
            
            # such names completly ignore inplace register assignments (always work like variable inplace register assignments since they can't have dedicated variables)
            if access_data_entry.is_device or access_data_entry.is_batch_device:
                p_reg = str(access_data_entry.reg)
            elif access_data_entry.is_const:  # must be formatted in a certain way fixed point not scientific
                p_reg = f"{access_data_entry.reg:.16f}".rstrip("0").rstrip(".")  # can't be in one rstrip call because 0.0 would result in empty string
            # in the following when using inplace register assignment with prefix/suffix set get of variables and not dedicating an register
            # res_reg and alt_reg are the register names used in the graph (must be replaced later) and access_data_entry.reg is an actual register which will not be replaced
            else:
                p_reg = f"r{access_data_entry.reg}" if access_data_entry.reg is not None else f"$r{alt_reg}"
                if access_data_entry.reg is not None:
                    touched_registers.add(access_data_entry.reg)

            r_reg = f"r{access_data_entry.reg}" if access_data_entry.reg is not None else f"$r{res_reg}"
            if access_data_entry.reg:
                touched_registers.add(access_data_entry.reg)
            
            if (access_data_entry.reg is None) and ((res_reg is None) or (alt_reg is None)):
                raise CompilerException(f"Can't assign free register for variable {name.name}.")

            var_asg_tbl.append((
                p_reg,
                re.sub(r"\$rr", r_reg, access_data_entry.set_asm),
                re.sub(r"\$rr", p_reg, access_data_entry.get_asm),
                (access_data_entry.is_const, access_data_entry.is_device, access_data_entry.is_batch_device)
            ))
        
        init_asm = init_asm.replace("move ra sp\nmove sp ra\n", "")  # happens always when no init_asm is needed
        return var_asg_tbl, init_asm

    def free_registers(self, line=None):
        line = line or ProgramDatabase.line
        for reg in self._registers:
            if not reg.is_free() and reg.is_nameless() and (reg.line == line):
                reg.free()
    
    # both necessary, since without pointers elements wont get updated everywhere and those elements don't change
    @staticmethod
    def same_name(name_1, name_2):
        if (name_1.name == name_2.name) and (name_1.blid == name_2.blid):
            if name_1 is not name_2:
                raise UnexpectedException("There are two Name objects for the same name.")
            return True
        return False

    @staticmethod
    def same_block(blk_1, blk_2):
        if (blk_1.name == blk_2.name) and (blk_1.blid == blk_2.blid):
            if blk_1 is not blk_2:
                raise UnexpectedException("There are two Block objects for the same block")
            return True
        return False

    def first_free_register(self, reverse=False):
        for reg in (reversed(self._registers) if reverse else self._registers):
            if reg.is_free():
                return reg
        return None

    def first_free_var_stack(self, name):
        if name.blid == 0:  # global variable
            found = list(filter(lambda v: v._name and v._name.blid == name.blid and v._name.name == name.name, self._var_stack))
            if len(found)>1:
                raise UnexpectedException("Global variable several times in var_stack.")
            elif len(found)==1:
                return found[0]
        for var in self._var_stack:
            if var.is_free():
                return var
        return None

    def least_recently_used_register(self):
        regs = sorted(filter(lambda r: not r.is_free() and not r.is_nameless(), self._registers), key=lambda r: r.line)
        if len(regs) == 0:
            return None
        return regs[0]

    def get_name(self, name):
        valid_blks = [None]  # global block always accessible
        it = self._block_iter
        while it:
            valid_blks.append(it.blid)
            it = it.parent
        matches = sorted(filter(lambda n: n.blid in valid_blks and n.name == name,
                                self.names), key=lambda n: self.blocks[n.blid].depth, reverse=True)
        if len(matches) == 0:
            raise CompilerException(f"Unknown Variable {name}")
        return matches[0]

    def get_device(self, name):
        valid_blks = [0]  # global block always accessible
        it = self._block_iter
        while it:
            valid_blks.append(it.blid)
            it = it.parent
        matches = sorted(filter(lambda n: n[0].blid in valid_blks and n[0].name == name, self._devices+self._batch_devices), key=lambda n: self.blocks[n[0].blid].depth, reverse=True)
        if len(matches) == 0:
            raise CompilerException(f"Unknown Device {name}")
        return matches[0]

    def find_in_var_stack(self, name):
        for var in self._var_stack:
            if (not var.is_free()) and var._name and ProgramDatabase.same_name(var.name, name):  # var._name used since non free variable could be reserved and without name
                return var
        return None
    
    def get_used_registers(self):
        return set(filter(lambda r: not r.is_free(), self._registers))

compilerexception.ProgramDatabase = ProgramDatabase
