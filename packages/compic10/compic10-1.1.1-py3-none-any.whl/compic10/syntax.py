import itertools

from .tokens import *
from .compilerexception import CompilerException
from .compilerutil import *
from .programdatabase import ProgramDatabase

# syntax acts like a template for an concept
# function match_syntax is applied to an token tree and yields all detected syntaxes
# single token can only be part of one syntax higher priority token will remain if they overlapp
# syntaxes are evaluated according to the priority
# tokens that don't belong to an syntax invoke compile errors
# tokens have the value parent_syntax in order to assign them to syntaxes after eliminating overlapping syntaxes
# syntaxes like if do find subsyntaxes like condition expression on their own (check parent of token and add this subsyntax)
# in the end every line is only one root token with subtokens

# just to determine the first syntax will probably not work like that
def syntactic_analysis(_token_tree):
    if not _token_tree: return None
    for syntax in all_syntaxes:
            if syntax.match_token(_token_tree[0]):
                found = syntax(_token_tree)
                if len(found.get_token_family()) != len(_token_tree):
                    raise CompilerException(f"Stray tokens found: {_token_tree[len(found.get_token_family()):]}.")
                return found
    raise CompilerException("No known syntax found.")


class Syntax:
    # syntaxorder e.g. * before + before if
    _inducedby = []  # templates which induce this token

    def __init__(self, _token_tree):
        self.__token_vicinity = _token_tree
        self._token_family = []  # token_family are tokens belonging to this syntax
    
    def get_token_family(self):
        return self._token_family[:]

    @classmethod
    def match_token(cls, token):
        return isinstance(token, tuple(cls._inducedby))


