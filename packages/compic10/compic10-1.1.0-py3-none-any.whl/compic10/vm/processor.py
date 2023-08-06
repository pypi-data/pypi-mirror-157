# -*- coding: utf-8 -*-

import re
from typing import DefaultDict

from .instructionset import *

# TODO: environment checks only device propertys given in file and ignores all others
# TODO: extra option nosideeffects that only the environment 
# device propertys are set and no others otherwiese failed test
# TODO: dynamic register and device access rr0? rrrr0 drrr0 dr0 ...
# TODO: When overwriting register / stack value that was written to before 
# without reading afterwards recognize and log this
# TODO: Statistics on register usage
# TODO: breakpoints
# TODO: hooks when register, stack or device etc. is accessed or written to
# TODO: enumerate used / unused labels and registers in executed code and whole codebase (just go over every line)
# TODO: recognize equation simplifications with existing commands like variable selection etc.
# TODO: use propertys for stack, registers to log access


# Device class that supports all sorts of possible devices (slots, reagent etc.)

class ProcessorException(Exception):
    pass


class Processor:
    register_translation = {f"r{i}" : i for i in range(18)}
    register_translation["sp"] = 16
    register_translation["ra"] = 17

    @property
    def _ip(self):
        return self._ipv

    @_ip.setter
    def _ip(self, address):
        if 0 < address < 128:
            self._ipv = address
        else:
            # TODO: reaching end of program handled elsewhere
            raise ProcessorException("Instruction pointer out of range.")


    # Parameter factory
    # TODO: fallback to string if PName expected but string equals register or devicename
    def _parse_parameter(self, param):
        # register
        if (m:=re.match("^(?:r(r*)(\d{1,2})|ra|sp)$", param)) is not None:
            try:
                if m[1] is None:
                    return PRegister(m[0], Processor.register_translation[m[0]])
                else:
                    # relative referencing
                    val = int(m[2])
                    for i in range(len(m[1])):  # amount of references
                        if not (0<=val<len(self._registers)):
                            raise ProcessorException("Indirect indexing failed. Got out of range register index {val} after {i+1} references on line {self._ip+1}.")
                        val = int(self._registers[val])
                    if not (0<=val<len(self._registers)):
                        raise ProcessorException("Indirect indexing failed. Got out of range register index {val} after {i+1} references on line {self._ip+1}.")
                    return PRegister(f"r{val}", val)
            except:
                raise ProcessorException(f"Unknown register {m[0]} on line {self._ip+1}.")
       
       # device 
        if (m:=re.match(r"^(?:d(r*)(\d{1,2})|db)$", param)) is not None:
            try:
                if m[1] is None:
                    return PDevice(m[0])
                else:
                    # relative referencing
                    val = int(m[2])
                    for i in range(len(m[1])):  # amount of references
                        if not (0<=val<len(self._registers)):
                            raise ProcessorException("Indirect indexing failed. Got out of range register index {val} after {i+1} references on line {self._ip+1}.")
                        val = int(self._registers[val])
                    if not (0<=val<len(self._registers)):
                        raise ProcessorException("Indirect indexing failed. Got out of range device index {val} after {i+1} references on line {self._ip+1}.")
                    return PDevice(f"d{val}")
            except:
                raise ProcessorException(f"Unknown device {m[0]} on line {self._ip+1}.")
       
       # integer 
        if (m:=re.match(r"^(?:[+-]?\d+)$", param)) is not None:
            return PNumber(float(m[0]))
       
       # float 
        if (m:=re.match(r"^(?:[+-]?(?:\d+\.\d*|\.\d+))$", param)) is not None:
            return PNumber(float(m[0]))
       
       # name (default) 
       # TODO: checking order might differ from original ic10 implementation
        if param in self._labels:
            return PNumber(self._labels[param])
        if param in self._aliases:
            return self._aliases[param]
        if param in self._defines:
            return self._defines[param]
        return PName(param)
        

    def _empty_line(self, line=None):
        if line is None:
            line = self._code[self._ip]
        if not line:
            return True

        m = re.match(r"^\s*(\#.*)?$", line)
        return m is not None


    def _label_line(self, line=None):
        if line is None:
            line = self._code[self._ip]
        if not line:
            raise ProcessorException(f"Expected non empty line number {self._ip+1}.")

        m = re.match(r"^\s*([\w\d]+)\:\s*$", line)  
        # seems like labels can be single digit too but would be interpreted as an integer
        # in parse parameters therefore first interpret as an integer before interpretation as an label
        return m


    def _parse_line(self, line=None):
        if line is None:
            line = self._code[self._ip]
        if not line:
            raise ProcessorException(f"Expected non empty line number {self._ip+1}.")

        m = re.match(r"^\s*(\w+)((?:\s+[\d\.\w]+)*)\s*(?:\#.*)?", line)
        if m is None:
            raise ProcessorException(f"Unknown syntax line {self._ip+1}.")
        cmd = m[1]
        params = m[2]
        return cmd, params


    def _(self):
        """Execution step."""
        # print("Evaluation of line,", self._code[self._ip])
        if self._empty_line() or (self._label_line() is not None):
            self._ip += 1
            return False, False

        cmd, params = self._parse_line()
        if cmd in ["or", "and", "yield"]:  # can't overwrite keywords
            cmd = "_" + cmd
        parsed_params = []
        for p in re.finditer("[^\s]+", params):
            parsed_params.append(self._parse_parameter(p[0]))

        # instruction is conditional branch 
        b_pattern = r"^b(r)?(eq|eqz|ge|gez|gt|gtz|le|lez|lt|ltz|ne|nez|dns|dse|ap|apz|na|naz)(al)?$"
        s_pattern = r"^s(eq|eqz|ge|gez|gt|gtz|le|lez|lt|ltz|ne|nez|dns|dse|ap|apz|na|naz)$"

        if (m:=re.match(b_pattern, cmd)) is not None:
            check_parameter_types(parsed_params, instruction_dict["_"+m[2]] + ["rn"], self)
            if not Instructions._branch(m, self, *parsed_params):  # returns true if jump occured
                self._ip+=1
        
        elif (m:=re.match(s_pattern, cmd)) is not None:
            check_parameter_types(parsed_params, ["r"] + instruction_dict["_"+m[1]], self)
            Instructions._set(m, self, *parsed_params)
            self._ip+=1
        
        # non conditional branching or set register instruction
        elif cmd not in instruction_dict:
            raise ProcessorException(f"Unkown instruction {cmd} on line {self._ip+1}.", self)

        else:
            check_parameter_types(parsed_params, instruction_dict[cmd], self)
            if not getattr(Instructions, cmd)(self, *parsed_params):  # returns true if jump occured
                self._ip+=1
        
        syncs = 0
        if cmd == "_yield":
            syncs = 1
        elif cmd == "sleep":
            syncs = Instructions._get(self, params[0]) * 2  # dirty solution, *2 because every tick = 0.5 seconds
        return syncs, cmd=="hcf" # return True if execution stopped for this tick



    def __init__(self, code="", overwrite_registers=None, overwrite_stack=None):
        # internal registers [0,17], aliases for sp, ra recognized by .reg method
        self._registers = [0 for _ in range(18)]
        self._devices = {f"d{i}" : {} for i in range(6)}
        self._devices["db"] = {"Setting" : 0}

        # stack addresses [0, 511]
        self._stack = [0 for _ in range(512)]

        # Instruction pointer
        # Line number in editor is _ip+1!
        self._ipv = 0

        # mips instructions
        self._code = code.split("\n")

        self._labels = {}
        for i, line in enumerate(self._code):
            if (not self._empty_line(line)) and ((m:=self._label_line(line)) is not None):
                if m[1] in self._labels:
                    raise ProcessorException(f"Label {m[1]} used more than once on line {i+1}.")
                self._labels[m[1]] = i

        # TODO: find and store alias as command and use device names in output
        self._aliases = {}  # values already interpreted with .parsed_params!

        # TODO: Can't rename db! Maybe not as an error but don't respect this action.
        # add to alias instruction update of this dict
        self._device_names = {f"d{i}" : f"d{i}" for i in range(6)}

        self._batch_devices = None

        # implemented as command
        self._defines = {}  # values already interpreted with .parsed_params! (infinite recursion possible!)

        if overwrite_registers is not None:
            if isinstance(overwrite_registers, dict):
                pass
            elif isinstance(overwrite_registers, list):
                pass
            else:
                raise ProcessorException("Unknown register overwrite format.")

        if overwrite_stack is not None:
            if isinstance(overwrite_stack, dict):
                pass
            elif isinstance(overwrite_stack, list):
                pass
            else:
                raise ProcessorException("Unknown stack overwrite format.")


    def run(self):
        for _ in range(128): 
            if self._ip >= 128:
                yield  # so tests at the end of script are run
                return  # end iterator

            if self._ip >= len(self._code):
                yield  # so tests at the end of script are run
                return  # end iterator

            syncs, stop = self._()

            if stop: 
                # TODO: hcf might be handled in a diffrent way
                yield  # so tests at the end of script are run
                return

            for _ in range(syncs):
                yield  # wait until next game tick (synchronize)
