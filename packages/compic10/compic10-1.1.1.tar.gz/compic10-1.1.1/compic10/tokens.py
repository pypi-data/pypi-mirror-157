import re

from .compilerexception import CompilerException
from .programdatabase import ProgramDatabase

# will match all Token subclasses and find longest matches (maximal munch)
# due too maximal munch lookaheads and behinds unnecessary in all regex expressions
# longest tokens must be unique can't be several things with the same length at the same time


def match_tokens(_line):
    found_tokens = []
    for token_type in all_tokens:
        for match in token_type.match_token(_line):
            found_tokens.append((token_type, match))
    return found_tokens 

def clean_sort_matches(_matches):
    weak_entrys = set()  # using set to get only unique matches
    for i, match in enumerate(_matches):
        for j, comp_match in enumerate(_matches):
            if match is comp_match: continue
            if  (match[1].start() <= comp_match[1].start() < match[1].end()) \
                    or (match[1].start() < comp_match[1].end() <= match[1].end()):  # caution half open interval!
                weak_entrys.add(j if (match[1].end()-match[1].start()) > (comp_match[1].end()-comp_match[1].start()) else i)  # mark (length wise) smaller entry for deletion
    # print([_matches[i] for i in weak_entrys])
    tmp = [_matches[idx] for idx in (set(range(len(_matches))) - weak_entrys)]
    return list(sorted(tmp, key=lambda ele: ele[1].start()))

def check_space_inbetween(_string, _tokens):
    whitespace = [' ', '\t']
    unassigned_parts = set(range(len(_string)))
    for token in _tokens:
        unassigned_parts-=set(range(*token.get_bounds()))
    for i in unassigned_parts:
        if _string[i] not in whitespace:
            raise CompilerException(f"Unexpected character '{_string[i]}'.")  # find line and letter somehow

def resolve_tokens(_string):
    if not re.match(r"^\s*\@", _string):  # not for inline asm
        _string = re.sub(r"(?<!^)\s*#.*", "", _string)  # remove comments but not comment tokens (needed for inline asm with --annotate)
    matches = match_tokens(_string)
    matches = clean_sort_matches(matches)
    token_tree = []
    for match in matches:
        # generate "branch" of token tree (maybe originating from lower branch)
        token_tree.append(match[0](match[1][0], match[1].span()))
        # check if space between tokens is only spaces (raise NonTokenError)
    check_space_inbetween(_string, token_tree)
    return token_tree


class Token:
    # abstract class
    _r = ""

    def __init__(self, _string, _bounds):  # string of supposed token
        self._subtokens = []
        self.__rawstring = _string
        self._bounds = _bounds
        self.__parent_syntax = None

    def __str__(self):
        return type(self).__name__ + "{" + self.__rawstring + "}"

    @classmethod
    def match_token(Cls, _line):  
        # matches regex of token with _line (Lexer)
        # returns beginning and end of token
        # longest token will be accepted (max. munsh)
        # will only do lexiographic analysis
        if Cls is Token:
            raise NotImplementedError
        return re.finditer(Cls._r, _line)

    def get_subtokens(self):
        return self._subtokens[:]

    def get_rawstring(self):
        return self.__rawstring

    def validate(self) -> bool:
        # validates token syntax and check e.g. if correct subtokens like Braces subtokens are of Syntax.Expression
        raise NotImplementedError

    def generate_code(self) -> list:
        # returns list of strings with asm-code
        raise NotImplementedError

    # def get_namespace(self) -> list:
    #     # returns list of variable names
    #     return self.__namespace[:]

    # def get_nonlocals(self) -> list:
    #     # returns list of variable names used withing the token from outside
    #     return self.__used_nonlocals[:]
    
    @classmethod
    def get_regex(Cls):
        return Cls._r[:]
    

    def get_bounds(self):
        return self._bounds[:]
    
    def set_parent_syntax(self, _syntax):
        self.__parent_syntax = _syntax

    def get_parent_syntax(self):
        return self.__parent_syntax
    