class Expression(Syntax):    
    _inducedby = [Operation, Operand]
    __operator_priority = [
        # operator class (most abstract), priority (higher evaluates before lower), as unary operation True/False
        (OperatorDot, 999, False),  # must stay highest priority no matter what
        
        (OperatorInc, 12, True),
        (OperatorDec, 12, True),

        (OperatorAdd, 11, True),
        (OperatorSub, 11, True),        
        (OperatorNeg, 11, True),

        (OperatorMul, 10, False),
        (OperatorDiv, 10, False),
        (OperatorMod, 10, False),
        
        (OperatorAdd, 9, False),
        (OperatorSub, 9, False),
        
        (OperatorShl, 8, False),
        (OperatorShr, 8, False),
        
        (OperatorBitwiseAnd, 7, False),
        
        (OperatorBitwiseXor, 6, False),
        
        (OperatorBitwiseOr, 5, False),

        (OperatorEq, 4, False),
        (OperatorNeq, 4, False),
        (OperatorLt, 4, False),
        (OperatorLte, 4, False),
        (OperatorGt, 4, False),
        (OperatorGte, 4, False),

        (OperatorNot, 3, True),
        
        (OperatorAnd, 2, False), 
        
        (OperatorOr, 1, False), 

        (OperatorAssign, 0, False), 
        (OperatorAddAssign, 0, False), 
        (OperatorSubAssign, 0, False), 
        (OperatorMulAssign, 0, False), 
        (OperatorDivAssign, 0, False), 
        (OperatorModAssign, 0, False), 
        (OperatorAndAssign, 0, False), 
        (OperatorOrAssign, 0, False), 
    ]

    @classmethod
    def __determine_priority(Cls, operator_token, unary_context):
        for op in Cls.__operator_priority:
            if isinstance(operator_token, op[0]) and unary_context==op[2]:
                return op[1]
        raise CompilerException(f"Unknown operator priority {operator_token.get_rawstring()}.")


    def __str__(self):
        repr_str = ""
        for token, subs in self.__subsyntaxes:
            repr_str += "Subsyntaxes for: " + token.get_rawstring() + "\n"
            repr_str += "\t" + str(subs).replace("\n", "\n\t")[:-1]
        for call in self.__calls:
            repr_str += "operator" + call[0] + "(" + "".join([(("prev res " + str(param) + ", ")  if type(param) is int else (param.get_rawstring() +", ")) for param in call[1]])[:-2] + ")\n"
        return repr_str

    def get_calls(self):
        return self.__calls[:]

    def get_subsyntaxes(self):
        return self.__subsyntaxes[:]

    def __init__(self, _token_tree):
        super().__init__(_token_tree)
        self.__subsyntaxes = []  # can only be expressions and Parameters
        # must be evaluated from left to right tokenindex wise except for operations depending on others

        # find last token of expression and operations
        cur_token = _token_tree[0]
        index = 0
        operation_indizes = []
        while isinstance(cur_token, tuple(self._inducedby)):
            self._token_family.append(cur_token)
            if isinstance(cur_token, Operation):
                operation_indizes.append(index)
            index+=1
            if index<len(_token_tree):
                cur_token = _token_tree[index]
            else: break
        last_index = index

        if len(_token_tree) != last_index:
            raise CompilerException("Stray tokens.")

        # evaluate operations
        # operation group format: [([list of token family], priority of operation, unary operation True/False)...]
        operation_groups = []
        # evaluation order gets determinend from that
        for index in operation_indizes:
            cur_token = _token_tree[index]
            next_token = _token_tree[index+1] if (index+1)<last_index else None
            prev_token = _token_tree[index-1] if index>0 else None

            # remove tokens which are not part of the expression
            if not isinstance(next_token, tuple(self._inducedby)): next_token = None
            if not isinstance(prev_token, tuple(self._inducedby)): prev_token = None
            
            # case binary operation: binary operator, to the left operand, to the right operand, unary operator
            if isinstance(cur_token, BinaryOperation) and isinstance(prev_token, Operand) and isinstance(next_token, (Operand, UnaryOperation)):
                asgn_ops = [OperatorAssign, OperatorAddAssign, OperatorSubAssign,
                            OperatorDivAssign, OperatorMulAssign, OperatorModAssign]
                if isinstance(cur_token, tuple(asgn_ops)):  # assignement operations must be evalutated from right to left so assignments like a=b=c are possible otherwise would be assignment to expression
                    i = len(operation_groups)-1
                    while((i>=0) and isinstance(operation_groups[i][0][-2], tuple(asgn_ops+[OperatorDot]))):  # -2 since this is always second to last and for unary and binary cur_token <-> the operator (dot operations have special treatment since normally equal to variable)
                        i-=1
                    operation_groups.insert(i+1, ([prev_token, cur_token, next_token], Expression.__determine_priority(cur_token, False), False))
                else:
                    operation_groups.append(([prev_token, cur_token, next_token], Expression.__determine_priority(cur_token, False), False))

            # case unary operation: unary operator, to the left None/binary operator to the right operand
            elif isinstance(cur_token, UnaryOperation) and isinstance(prev_token, (BinaryOperation, type(None))) and isinstance(next_token, Operand):
                operation_groups.append(([cur_token, next_token], Expression.__determine_priority(cur_token, True), True))

            # unknown
            else:
                raise CompilerException(f"Ill formed operation {cur_token.get_rawstring()}")


        # sort operations according to priority from high to low
        operation_groups = sorted(operation_groups, key=lambda ele: ele[1], reverse=True)
        # function, that determines token part of previous operation (tighter binding than current operation)
        def already_evaluated(token, prev_calls, only_last=False):
            for i, (_, params, op) in enumerate(reversed(prev_calls)):
                for param in [*params, op]:  # op too due to unary operations
                    if not isinstance(param, Token):  # call to former operation -> param is index of this operation
                        ret = already_evaluated(token, prev_calls[:param+1], only_last=True)
                        if ret != -1: 
                            return len(prev_calls)-1-i
                    else:  # token param
                        if token is param: 
                            return len(prev_calls)-1-i  # is very important here since there could be several equal tokens
                if only_last:
                    break
            return -1  # not found
                
        # associate operations with operands or previous operation results
        calls = []  # list of previous calls format: list of (operator as str, [params], operatortoken)
        if last_index == 1 and isinstance(_token_tree[0], Operand):  # only operand without expression (last_index == 1 -> only one token)
            calls = [("id", [_token_tree[0]], None)]  # identity operation e.g. do nothing
        
        # iterate over alle operations in expression (not subexpressions those are tokens) 
        # not called if no operations (single operand handled by previous if)
        for i, op in enumerate(operation_groups):
            if op[2]:  # unary operation
                # op[0][-1] is operand token of unary operation
                param = already_evaluated(op[0][-1], calls[:i])  # check next_element already evaluated
                # param is index of operation_groups entry
                if param == -1: param = op[0][-1]  # param is actual operand otherwise int with index in calls
                calls.append((op[0][0].get_rawstring(), [param], op[0][0]))
            else:  # binary operation
                param0 = already_evaluated(op[0][0], calls[:i])  # check prev_element already evaluated
                # param0 is index of operation_groups entry
                if param0 == -1: param0 = op[0][0]  # # param0 is actual operand otherwise int with index in calls
                param1 = already_evaluated(op[0][-1], calls[:i])  # check next_element already evaluated
                # param1 is index of operation_groups entry
                if param1 == -1: param1 = op[0][-1]  # # param1 is actual operand otherwise int with index in calls
                calls.append((op[0][1].get_rawstring(), [param0, param1], op[0][1]))
            # op[2] must be changed to an enum if tertiary operations will ever come (could use all those special branching operations)
        
        if not calls:  # empty
            raise CompilerException("Empty expressions are not allowed.")
        # special case device access is whole expression extra id operation needed (like single operand expressions)
        if calls[0][0] == ".":
            calls.append(("id", [len(calls)-1], None))
        # all expression tokens must be part of at least one element of first list in tuple from operations_groups 
        # in addition to that they must be connected with all other operations (tested in codegen)
        used_tokens = set(itertools.chain(*list(map(lambda c: c[1], calls)))) | set(map(lambda c: c[2], calls))
        for token in _token_tree[:last_index]:
            if token not in used_tokens:
                raise CompilerException(f"Atom is not part of any operation {token.get_rawstring()}")
        
        self.__calls = calls
        
        # call for evaluation of subsyntaxes which includes subtokens
        for token in _token_tree[:last_index]:
            subtoken_tree = token.get_subtokens()
            if len(subtoken_tree) == 0:
                if isinstance(token, Braces):
                    raise CompilerException("Can't have empty braces in expression.")
                elif isinstance(token, FunctionCall):
                    self.__subsyntaxes.append((token, None))  # otherwise problems in expression codegen
                elif isinstance(token, Indexing):
                    raise CompilerException("Can't have empty indexing brackets.")
            else:
                if isinstance(token, Braces):
                    cur_subsyntax = Expression(subtoken_tree)
                elif isinstance(token, FunctionCall):
                    cur_subsyntax = Parameters(subtoken_tree)
                elif isinstance(token, Indexing):
                    cur_subsyntax = Expression(subtoken_tree)
                else:
                    raise CompilerException("Unexpected subsyntax.")
                self.__subsyntaxes.append((token, cur_subsyntax))
        # self._token_family = _token_tree[:last_index]
        

