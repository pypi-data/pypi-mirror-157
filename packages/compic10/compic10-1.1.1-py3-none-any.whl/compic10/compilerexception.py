ProgramDatabase = None

class CompilerException(BaseException):
    def __init__(self, error_string="Unspecified Error.", line=None):
        super().__init__(self)
        self.__errorstring =  error_string
        if not line:
            line = ProgramDatabase.line
        self.__line = line

    def __str__(self):
        return f"Compilation error on line {(self.__line + 1) if self.__line is not None else 'undefined'}: {self.__errorstring}"

class UnexpectedException(BaseException):
    def __init__(self, error_string="Unexpected Error.", line=None):
        super().__init__(self)
        self.__errorstring = error_string
        if not line:
            line = ProgramDatabase.line
        self.__line = line

    def __str__(self):
        return f"Unexpected compiler error on line {(self.__line + 1) if self.__line is not None else 'undefined'} This is a bug."