# comma seperator
class Comma(Token):
    _r = r","


# operands
class Operand(Token):
    pass


class BracedToken(Token):
    class match_wrapper:  # custom for function
        @staticmethod
        def find_closing_parentheses(_string, _startindex, *, n0=1):
            for i, l in enumerate(_string[_startindex:]):
                if l == '(':
                    n0 += 1
                elif l == ')':
                    n0 -= 1
                if n0 <= 0:
                    return i+_startindex
            else:
                return None

        def __init__(self, match, *, inner_index = 1):
            self._match = match
            self.__inner_index = inner_index
            self._end = self.find_closing_parentheses(
                match.string, match.end()) + 1
            if not self._end:
                raise CompilerException("No closing parentheses.")

        def end(self, *params):
            return self._end

        def span(self, *params):
            return (self._match.start(), self._end)

        def __getattr__(self, name):
            return getattr(self._match, name)

        def __getitem__(self, idx):
            if idx == 0:
                return self._match.string[self._match.start(): self._end]
            elif idx == self.__inner_index:
                return self._match.string[self._match.end(): self._end-1]
            else:
                return self._match[idx]

    @classmethod
    def match_token(Cls, _line):
        cust_m = re.finditer(Cls._r, _line)
        # methods needed .end() .start() .span() match[0]=funcname match[1] = stuff between parentheses
        try:
            m = next(cust_m)
            while True:
                # calling match_wrapper directly would raise an exception for false matches
                endindex = Cls.match_wrapper.find_closing_parentheses(
                    _line, m.end())
                if not endindex:
                    m = next(cust_m)
                    continue
                yield Cls.match_wrapper(m)
                m = next(cust_m)
        except StopIteration:
            return


class Braces(Operand, BracedToken):
    _r = r"\("

    def __init__(self, _string, _bounds):
        super().__init__(_string, _bounds)
        match = BracedToken.match_wrapper(re.match(self._r, _string))
        self._subtokens = resolve_tokens(match[1])

    @classmethod
    def match_token(Cls, _line):
        cust_m = re.finditer(Cls._r, _line)
        # methods needed .end() .start() .span() match[0]=funcname match[1] = stuff between parentheses
        try:
            m = next(cust_m)
            while True:
                # calling match_wrapper directly would raise an exception for false matches
                endindex = BracedToken.match_wrapper.find_closing_parentheses(_line, m.end())
                if not endindex:
                    m = next(cust_m)
                    continue
                yield BracedToken.match_wrapper(m)
                m = next(cust_m)
        except StopIteration:
            return

class VarName(Operand):
    _r = r"[a-zA-Z_]\w*"

    def __init__(self, _string, _bounds):
        super().__init__(_string, _bounds)
        self.__name = re.match(self._r, _string)[0]
        if self.__name in keywords:
            raise CompilerException("Variablenames can't be keywords.")

    def get_name(self):
        return self.__name

    def __str__(self):
        return "var{" + self.__name + "}"

    @classmethod
    def match_token(Cls, _line):
        it = re.finditer(Cls._r, _line)
        try:
            m = next(it)
            while True:
                if m[0] not in keywords:
                    yield m
                    m=next(it)
                else:
                    m=next(it)
        except StopIteration:
            return


class FunctionCall(Operand, BracedToken):  # I_love_ducktyping.exe
    _r = r'('+VarName.get_regex()+r')' + r"\s*\("  # using Braces.get_regex() not possible due too empty braces () 

    # define name( as startlabel and find the belonging )
        
    def __init__(self, _string, _bounds):
        super().__init__(_string, _bounds)
        match = BracedToken.match_wrapper(re.match(self._r, _string), inner_index=2)
        self.__name = match[1]
        if self.__name  in keywords:
            raise CompilerException("Functionnames can't be keywords.")
        self._subtokens = resolve_tokens(match[2])

    def get_name(self):
        return self.__name

    def __str__(self):
        return "call{" + self.__name + "}"
    
    @classmethod
    def match_token(Cls, _line):
        cust_m = re.finditer(Cls._r, _line)
        # methods needed .end() .start() .span() match[0]=funcname match[1] = stuff between parentheses
        try:
            m = next(cust_m)
            while True:
                endindex = BracedToken.match_wrapper.find_closing_parentheses(_line, m.end())  # calling match_wrapper directly would raise an exception for false matches
                if not endindex or m[1] in keywords:
                    m = next(cust_m)
                    continue
                yield BracedToken.match_wrapper(m)
                m = next(cust_m)
        except StopIteration:
            return


