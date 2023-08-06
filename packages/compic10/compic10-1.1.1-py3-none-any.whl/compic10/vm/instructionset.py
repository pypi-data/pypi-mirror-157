# -*- coding: utf-8 -*-

from dataclasses import dataclass
import sys
import math
import random


class InstructionException(Exception):
    pass

_SP = 16
_RA = 17 


# Parameter types
@dataclass
class PRegister:
    name : str
    idx : int


@dataclass
class PDevice:
    name : str


@dataclass
class PNumber:
    value : float


@dataclass
class PName:
    string : str


def check_parameter_types(params, expected_types, ic):
    """Utility function to test for correct parameters"""
    if len(params) != len(expected_types):
        raise InstructionException(f"Wrong parameter amount on line {ic._ip+1}, expected {len(expected_types)}.")
    for i, (p, es) in enumerate(zip(params, expected_types)):
        for e in es: 
            if "r"==e and isinstance(p, PRegister):
                break
            if "d"==e and isinstance(p, PDevice):
                break
            if "n"==e and isinstance(p, PNumber):
                break
            if "s"==e and isinstance(p, PName):
                break
        else:
            raise InstructionException(f"Parameter {i+1} of wrong type expected one of {','.join(es)} on line {ic._ip+1}.")


# dict with commandname and expected parametertypes as list of strings with:
# [r]egister, [d]evice, [n]umber, [s]tring
# no need to consider aliases / defined constants since handled elsewhere and substituted automatically
# example, command foo expects string or integer as only parameter: "foo" : ["si"]
# staticmethod of name foo must be part of Instructions class
# TODO: hook for common branching suffixes
instruction_dict = {
    "alias" : ["s", "rd"],
    "define" : ["s", "n"],

    # TODO: are registers actually allowed here? (If so replace in compiler too)
    # jump types (also used for branching)
    "j" : ["n"],
    "jal" : ["n"],
    "jr" : ["n"],
    # TODO: notice stack overflows (stack property access)
    
    # branching conditions
    "_eq" : ["rn", "rn"],
    "_eqz" : ["rn"],
    "_ge" : ["rn", "rn"],
    "_gez" : ["rn"],
    "_gt" : ["rn", "rn"],
    "_gtz" : ["rn"],
    "_le" : ["rn", "rn"],
    "_lez" : ["rn"],
    "_lt" : ["rn", "rn"],
    "_ltz" : ["rn"],
    "_ne" : ["rn", "rn"],
    "_nez" : ["rn"],
    "_dns" : ["d"],
    "_dse" : ["d"],
    "_ap" : ["rn", "rn", "rn"],
    "_apz" : ["rn", "rn"],
    "_na" : ["rn", "rn", "rn"],
    "_naz" : ["rn", "rn"],

    # I/O
    "l" : ["r", "d", "s"],
    # TODO: are registers also allowed for batch device type?
    # TODO: check batchMode types and actually implement environment with batch devices, list of device type
    # TODO: also support numbers instead of reagent mode batch mode name (see stationeering.com)
    "lb" : ["r", "n", "s", "sn"],
    "lr" : ["r", "d", "sn", "s"],
    # TODO: also register as slot allowed?
    "ls" : ["r", "d", "n", "s"],
    # TODO: according to stationeering.com here no integer number allowed?!
    "s" : ["d", "s", "rn"],
    # TODO: according to stationeering.com here no integer number allowed?!
    "sb" : ["n", "s", "rn"],

    # variable selection
    "select" : ["r", "rn", "rn", "rn"],

    # arithmetic
    "abs" : ["r", "rn"],
    "acos" : ["r", "rn"],
    "asin" : ["r", "rn"],
    "atan" : ["r", "rn"],
    "ceil" : ["r", "rn"],
    "cos" : ["r", "rn"],
    "exp" : ["r", "rn"],
    "floor" : ["r", "rn"],
    "log" : ["r", "rn"],
    "round" : ["r", "rn"],
    "sin" : ["r", "rn"],
    "sqrt" : ["r", "rn"],
    "tan" : ["r", "rn"],
    "trunc" : ["r", "rn"],

    "add" : ["r", "rn", "rn"],
    "div" : ["r", "rn", "rn"],
    "max" : ["r", "rn", "rn"],
    "min" : ["r", "rn", "rn"],
    "mod" : ["r", "rn", "rn"],
    "mul" : ["r", "rn", "rn"],
    "sub" : ["r", "rn", "rn"],
    
    "rand" : ["r"],

    # Logic
    "_and" : ["r", "rn", "rn"],
    "nor" : ["r", "rn", "rn"],
    "_or" : ["r", "rn", "rn"],
    "xor" : ["r", "rn", "rn"],

    # Stack
    "peek" : ["r"],
    "pop" : ["r"],
    "push" : ["rn"],

    # Misc
    "hcf" : [],
    "move" : ["r", "rn"],
    "sleep" : ["rn"],  # could be used for debugging since no meaning here
    "_yield" : [],



}