class Parameters(Syntax):
    _inducedby = [Comma]
    def __init__(self, _token_tree, *, subsyntax_types=Expression):
        super().__init__(_token_tree)
        self.__subsyntaxes = []
        self.__subsyntax_types = subsyntax_types
        tokentrees = []
        start_index = 0
        index = 0
        while index < len(_token_tree):
            if isinstance(_token_tree[index], Comma):
                tokentrees.append(_token_tree[start_index:index])
                start_index = index+1
                index = start_index
            else:
                index+=1
        tokentrees.append(_token_tree[start_index:])
        for index, subtoken_tree in enumerate(tokentrees):
            if len(subtoken_tree) == 0:
                raise CompilerException("Empty parameter in Parameterlist.")
            if type(subsyntax_types) is list:
                if index >= len(subsyntax_types):
                    raise CompilerException("Too many parameters.")
                if type(subsyntax_types[index]) in (list, tuple):
                    for ss in subsyntax_types[index]:
                        if ss.match_token(subtoken_tree[0]):
                            cur_subsyntax = ss(subtoken_tree)
                            break
                    else:
                        raise CompilerException(f"Wrong parameter type at paramter {index}.")
                else:
                    if subsyntax_types[index].match_token(subtoken_tree[0]):
                        cur_subsyntax = subsyntax_types[index](subtoken_tree)
                    else:
                        raise CompilerException(f"Wrong parameter type at paramter {index}.")
            else:
                cur_subsyntax = subsyntax_types(subtoken_tree)
            self.__subsyntaxes.append((index, cur_subsyntax))
        self._token_family = _token_tree[:]
        
        # check if all are expressions

    def get_parameter_syntaxes(self):
        return self.__subsyntaxes

    def __str__(self):
        repr_str = "Parameters:\n"
        for ss in self.__subsyntaxes:
            repr_str+="\t"+str(ss[1])
        return repr_str


