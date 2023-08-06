from enum import Enum
from collections import namedtuple
from dataclasses import dataclass

from .tokens import *

__all__ = ["ExprGraph", "find_by_index"]

def find_by_index(lst, idx, item):
    for i, entry in enumerate(lst):
        if entry[idx] == item:
            return i
    return -1

class IndexingPlaceholder:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"IndexingPlaceholder{{{self.name}}}"

    def get_name(self):
        return self.name


class ExprGraph:
    @dataclass
    class Node:
        root : object  # is Node but doesn't exist at time of annotation evaluation
        reg : int
        op : str
        params : list
        reserved_registers : list = None
    
    OpInfo = namedtuple("OpInfo", ["op", "result_reg", "param_regs"])
    N_REGISTERS = 15
    ALL_REGISTERS = set(range(N_REGISTERS))

    def __init__(self, op):
        self._root = __class__.Node(None, None, op, [])
        self._iterator = self._root        

    def crawler(self, fnc, origin = None, depth=0):
        if origin is None:
            origin = self._root
        fnc(origin, depth)
        for p in origin.params:
            self.crawler(fnc, p, depth+1)
            self._iterator = origin
    
    def reversed_crawler(self, fnc, origin=None, depth=0):
        if origin is None:
            origin = self._root
        for p in origin.params:
            self.reversed_crawler(fnc, p, depth+1)
            self._iterator = origin
        fnc(origin, depth)



    def append(self, op):
        self._iterator.params.append(__class__.Node(self._iterator, None, op, []))
        self._iterator = self._iterator.params[-1]
    
    def append_graph(self, sub_graph):
        # replace root of subgraph       
        for p in sub_graph._root.params:
            p.root=self._iterator
        
        # connect graph
        self._iterator.params.extend(sub_graph._root.params)

    def move_back(self):
        # move iterator back on graph
        if self._iterator.root: 
            self._iterator = self._iterator.root
        else:
            raise Exception("Trying to move back from root node of graph.") 
    
    def move_forward(self, param):
        # move iterator forward on graph
        if len(self._iterator.params)>param:
            self._iterator = self._iterator.params[param]
        else:
            raise Exception("Trying to move to nonexistant node.")
    
    def get(self):
        paramregs = [p.reg for p in self._iterator.params]
        return __class__.OpInfo(self._iterator.op, self._iterator.reg, paramregs)
    
    def get_depth(self):
        it = self._iterator
        i = 0
        while it:=it.root:
            i+=1
        return i

    def set_iterator(self, node):
        self._iterator = node
    
    def get_iterator(self):
        return self._iterator

    def reset_iterator(self):
        self._iterator = self._root

    def get_root(self):
        return self._root

    def __str__(self):
        res = ""
        def fnc(p, depth):
            nonlocal res
            res+=' '*depth + "|" + str(p.op)
            res+= ((" in r"+str(p.reg)) if p.reg is not None else "") + (" reserved: " + str(p.reserved_registers) if p.reserved_registers else "") + "\n"
        self.crawler(fnc, self._root)
        return res
    
    def eval_registers(self):
        reg_stack = [set()]
        def crawler(node, depth):
            # non device access except for indexing
            if type(node.op) is IndexingPlaceholder:
                if (node.params[0].op == "id") and (type(node.params[0].params[0].op) is IntegerNumber):
                    node.reg = node.params[0].params[0].op.get_value()
                elif (node.params[0].op == "id") and (type(node.params[0].params[0].op) is VarName):  # with constant
                    node.reg = node.params[0].params[0].op
                else:
                    raise CompilerException("Slot must be an integer or constant.")
                node.params = []
            if node.root and (type(node.root.op) is str) and (node.root.op == "."): 
                return
            if depth>=len(reg_stack):
                reg_stack.append(set())
            if not isinstance(node.op, NumberLiteral):
                # determine register of current node
                # used registers for parent node operation are safed within the parent node (depth-1)
                # allow parent node register if not used on level depth
                reserved_regs = set().union(*reg_stack[:depth-1])
                if node.root and (node.root.reg is not None):
                    reserved_regs-={node.root.reg}
                reserved_regs|=reg_stack[depth-1]
                
                node.reserved_registers = reserved_regs  # only used for FunctionCall

                pick = sorted((__class__.ALL_REGISTERS - reserved_regs))[0]  # smallest available register (since other parts of the program unfortunatly use it this way)
                if depth>0:  # not needed for root gives one more register
                    reg_stack[depth-1].add(pick)  # reserve register on current depth-level
                
                node.reg = pick

            for p in node.params:
                crawler(p, depth+1)
            
            del reg_stack[depth:]  # not needed anymore since at this point already executed (everything to the right in graph)
        
        crawler(self._root, 0)


    def invalidate_registers(self):
        def invalid(node, _): 
            node.reg = None 
            node.reserved_registers = []
        self.crawler(invalid, self._root)

    def used_registers(self):
        max_ = 0
        def get_max(n, _): 
            nonlocal max_
            if n.root and n.root.op == ".":  # reg has diffrent meaning in this case
                return
            if n.reg is not None:
                max_ = max(max_, n.reg)
        self.crawler(get_max)
        return max_ + 1  # +1 due to r0