# number literals part of operands
class NumberLiteral(Operand):
    def __init__(self, _string, _bounds):
        super().__init__(_string, _bounds)
        self._value = 0

    def get_value(self):
        return self._value


class IntegerNumber(NumberLiteral):
    _r = r"(?:\d+)"

    def __init__(self, _string, _bounds):
        super().__init__(_string, _bounds)
        self._value = int(re.match(self._r, _string)[0])


class BoolNumber(NumberLiteral):
    _r = r"(?:false)|(?:true)"

    def __init__(self, _string, _bounds):
        super().__init__(_string, _bounds)
        self._value = 1 if re.match(self._r, _string)[0] == "true" else 0

class FloatNumber(NumberLiteral):
    _r = r"(?<![a-zA-Z_])(?:\d+\.\d*(?![a-zA-Z_]))|(?:\d*\.\d+)"  # lookbehind since otherwise problem with 0.Setting

    def __init__(self, _string, _bounds):
        super().__init__(_string, _bounds)
        self._value = float(re.match(self._r, _string)[0])  # asm uses the same number syntax


class ENumber(NumberLiteral):
    _r = r'('+FloatNumber.get_regex()+ '|' + IntegerNumber.get_regex() + r')' + r"[eE]" + '([-+]?' + IntegerNumber.get_regex() + ')'

    def __init__(self, _string, _bounds):
        super().__init__(_string, _bounds)
        self._value = float(re.match(self._r, _string)[1]) * 10**int(re.match(self._r, _string)[2])


class BinNumber(NumberLiteral):
    _r = r"0b([01]+)"

    def __init__(self, _string, _bounds):
        super().__init__(_string, _bounds)
        self._value = int(re.match(self._r, _string)[1], 2)


class HexNumber(NumberLiteral):
    _r = r"0x([0-9a-fA-F]+)"

    def __init__(self, _string, _bounds):
        super().__init__(_string, _bounds)
        self._value = int(re.match(self._r, _string)[1], 16)
        if (self._value & 0x80000000) == 0x80000000:
            self._value = -((self._value ^ 0xffffffff) + 1)



# operations
class Operation(Token):
    pass


class UnaryOperation(Operation):
    pass


class BinaryOperation(Operation):
    pass

# tertiary operation is not operation in this sense and needs an seperate syntax


class OperatorAdd(UnaryOperation, BinaryOperation):
    _r = r"\+"


class OperatorSub(UnaryOperation, BinaryOperation):
    _r = r"\-"


class OperatorMul(BinaryOperation):
    _r = r"\*"


class OperatorMod(BinaryOperation):
    _r = r"\%"


class OperatorDiv(BinaryOperation):
    _r = r"\/"


class OperatorOr(BinaryOperation):
    _r = r"\|\|"


class OperatorAnd(BinaryOperation):
    _r = r"\&\&"


class OperatorNot(UnaryOperation):
    _r = r"\!"


class OperatorBitwiseXor(BinaryOperation):
    _r = r"\^"


class OperatorBitwiseAnd(BinaryOperation):
    _r = r"\&"


class OperatorBitwiseOr(BinaryOperation):
    _r = r"\|"


class OperatorNeg(UnaryOperation):
    _r = r"\~"


class OperatorInc(UnaryOperation):
    _r = r"\+\+"
    # for now only ++v not v++
    # for latter distinction UnaryLeft UnaryRight