class IfSyntax(Syntax):
    _inducedby = [IfToken]

    def __init__(self, _token_tree):
        super().__init__(_token_tree)
        if not isinstance(_token_tree[0], IfToken):
            raise CompilerException("If-syntax must start with an if-token.")
        self.__condition_expression = Expression(_token_tree[0].get_subtokens())
        self._token_family = _token_tree[:1]

    def get_condition(self):
        return self.__condition_expression

    def __str__(self):
        return "if\n\t"+str(self.__condition_expression).replace("\n","\n\t")[:-1]


class ElifSyntax(Syntax):
    _inducedby = [ElifToken]

    def __init__(self, _token_tree):
        super().__init__(_token_tree)
        if not isinstance(_token_tree[0], ElifToken):
            raise CompilerException("elif-syntax must start with an elif-token.")
        self.__condition_expression = Expression(_token_tree[0].get_subtokens())
        self._token_family = _token_tree[:1]

    def get_condition(self):
        return self.__condition_expression

    def __str__(self):
        return "elif\n\t"+str(self.__condition_expression).replace("\n", "\n\t")[:-1]


class ElseSyntax(Syntax):
    _inducedby = [ElseToken]

    def __init__(self, _token_tree):
        super().__init__(_token_tree)
        if not isinstance(_token_tree[0], ElseToken):
            raise CompilerException("else-syntax must start with an else-token.")
        self._token_family = _token_tree[:1]

    def __str__(self):
        return "else"


class WhileSyntax(Syntax):
    _inducedby = [WhileToken]

    def __init__(self, _token_tree):
        super().__init__(_token_tree)
        if not isinstance(_token_tree[0], WhileToken):
            raise CompilerException("while-syntax must start with an while-token.")
        self.__condition_expression = Expression(_token_tree[0].get_subtokens())
        self._token_family = _token_tree[:1]

    def get_condition(self):
        return self.__condition_expression

    def __str__(self):
        return "while\n\t"+str(self.__condition_expression).replace("\n", "\n\t")[:-1]


class ForSyntax(Syntax):
    _inducedby = [ForToken]

    def __init__(self, _token_tree):
        super().__init__(_token_tree)
        if not isinstance(_token_tree[0], ForToken):
            raise CompilerException("for-syntax must start with an for-token.")
        self.__loop_parameters = Parameters(_token_tree[0].get_subtokens(), subsyntax_types=[[VariableDeclarationSyntax, Expression]] + [Expression]*2)
        self._token_family = _token_tree[:1]

    def __str__(self):
        return "for\n"\
            + "\tinit: "+str(self.__loop_parameters.get_parameter_syntaxes()[0])\
            + "\tcondition: "+str(self.__loop_parameters.get_parameter_syntaxes()[1])\
            + "\titeration: "+str(self.__loop_parameters.get_parameter_syntaxes()[2])
    

    def get_loopparameters(self):
        return self.__loop_parameters.get_parameter_syntaxes()