class Instructions:
    @staticmethod
    def _get(ic, p, numeric=False, device=False, name=False): 
        if isinstance(p, PRegister):
            if device or name:
                raise InstructionException(f"Did not expect register {p} on line {ic._ip+1}.")
            return ic._registers[p.idx]
        if isinstance(p, PDevice):
            if numeric or name:
                raise InstructionException(f"Did not expect device {p} on line {ic._ip+1}.")
            return ic._devices[p.name]
        if isinstance(p, PNumber):
            if device or name:
                raise InstructionException(f"Did not expect number {p} on line {ic._ip+1}.")
            return p.value
        if isinstance(p, PName):
            if device or numeric:
                raise InstructionException(f"Did not expect name {p} on line {ic._ip+1}.")
            return p.string


    @staticmethod
    def alias(ic, name, replacement):
        if isinstance(replacement, PDevice):
            if replacement.name != "db":
                ic._device_names[name.string] = replacement
        ic._aliases[name.string] = replacement
    

    @staticmethod
    def define(ic, name, replacement):
        ic._aliases[name.string] = replacement


    # TODO: use those methods as templates for b#* instructions with * beeing one of: 
    # "al" (store ic+1 in ra), "r" (relative jump) or ""
    # r always follows b directly as in breq
    # al always at the end as in beqal
    # and # beeing a conditional (see beneath jr)
    @staticmethod
    def j(ic, address):
        ic._ip = Instructions._get(ic, address)    
        return True
    

    @staticmethod
    def jal(ic, address):
        ic._registers[_RA] = ic._ip + 1  # store next (!) line
        ic._ip = Instructions._get(ic, address)    
        return True
    

    @staticmethod
    def jr(ic, address):
        ic._ip += Instructions._get(ic, address)    
        return True


    # there is no jral or any branch combination with both al and r!


    # conditionals
    # https://stationeers-wiki.com/MIPS
    # comparsions between non integers should not happen and recognized before
    @staticmethod
    def _eq(ic, a, b):
        va = Instructions._get(ic, a)
        vb = Instructions._get(ic, b)
        return va == vb
    

    @staticmethod
    def _eqz(ic, a):
        va = Instructions._get(ic, a)
        return va == 0
    

    @staticmethod
    def _ge(ic, a, b):
        va = Instructions._get(ic, a)
        vb = Instructions._get(ic, b)
        return va >= vb
    

    @staticmethod
    def _gez(ic, a):
        va = Instructions._get(ic, a)
        return va >= 0


    @staticmethod
    def _gt(ic, a, b):
        va = Instructions._get(ic, a)
        vb = Instructions._get(ic, b)
        return va > vb
    

    @staticmethod
    def _gtz(ic, a):
        va = Instructions._get(ic, a)
        return va > 0

    
    @staticmethod
    def _le(ic, a, b):
        va = Instructions._get(ic, a)
        vb = Instructions._get(ic, b)
        return va <= vb
    

    @staticmethod
    def _lez(ic, a):
        va = Instructions._get(ic, a)
        return va <= 0


    @staticmethod
    def _lt(ic, a, b):
        va = Instructions._get(ic, a)
        vb = Instructions._get(ic, b)
        return va < vb
    

    @staticmethod
    def _ltz(ic, a):
        va = Instructions._get(ic, a)
        return va < 0


    @staticmethod
    def _ne(ic, a, b):
        va = Instructions._get(ic, a)
        vb = Instructions._get(ic, b)
        return va != vb
    

    @staticmethod
    def _nez(ic, a):
        va = Instructions._get(ic, a)
        return va != 0

    @staticmethod
    def _dns(ic, d):
        return ic._devices[d.name] is None
    

    @staticmethod
    def _dse(ic, d):
        return ic._devices[d.name] is not None


    # approximate equations from https://stationeers-wiki.com/MIPS
    @staticmethod
    def _ap(ic, a, b, err):
        va = Instructions._get(ic, a)
        vb = Instructions._get(ic, b)
        return abs(va - vb) <= max(err * max(abs(va), abs(vb)), sys.float_info.epsilon * 8)
    

    @staticmethod
    def _apz(ic, a, err):
        va = Instructions._get(ic, a)
        return abs(va) <= max(err * abs(va), sys.float_info.epsilon * 8)
    

    @staticmethod
    def _na(ic, a, b, err):
        va = Instructions._get(ic, a)
        vb = Instructions._get(ic, b)
        return not (abs(va - vb) <= max(err * max(abs(va), abs(vb)), sys.float_info.epsilon * 8))
    

    @staticmethod
    def _naz(ic, a, err):
        va = Instructions._get(ic, a)
        return not (abs(va) <= max(err * abs(va), sys.float_info.epsilon * 8))


    @staticmethod
    def _branch(match, ic, *params):
        relative = match[1] is not None
        cond = "_" + match[2]
        al = match[3] is not None
        if al and relative:
            raise InstructionException(f"Branching instructions on line {ic._ip+1} with both r and al does not exist.")

        if not getattr(Instructions, cond)(ic, *params[:-1]):  # don't branch
            return False

        # branch
        if al:
            return Instructions.jal(ic, params[-1])

        elif relative:
            return Instructions.jr(ic, params[-1])
        else:
            return Instructions.j(ic, params[-1])
    
    @staticmethod
    def _set(match, ic, *params):
        cond = "_" + match[1]
        ic._registers[params[0].idx] = float(getattr(Instructions, cond)(ic, *params[1:]))
        return False

    @staticmethod
    def select(ic, reg, a, b, c):
        va = Instructions._get(ic, a)
        vb = Instructions._get(ic, b)
        vc = Instructions._get(ic, c)
        ic._registers[reg.idx] = vb if va != 0 else vc
        return False


    @staticmethod
    def abs(ic, reg, a):
        va = Instructions._get(ic, a)
        ic._registers[reg.idx] = abs(va)
        return False
   


    @staticmethod
    def acos(ic, reg, a):
        va = Instructions._get(ic, a)
        ic._registers[reg.idx] = math.acos(va)
        return False
    

    @staticmethod
    def asin(ic, reg, a):
        va = Instructions._get(ic, a)
        ic._registers[reg.idx] = math.asin(va)
        return False
    

    @staticmethod
    def atan(ic, reg, a):
        va = Instructions._get(ic, a)
        ic._registers[reg.idx] = math.atan(va)
        return False

    
    @staticmethod
    def ceil(ic, reg, a):
        va = Instructions._get(ic, a)
        ic._registers[reg.idx] = math.ceil(va)
        return False
    

    @staticmethod
    def cos(ic, reg, a):
        va = Instructions._get(ic, a)
        ic._registers[reg.idx] = math.cos(va)
        return False
    

    @staticmethod
    def exp(ic, reg, a):
        va = Instructions._get(ic, a)
        ic._registers[reg.idx] = math.exp(va)
        return False
    

    @staticmethod
    def floor(ic, reg, a):
        va = Instructions._get(ic, a)
        ic._registers[reg.idx] = math.floor(va)
        return False
    

    @staticmethod
    def log(ic, reg, a):
        va = Instructions._get(ic, a)
        ic._registers[reg.idx] = math.log(va)
        return False
    

    @staticmethod
    def round(ic, reg, a):
        va = Instructions._get(ic, a)
        ic._registers[reg.idx] = math.round(va)
        return False
    

    @staticmethod
    def sin(ic, reg, a):
        va = Instructions._get(ic, a)
        ic._registers[reg.idx] = math.sin(va)
        return False
    

    @staticmethod
    def sqrt(ic, reg, a):
        va = Instructions._get(ic, a)
        ic._registers[reg.idx] = math.sqrt(va)
        return False
    

    @staticmethod
    def tan(ic, reg, a):
        va = Instructions._get(ic, a)
        ic._registers[reg.idx] = math.tan(va)
        return False
    

    @staticmethod
    def trunc(ic, reg, a):
        va = Instructions._get(ic, a)
        ic._registers[reg.idx] = math.trunc(va)
        return False
    

    @staticmethod
    def add(ic, reg, a, b):
        va = Instructions._get(ic, a)
        vb = Instructions._get(ic, b)
        ic._registers[reg.idx] = va + vb
        return False
    

    @staticmethod
    def div(ic, reg, a, b):
        va = Instructions._get(ic, a)
        vb = Instructions._get(ic, b)
        ic._registers[reg.idx] = va / vb
        return False
    

    @staticmethod
    def max(ic, reg, a, b):
        va = Instructions._get(ic, a)
        vb = Instructions._get(ic, b)
        ic._registers[reg.idx] = max(va, vb)
        return False
    

    @staticmethod
    def min(ic, reg, a, b):
        va = Instructions._get(ic, a)
        vb = Instructions._get(ic, b)
        ic._registers[reg.idx] = min(va, vb)
        return False
    
    @staticmethod
    def mod(ic, reg, a, b):
        va = Instructions._get(ic, a)
        vb = Instructions._get(ic, b)
        ic._registers[reg.idx] = va % vb  # python % is actually mod!
        return False
    

    @staticmethod
    def mul(ic, reg, a, b):
        va = Instructions._get(ic, a)
        vb = Instructions._get(ic, b)
        ic._registers[reg.idx] = va * vb
        return False
    

    @staticmethod
    def sub(ic, reg, a, b):
        va = Instructions._get(ic, a)
        vb = Instructions._get(ic, b)
        ic._registers[reg.idx] = va - vb
        return False


    @staticmethod
    def rand(ic, reg):
        ic._registers[reg.idx] = random.random()
        return False
    
    
    @staticmethod
    def _and(ic, reg, a, b):
        va = Instructions._get(ic, a)
        vb = Instructions._get(ic, b)
        ic._registers[reg.idx] = va and vb
        return False
    

    @staticmethod
    def nor(ic, reg, a, b):
        va = Instructions._get(ic, a)
        vb = Instructions._get(ic, b)
        ic._registers[reg.idx] = not (va or vb)
        return False
    

    @staticmethod
    def _or(ic, reg, a, b):
        va = Instructions._get(ic, a)
        vb = Instructions._get(ic, b)
        ic._registers[reg.idx] = va or vb
        return False
    

    @staticmethod
    def xor(ic, reg, a, b):
        va = Instructions._get(ic, a)
        vb = Instructions._get(ic, b)
        ic._registers[reg.idx] = va != vb
        return False
    

    @staticmethod
    def push(ic, a):
        if ic._registers[_SP]>=512:
            raise InstructionException(f"Stack overflow on line {ic._ip+1}.")
        va = Instructions._get(ic, a)
        ic._stack[ic._registers[_SP]] = va
        ic._registers[_SP]+=1
        return False
    

    @staticmethod
    def pop(ic, reg):
        ic._registers[_SP]-=1
        ic._registers[reg.idx] = ic._stack[ic._registers[_SP]] 
        return False
    

    @staticmethod
    def peek(ic, reg):
        ic._registers[reg.idx] = ic._stack[ic._registers[_SP]-1] 
        return False
   

    @staticmethod
    def move(ic, reg, a):
        va = Instructions._get(ic, a)
        ic._registers[reg.idx] = va 
        return False

   
    @staticmethod
    def hcf(ic):
        pass
        return False
    

    @staticmethod
    def sleep(ic, va):
        return False
    

    @staticmethod
    def _yield(ic):
        return False
    

    @staticmethod
    def l(ic, reg, dev, prop):
        if prop.string not in ic._devices[dev.name]:
            raise InstructionException(f"Unset property {dev.name}.{prop.string} accessed on line {ic._ip+1}.")
        ic._registers[reg.idx] = ic._devices[dev.name][prop.string]
        return False
    

    @staticmethod
    def lb(ic, reg, bdev, prop, mode):
        # TODO
        raise NotImplementedError
        return False
    

    @staticmethod
    def lr(ic, reg, dev, slot, reag):
        # TODO
        raise NotImplementedError
        return False
    

    @staticmethod
    def s(ic, dev, prop, a):
        va = Instructions._get(ic, a)
        # Creation of entry if nonexistant is intended.
        ic._devices[dev.name][prop.string] = va
        return False
    

    @staticmethod
    def sb(ic, bdev, prop, a):
        va = Instructions._get(ic, a)
        # TODO
        raise NotImplementedError
        return False