class OperatorDec(UnaryOperation):
    _r = r"\-\-"
    # for now only --v not v--
    # for latter distinction UnaryLeft UnaryRight


class OperatorShl(BinaryOperation):
    _r = r"\<\<"


class OperatorShr(BinaryOperation):
    _r = r"\>\>"


class OperatorEq(BinaryOperation):
    _r = r"\=\="


class OperatorLt(BinaryOperation):
    _r = r"\<"


class OperatorGt(BinaryOperation):
    _r = r"\>"


class OperatorLte(BinaryOperation):
    _r = r"\<\="


class OperatorGte(BinaryOperation):
    _r = r"\>\="


class OperatorNeq(BinaryOperation):
    _r = r"\!\="


class OperatorAssign(BinaryOperation):
    _r = r"\="


class OperatorAddAssign(BinaryOperation):
    _r = r"\+\="


class OperatorSubAssign(BinaryOperation):
    _r = r"\-\="


class OperatorMulAssign(BinaryOperation):
    _r = r"\*\="


class OperatorDivAssign(BinaryOperation):
    _r = r"\/\="


class OperatorModAssign(BinaryOperation):
    _r = r"\%\="

class OperatorDot(BinaryOperation):
    _r = r"\."

class OperatorAndAssign(BinaryOperation):
    _r = r"\&\&\="

class OperatorOrAssign(BinaryOperation):
    _r = r"\|\|\="

# shlassign, shrassign, bitwise everything assign

# alternatives
class IfToken(BracedToken):
    _r = r"if\s*\("

    def __init__(self, _string, _bounds):
        super().__init__(_string, _bounds)
        match = BracedToken.match_wrapper(re.match(self._r, _string))
        self._subtokens = resolve_tokens(match[1])


class ElifToken(BracedToken):
    _r = r"elif\s*\("

    def __init__(self, _string, _bounds):
        super().__init__(_string, _bounds)
        match = BracedToken.match_wrapper(re.match(self._r, _string))
        self._subtokens = resolve_tokens(match[1])


class ElseToken(Token):
    _r = r"else"


class EndToken(Token):
    _r = r"end"


class ForToken(BracedToken):
    _r = r"for\s*\("

    def __init__(self, _string, _bounds):
        super().__init__(_string, _bounds)
        match = BracedToken.match_wrapper(re.match(self._r, _string))
        self._subtokens = resolve_tokens(match[1])


class WhileToken(BracedToken):
    _r = r"while\s*\("

    def __init__(self, _string, _bounds):
        super().__init__(_string, _bounds)
        match = BracedToken.match_wrapper(re.match(self._r, _string))
        self._subtokens = resolve_tokens(match[1])


class ContinueToken(Token):
    _r = r"continue"


class BreakToken(Token):
    _r = r"break"


class ConstToken(Token):
    _r = r"const"


class DevToken(Token):
    _r = r"dev"


class BDevToken(Token):
    _r = r"bdev"

class VarToken(Token):
    _r = r"var"


class FuncToken(Token):
    _r = r"func"


class ProcToken(Token):
    _r = r"proc"


class MainToken(Token):
    _r = r"main"


class ReturnToken(Token):
    _r = r"return"


class CommentToken(Token):
    _r = r"#(.*)"

    def __init__(self, _string, _bounds):
        super().__init__(_string, _bounds)
        m = re.match(self._r, _string)
        self._comment_text = m[1]
    
    def get_comment(self):
        return self._comment_text


class AsmToken(Token):
    _r = r"asm"