class EndSyntax(Syntax):
    _inducedby = [EndToken]

    def __init__(self, _token_tree):
        super().__init__(_token_tree)
        if not isinstance(_token_tree[0], EndToken):
            raise CompilerException("end-syntax must start with an end-token.")
        self._token_family = _token_tree[:1]
    
    def __str__(self):
        return "end"


class VariableDeclarationSyntax(Syntax):
    _inducedby = [VarToken]

    def __init__(self, _token_tree):
        super().__init__(_token_tree)
        if not isinstance(_token_tree[0], VarToken):
            raise CompilerException("var-syntax must start with an var-token.")
        if not isinstance(_token_tree[1], VarName):
            raise CompilerException("var keyword must be followed by variable name.")
        self.__var_token = _token_tree[1]
        self.__init_expr = None
        self._token_family = _token_tree[:2]
        if len(_token_tree)>2:
            if not isinstance(_token_tree[2], OperatorAssign) or not Expression.match_token(_token_tree[3]):
                raise CompilerException("Invalid Assignment in variable declaration.")
            else:
                self.__init_expr = Expression(_token_tree[3:])
                self._token_family = _token_tree[:]

    def __str__(self):
        return "var: " + self.__var_token.get_name()
    
    def get_init_expr(self):
        return self.__init_expr
    
    def get_name(self):
        return self.__var_token.get_name()


class ConstantDeclarationSyntax(Syntax):
    _inducedby = [ConstToken]

    def __init__(self, _token_tree):
        super().__init__(_token_tree)
        if not isinstance(_token_tree[0], ConstToken):
            raise CompilerException("const-syntax must start with an const-token.")
        if not isinstance(_token_tree[1], VarName):
            raise CompilerException("const keyword must be followed by variable name.")
        if isinstance(_token_tree[2], OperatorAssign) and isinstance(_token_tree[3], NumberLiteral):
            self._token_family = _token_tree[:4]
            self.__value_token = _token_tree[3]
            self.__negative = False
        elif isinstance(_token_tree[2], OperatorAssign) and isinstance(_token_tree[3], (OperatorAdd, OperatorSub)) and isinstance(_token_tree[4], NumberLiteral):  # since no expressions allowed and negative literals don't exist
            self._token_family = _token_tree[:5]
            self.__value_token = _token_tree[4]
            self.__negative = isinstance(_token_tree[3], OperatorSub) 
        else:    
            raise CompilerException("Invalid assignment in const declaration.")
        self.__var_token = _token_tree[1]

    def __str__(self):
        return "const: " + self.__var_token.get_name()

    def get_name(self):
        return self.__var_token.get_name()
    
    def get_value(self):
        return self.__value_token.get_value() * (-1 if self.__negative else 1)


class DeviceDeclarationSyntax(Syntax):
    _inducedby = [DevToken]

    def __init__(self, _token_tree):
        super().__init__(_token_tree)
        if not isinstance(_token_tree[0], DevToken):
            raise CompilerException(
                "device-syntax must start with an device-token.")
        if not isinstance(_token_tree[1], VarName):
            raise CompilerException(
                "device keyword must be followed by variable name.")
        if not (len(_token_tree) >= 4):
            raise CompilerException("No assignment in device declaration.")
        if not isinstance(_token_tree[2], OperatorAssign) or not isinstance(_token_tree[3], IntegerNumber):
            raise CompilerException("Invalid Assignment in device declaration.")
        self.__var_token = _token_tree[1]
        self.__value_token = _token_tree[3]
        if not (0<=self.__value_token.get_value()<6):
            raise CompilerException("At most 6 device slots are supported starting from 0 upto 5")
        self._token_family = _token_tree[:4]

    def __str__(self):
        return "device: " + self.__var_token.get_name()

    def get_name(self):
        return self.__var_token.get_name()

    def get_value(self):
        return self.__value_token.get_value()


class BatchDeviceDeclarationSyntax(Syntax):
    _inducedby = [BDevToken]

    def __init__(self, _token_tree):
        super().__init__(_token_tree)
        if not isinstance(_token_tree[0], BDevToken):
            raise CompilerException(
                "batch device-syntax must start with an batch device-token.")
        if not isinstance(_token_tree[1], VarName):
            raise CompilerException(
                "batch device keyword must be followed by variable name.")
        if isinstance(_token_tree[2], OperatorAssign) and isinstance(_token_tree[3], NumberLiteral):
            self._token_family = _token_tree[:4]
            self.__value_token = _token_tree[3]
            self.__negative = False
        elif isinstance(_token_tree[2], OperatorAssign) and isinstance(_token_tree[3], (OperatorAdd, OperatorSub)) and isinstance(_token_tree[4], NumberLiteral):  # since no expressions allowed and negative literals don't exist
            self._token_family = _token_tree[:5]
            self.__value_token = _token_tree[4]
            self.__negative = isinstance(_token_tree[3], OperatorSub) 
        else:    
            raise CompilerException("Invalid assignment in batch device declaration.")
        self.__var_token = _token_tree[1]

    def __str__(self):
        return "batch device: " + self.__var_token.get_name()

    def get_name(self):
        return self.__var_token.get_name()

    def get_value(self):
        return self.__value_token.get_value() * (-1 if self.__negative else 1)


class BreakSyntax(Syntax):
    _inducedby = [BreakToken]

    def __init__(self, _token_tree):
        super().__init__(_token_tree)
        if not isinstance(_token_tree[0], Token):
            raise CompilerException(
                "break-syntax must start with an break-token.")
        self._token_family = _token_tree[:1]

    def __str__(self):
        return "break"

    
class ContinueSyntax(Syntax):
    _inducedby = [ContinueToken]

    def __init__(self, _token_tree):
        super().__init__(_token_tree)
        if not isinstance(_token_tree[0], Token):
            raise CompilerException(
                "continue-syntax must start with an continue-token.")
        self._token_family = _token_tree[:1]

    def __str__(self):
        return "continue"

# func, proc, return declarations


class ReturnSyntax(Syntax):
    _inducedby = [ReturnToken]

    def __init__(self, _token_tree):
        super().__init__(_token_tree)
        if not isinstance(_token_tree[0], Token):
            raise CompilerException(
                "return-syntax must start with an return-token.")
        self._return_expression = None
        self._token_family = _token_tree[:1]
        if len(_token_tree) > 1 and _token_tree[1]:
            self._return_expression = Expression(_token_tree[1:])
            self._token_family = _token_tree[:]

    def __str__(self):
        return "return"
    
    def get_return_expression(self):
        return self._return_expression