class BracketedToken(Token):
    class match_wrapper:  # custom for function
        @staticmethod
        def find_closing_parentheses(_string, _startindex, *, n0=1):
            for i, l in enumerate(_string[_startindex:]):
                if l == '[':
                    n0 += 1
                elif l == ']':
                    n0 -= 1
                if n0 <= 0:
                    return i+_startindex
            else:
                return None

        def __init__(self, match, *, inner_index=1):
            self._match = match
            self.__inner_index = inner_index
            self._end = self.find_closing_parentheses(
                match.string, match.end()) + 1
            if not self._end:
                raise CompilerException("No closing brackets.")

        def end(self, *params):
            return self._end

        def span(self, *params):
            return (self._match.start(), self._end)

        def __getattr__(self, name):
            return getattr(self._match, name)

        def __getitem__(self, idx):
            if idx == 0:
                return self._match.string[self._match.start(): self._end]
            elif idx == self.__inner_index:
                return self._match.string[self._match.end(): self._end-1]
            else:
                return self._match[idx]


class Indexing(Operand, BracketedToken):  # I_love_ducktyping2.exe
    # using Braces.get_regex() not possible due too empty brackets []
    _r = r'('+VarName.get_regex()+r')' + r"\s*\["

    # define name( as startlabel and find the belonging )

    def __init__(self, _string, _bounds):
        super().__init__(_string, _bounds)
        match = BracketedToken.match_wrapper(
            re.match(self._r, _string), inner_index=2)
        self.__name = match[1]
        if self.__name in keywords:
            raise CompilerException("Indexable names can't be keywords.")
        self._subtokens = resolve_tokens(match[2])

    def get_name(self):
        return self.__name

    def __str__(self):
        return "indexing{" + self.__name + "}"

    @classmethod
    def match_token(Cls, _line):
        cust_m = re.finditer(Cls._r, _line)
        # methods needed .end() .start() .span() match[0]=funcname match[1] = stuff between parentheses
        try:
            m = next(cust_m)
            while True:
                # calling match_wrapper directly would raise an exception for false matches
                endindex = BracketedToken.match_wrapper.find_closing_parentheses(
                    _line, m.end())
                if not endindex or m[1] in keywords:
                    m = next(cust_m)
                    continue
                yield BracketedToken.match_wrapper(m)
                m = next(cust_m)
        except StopIteration:
            return


class Register(Token):
    _r = r"\$r([0-9a]{1,2})"

    def get_register(self):
        return self._register

    def __init__(self, _string, _bounds):
        super().__init__(_string, _bounds)
        self._register = int(re.match(self._r, _string)[1])


class InlineAsmToken(Token):
    _r = r"@(.*)"  # catches whole line like comment

    def __init__(self, _string, _bounds):
        super().__init__(_string, _bounds)
        m = re.match(self._r, _string)
        self._asm = m[1]

    def get_asm(self):
        return self._asm


# only working tokens
all_tokens =    [
                Comma, Braces, VarName, FunctionCall, 
                IntegerNumber, FloatNumber, ENumber, BinNumber, HexNumber, BoolNumber,
                OperatorAdd, OperatorAnd, OperatorBitwiseAnd, OperatorBitwiseOr, OperatorBitwiseXor, OperatorDec, 
                OperatorDiv, OperatorEq, OperatorGt, OperatorGte, OperatorInc,
                OperatorLt, OperatorLte, OperatorMod, OperatorMul, OperatorNeg, OperatorNot, OperatorOr, OperatorShl, 
                OperatorShr, OperatorSub, OperatorNeq, OperatorAddAssign, OperatorSubAssign, OperatorDivAssign, OperatorMulAssign, OperatorModAssign,
                OperatorAssign, OperatorAndAssign, OperatorOrAssign,
                IfToken, ElifToken, ElseToken,
                ForToken, WhileToken, ContinueToken, BreakToken, EndToken,
                ConstToken, VarToken, FuncToken, ProcToken, ReturnToken, MainToken, CommentToken, AsmToken, OperatorDot, Indexing,
                DevToken, BDevToken, Register, InlineAsmToken,
                ]


keywords = [
    "for", "while", "if", "elif", "else",  "end", "continue", "break", "const", "var", "func", "proc", "true", "false", "return", "main", "asm", "dev", "bdev",
]