class FuncSyntax(Syntax):
    _inducedby = [FuncToken]

    def __init__(self, _token_tree):
        super().__init__(_token_tree)
        if not isinstance(_token_tree[0], FuncToken):
            raise CompilerException("func-syntax must start with an func-token.")
        if not isinstance(_token_tree[1], FunctionCall):
            raise CompilerException("func-syntax must have an functioncall-token.")
        tokentrees = []
        start_index = 0
        index = 0
        subtoken_tree = _token_tree[1].get_subtokens()
        while index < len(subtoken_tree):
            if isinstance(subtoken_tree[index], Comma):
                tokentrees.append(subtoken_tree[start_index:index])
                start_index = index+1
                index = start_index
            else:
                index += 1
        if len(subtoken_tree[start_index:]) > 0:
            tokentrees.append(subtoken_tree[start_index:])
        self.__func_parameters = []
        self.__defaults = []
        non_defaults_allowed = True
        for token in tokentrees:
            if (len(token) == 1) and isinstance(token[0], VarName):
                if not non_defaults_allowed:
                    raise CompilerException("No non default parameters allowed after default parameters.")
                self.__func_parameters.append(token[0].get_name())
            elif (len(token) == 3) and isinstance(token[0], VarName) and isinstance(token[1], OperatorAssign) and isinstance(token[2], NumberLiteral):
                non_defaults_allowed = False
                self.__func_parameters.append(token[0].get_name())
                self.__defaults.append(token[2].get_value())
            elif (len(token) == 4) and isinstance(token[0], VarName) and isinstance(token[1], OperatorAssign) and isinstance(token[2], (OperatorAdd, OperatorSub)) and isinstance(token[3], NumberLiteral):  # since no expressions allowed and negative literals don't exist
                non_defaults_allowed = False
                self.__func_parameters.append(token[0].get_name())
                self.__defaults.append(token[3].get_value() * (-1 if isinstance(token[2], OperatorSub) else 1))
            else:
                raise CompilerException(f"Parameters of func syntax must be variable names with optional default values not {token[0].get_rawstring()}.")
        self._token_family = _token_tree[:2]

    def __str__(self):
        return "function{" + ",".join(self.__func_parameters) + "}\n"

    def get_funcparameters(self):
        return self.__func_parameters
    
    def get_defaults(self):
        return self.__defaults

    def get_name(self):
        return self._token_family[1].get_name()


class ProcSyntax(Syntax):
    _inducedby = [ProcToken]

    def __init__(self, _token_tree):
        super().__init__(_token_tree)
        if not isinstance(_token_tree[0], ProcToken):
            raise CompilerException("proc-syntax must start with an proc-token.")
        if not isinstance(_token_tree[1], FunctionCall):
            raise CompilerException("procedure-syntax must have an functioncall-token.")
        tokentrees = []
        start_index = 0
        index = 0
        subtoken_tree = _token_tree[1].get_subtokens()
        while index < len(subtoken_tree):
            if isinstance(subtoken_tree[index], Comma):
                tokentrees.append(subtoken_tree[start_index:index])
                start_index = index+1
                index = start_index
            else:
                index += 1
        if len(subtoken_tree[start_index:])>0:
            tokentrees.append(subtoken_tree[start_index:])
        self.__func_parameters = []
        self.__defaults = []
        non_defaults_allowed = True
        for token in tokentrees:
            if (len(token) == 1) and isinstance(token[0], VarName):
                if not non_defaults_allowed:
                    raise CompilerException("No non default parameters allowed after default parameters.")
                self.__func_parameters.append(token[0].get_name())
            elif (len(token) == 3) and isinstance(token[0], VarName) and isinstance(token[1], OperatorAssign) and isinstance(token[2], NumberLiteral):
                non_defaults_allowed = False
                self.__func_parameters.append(token[0].get_name())
                self.__defaults.append(token[2].get_value())
            elif (len(token) == 4) and isinstance(token[0], VarName) and isinstance(token[1], OperatorAssign) and isinstance(token[2], (OperatorAdd, OperatorSub)) and isinstance(token[3], NumberLiteral):  # since no expressions allowed and negative literals don't exist
                non_defaults_allowed = False
                self.__func_parameters.append(token[0].get_name())
                self.__defaults.append(token[3].get_value() * (-1 if isinstance(token[2], OperatorSub) else 1))
            else:
                raise CompilerException(f"Parameters of proc syntax must be variable names with optional default values not {' '.join([t.get_rawstring() for t in token])}.")
        self._token_family = _token_tree[:2]

    def __str__(self):
        return "procedure{" + ",".join(self.__func_parameters) + "}\n"

    def get_funcparameters(self):
        return self.__func_parameters

    def get_defaults(self):
        return self.__defaults

    def get_name(self):
        return self._token_family[1].get_name()


class MainSyntax(Syntax):
    _inducedby = [MainToken]

    def __init__(self, _token_tree):
        super().__init__(_token_tree)
        if not isinstance(_token_tree[0], MainToken):
            raise CompilerException(
                "main-syntax must start with an main-token.")
        self._token_family = _token_tree[:1]

    def __str__(self):
        return "main\n"


class CommentSyntax(Syntax):
    _inducedby = [CommentToken]

    def __init__(self, _token_tree):
        super().__init__(_token_tree)
        if not isinstance(_token_tree[0], CommentToken):
            raise CompilerException(
                "comment-syntax must start with an comment-token.")
        self._token_family = _token_tree[:1]

    def get_comment(self):
        return self._token_family[0].get_comment()

    def __str__(self):
        return f"comment {self._token_family[0].get_comment()}\n"


class AsmSyntax(Syntax):
    _inducedby = [AsmToken]

    def __init__(self, _token_tree):
        super().__init__(_token_tree)
        if not isinstance(_token_tree[0], AsmToken):
            raise CompilerException("asm-syntax must start with an func-token.")
        tokentrees = []
        start_index = 0
        index = 0
        subtoken_tree = _token_tree[1:]
        while index < len(subtoken_tree):
            if isinstance(subtoken_tree[index], Comma):
                tokentrees.append(subtoken_tree[start_index:index])
                start_index = index+1
                index = start_index
            else:
                index += 1
        if len(subtoken_tree[start_index:]) > 0:
            tokentrees.append(subtoken_tree[start_index:])
        self.__clobbers = []
        self.__associations = []
        for token in tokentrees:
            # second part must be diffrent when using default arguments
            if (len(token) == 3) and isinstance(token[0], Register) and isinstance(token[1],  OperatorAssign) and isinstance(token[2], VarName):
                # associated variable
                self.__associations.append((token[2].get_name(), token[0].get_register()))
            elif (len(token) == 1) and isinstance(token[0], Register):
                # clobbered register
                self.__clobbers.append(token[0].get_register())
            else:
                raise CompilerException(f"Parameters of asm syntax must be register names or variable assignments to register names not {' '.join([t.get_rawstring() for t in token])}.")
        if len(self.__clobbers) != len(set(self.__clobbers)):
            raise CompilerException("Non-unique reserved registers.")

        a_names = list(map(lambda a: a[0], self.__associations))
        a_regs = list(map(lambda a: a[1], self.__associations))
        if len(a_names) != len(set(a_names)):
            raise CompilerException("Non-unique associated register names.")
        if len(a_regs) != len(set(a_regs)):
            raise CompilerException("Non-unique associated registers.")
        if len(set(a_regs).intersection(set(self.__clobbers)))>0:
            raise CompilerException("Reserved registers and associated registers overlap.")
        
        self._token_family = _token_tree[:]

    def __str__(self):
        return "asm{clobbers: " + ",".join(map(str, self.__clobbers)) + " associations: " + ",".join(map(str, self.__associations)) + "}\n"

    def get_clobbers(self):
        return self.__clobbers
    
    def get_associations(self):
        return self.__associations

    def get_name(self):
        return self._token_family[1].get_name()


class InlineAsmSyntax(Syntax):
    _inducedby = [InlineAsmToken]
    def __init__(self, _token_tree):
        super().__init__(_token_tree)
        if not isinstance(_token_tree[0], InlineAsmToken):
            raise CompilerException("inline asm-syntax must start with an inline asm-token.")
        self._token_family = _token_tree[:1]

    def get_asm(self):
        return self._token_family[0].get_asm()

    def __str__(self):
        return f"inline asm {self._token_family[0].get_asm()}\n"


all_syntaxes = [
    Expression, IfSyntax, ElifSyntax, ElseSyntax, WhileSyntax, ForSyntax, 
    EndSyntax, VariableDeclarationSyntax, ConstantDeclarationSyntax, BreakSyntax, 
    ContinueSyntax, FuncSyntax, ProcSyntax, MainSyntax, ReturnSyntax, CommentSyntax, 
    AsmSyntax, DeviceDeclarationSyntax, BatchDeviceDeclarationSyntax, InlineAsmSyntax,
    ]  # only syntaxes for syntactic analysis, which don't have to be subsyntaxes (like e.g. Parameters)
