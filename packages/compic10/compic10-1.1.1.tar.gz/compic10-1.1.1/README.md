# compIC10
compIC10 is a compiler for the "IC10" from the game Stationeers. It supports common programming language features like
loops, if-statements, functions, procedures (functions without return value), variables and expressions.

## How to install
Just install Python3 version 3.8.2 or later (earlier versions probably work too) and the compic10 pip package with `python3 -m pip install compic10`.

## Programming Language
### Basics
All statements must be on a single line, blank lines are allowed.
Every line can only contain one statement which means that every statement ends with a linebreak.
When referring to names meant are strings starting with a \'\_\' or letter followed by zero or more \'\_\', letters or numbers.
Names can not be keywords.
There are no types since every operation in stationeers results in a floating point number.
Everything is case sensitive. Multiple spaces or tabs are beeing ignored by the compiler meaning indentation is possible but not enforced.

After successful compilation the compiler conducts post process optimizations to remove redundant and garbage code from crude compiler output.

### Compilation Errors
If there is an error in the source code, the compiler will notice you and tell you at which line the error is.
If the compiler yields some python-exception than there may be a bug in compic10 or in the source code.
Bugs within compic10 can be submitted at: gitlab.com/smpkdev/compic10/-/issues
### Post Processor Errors
If you get that error, usage of the --no_post_processing_optimization flag is recommended, to disable post process optimizations. Usually this error should not be appearing.
### Runtime Errors
If the program ends up in a unrecoverable state it sets the state of the IC10 housing to an error code and turns the IC10 off.
Currently there is only the error-state -1 which means an function ended without an `return` statement.
Unfortunately AIMEe doesn't support a state so he will just turn off.
## Compiler
**Basic usage:**

    python3 -m compic10 [source_file]
Compiles the source code in file source_file. This doesn't save the result anywhere. 
Use the following parameters in order to get the result (version without further parameters still useful to check for errors).

**Parameters:**

    -o [file], --out_file [file]
Safes generated code in [file].

    -p, --print_output
Prints code to the stdout.

    -c, --copy
Copys resulting code to clipboard.

    -a, --annotate
Creates comments in the generated code in order to easily associate source-code with asm-code.

    -s, --offset_varstack [offset]
Sets the location reserved for variables in the stack.

    -l, --length_varstack [length]
Sets the length of the reserved section in stack for variables. 
offset+length must be less then 512.

    --silent
Suppress any console output except code output from the -p flag.

    --no_post_processing_optimization
Disable post processor optimizations.
PPO might be buggy, if the code does not work properly, try to use this flag to completely disable the PPO.

    

## Statements
### Comments
Comments start with a `#`. Everything after this symbol on the current line will be ignored by the compiler.
The following code is a comment with comment message [comment]:

    # [comment]
Comments on a seperate line will be placed in the resulting asm-code if the `--annotate` flag is set.
### main
Every program starts within the main block given by:

    main
    [main code]
    end
`[main code]` is the source code of main.
### Number literals
Integer numbers:

    1

Floating point numbers:

    1.1
Shortcuts like .1 or 1. are possible.
Exponential number literals:

    1.1e5
    1.1E5
    1.1e-5
    1.1E-5
    1.1e+5
    1.1E+5

Since Stationeers doesn't support scientfic notation, floating point numbers are limited to at most 16 digits behind the comma.
Binary numbers:

    0b0101
Hexadecimal numbers:

    0xFF
Booleans:

    true
    false
True is represented as an 1 and false as an 0.
Note that all number literals are positive a additional minus (-) before that is will result in an expression of unary - and the number literal.
### Variables
The following code generates a variable with name `[name]` and (1) initial value 0 or (2) initial value beeing the 
result of the expression `[expression]`:

    var [name]  # (1)
    var [name] = [expression]  # (2)
Variables can be used in the current block (namespace) and inner blocks.
Global variables are possible too. Those unfortunately require a bigger overhead (those can not be within registers).
### Constants
The following code generates a constant with name `[name]` and value `[value]`.

    const [name] = [value]
Like variables, constants will be available in the current block and all inner blocks.
The value must be known at compile time (no expressions allowed only number literals) an optional +/- before the number is allowed.
### Devices 
The following code assignes device number `[dev]` on the IC10 to the name `[name]`:

    dev [name] = [dev]
The 'd' like in `d0` must be omitted here.
Values of device `[name]` propertys `[property]` can be modified and written to by:

    [name].[property]
This statement can be used like a variable.
If the device has slots, a certain slot `[slot]` can be accessed by:

    [name][ [slot] ].[property]

In order to access reagents use:

    [name].[reagentmode].[property]
`[reagentmode]` has to be one of: `Contents`, `Required`, `Recipe`.

The special device `db` can always be accessed through the keyword `self`.
`[name]` can also be a variable or constant for dynamic device access.
`[name]` in an expression refers to the pin on the housing set by the device declaration.
The special device property `DeviceIsSet` can be used to check if the port is configured on socket.
### Batch Devices 
The following code associates all devices on the network with itemhash `[hash]` with the name `[name]`:

    bdev [name] = [hash]
Itemhashes can be found here: https://stationeers-wiki.com/ItemHash
The value of batch device `[name]` property `[property]` can be read by:

    [name].[property].[batchmode]
`[batchmode]` is the function used to combine all the values and must be one of: `Average`, `Sum`, `Minimum`, `Maximum`.
The property `[property]` of all devices on the network, associated with `[name]`, can be assigned with the result of an expression `[expression]` by:

    [name].[property] = [expression]

`[name]` in an expression refering to the hash set by the batch device declaration.
### Functions 
A function with name `[name]` is defined by the following code:

    func [name]([parameters...])
    [function body]
    end
`[function body]` is the source code of the function.
The functions has parameters `[parameters...]`, which is a comma seperated collection of names. Default values are supported and added with `param=1`, `param=-1` or `param=+1` 
after an parameter with a default value, no parameters without a default value are allowed. All default values must be known at compile time.
All functions must end with a `return` statement that has a return value.
At the end of the function body is a `end` statement.
Functions have their own namespace.
If a function ends without an return statement, the state of the IC10-housing changes to -1 followed by it shuting down.
Recursion is supported.
### Procedures
A procedure with name `[name]` is defined by the following code:

    proc [name]([parameters...])
    [procedure body]
    end
`[procedure body]` is the source code of the procedure.
The procedure has parameters `[parameters...]`, which is a comma seperated collection of names. Default values are supported like `param=1`, `param=-1` or `param=+1`
after an parameter with default value, no parameters without a default value are allowed. All default values must be known at compile time.
At the end of the procedure body is an `end`.
Procedures don't have to end with an `return` statement.
Procedures have their own namespace.
Recursion is supported.
### return
Functions can be returned from everywhere with a return statement by:

    return [expression]
The return value is the result of expression `[expression]`.
Same goes for procedures but without a return value:

    return
`return` is only allowed within functions or procedures.
### Expressions
Expression are mathematical statements where operators are connected with variables, number literals, devices, batch devices, 
subexpressions within braces () or functions.
Expressions are always evaluated from left to right for operators with equal priorities. 
An exception to that are assignment operations. Those are evaluated from right to left when grouped like `a=b=c`.
Supported operators from higher to lower priority (grouped ones have equal priority):

    -- [operand]  # decrement: [operand] = [operand] - 1
    ++ [operand]  # increment: [operand] = [operand] + 1

    + [operand]  # * 1 (do nothing)
    - [operand]  # * -1

    # Currently not implemented but recognized:
    ~ [operand]  # bitwise negate
    
    [operand1] * [operand2]  # multiply
    [operand1] / [operand2]  # divide
    [operand1] % [operand2]  # modulus

    [operand1] + [operand2]  # add
    [operand1] - [operand2]  # subtract
    
    # Currently not implemented but recognized:
    [operand1] << [operand2]  # shift left
    # Currently not implemented but recognized:
    [operand1] >> [operand2]  # shift right
    
    # Currently not implemented but recognized:
    [operand1] & [operand2]  # bitwise and 
    
    # Currently not implemented but recognized:
    [operand1] ^ [operand2]  # bitwise xor
    
    # Currently not implemented but recognized:
    [operand1] | [operand2]  # bitwise or

    [operand1] == [operand2]  # equal
    [operand1] != [operand2]  # not equal
    [operand1] < [operand2]  # less
    [operand1] <= [operand2]  # less equal
    [operand1] > [operand2]  # greater
    [operand1] >= [operand2]  # greater equal

    ! [operand]     # logical not
    
    [operand1] && [operand2]  # logical and
    
    [operand1] || [operand2]  # logical or
    
    [operand1] = [operand2]  # assignment
    [operand1] += [operand2]  # assign and add:  [operand1] = [operand1] + [operand2]
    [operand1] -= [operand2]  # assign and subtract:  [operand1] = [operand1] - [operand2]
    [operand1] *= [operand2]  # assign and multiply:  [operand1] = [operand1] * [operand2]
    [operand1] /= [operand2]  # assign and divide:  [operand1] = [operand1] / [operand2]
    [operand1] %= [operand2]  # assign and calculate modulus:  [operand1] = [operand1] % [operand2]
    [operand1] &&= [operand2]  # assign and and:  [operand1] = [operand1] && [operand2]
    [operand1] ||= [operand2]  # assign and or:  [operand1] = [operand1] || [operand2]
### if, elif, else
If statements can be implemented by:

    if([expression])
    [if body]
    elif([expression])
    [elif body]
    else
    [else body]
    end
The first body with an true (nonzero) expression will be executed or, if none is true, the `else` body will be executed.
Every body has its own namespace. Everything except the `if([expression])` and `end` is optional. There can also be more than one elif.
### while
While loops can be implemented by:

    while([expression])
    [while body]
    end
The body will be executed until it is leaved by `break` or the expression `[expression]` is not true anymore.
Every iteration can be cut short with `continue`. This immediately triggers a new loop iteration.
### for
For loops are implemented by:

    for([expression or variable definition], [cond_expression], [iter_expression])
    [for_body]
    end

For loops lopp until expression cond_expression is false or it is stopped by `break`.
Before the loop, an expression is executed or a variable in the embedding scope `[for_body]` is definded by [expression or variable definition].
Every iteration can be cut short with `continue`. This immediately triggers a new loop iteration.
### continue, break

    continue
    break
`break` exits a loop immeditly and `continue` skips the remainder of the current iteration.
Both are only allowed within loops.
### Inline assembler
It is possible to execute IC10-MIPS assembler code [asm code] within the source code through:

    asm [register list and associated variables]
    [asm code]
    end

`[register list and associated variables]` refers to a comma separated list, consisting out of elements representing registers like `$r0`-`$r13` 
and optional associations with variables by `$r0-13=[variable]` where variable refers to the identifier of the variable. All modifications to that register will be saved in the variable.
asm code must start with a `@` like `@move $r0 $r1`.
In asm code registers can be used like usual. However they shouldn't be since that may break the program they should be addressed with `$r0` - `$r13` 
and added to the register list by which only the compiler assigned registers will be used that are also safe to use (references to them in the comments within an inline asm will be replaced with the corresponding compiler-assigned registers as well).
A maximum of 14 registers can be used like that since `sp`, `ra`, `r14` and `r15` are used by the compiler. However, `ra`, `r14` and `r15` are generally save to use within an inline assembler block. Only `sp` must refer to the same value at the end.
The registers will in general not be associated with the corresponding registers in IC10 assembler source code, 
since they could be reserved for variables.
It should not be possible to break a program with inline assembler since all used registers get backed up on the stack before the execution of the inline asm block.
This is not the case for jumps and branching instructions. Use of those should be limited to labels within the inline asm block. The latter will not be enforced.

It is possible but not recommended to use asm code outside of a asm block. Everything after a `@` will be placed in the source code without modification (including comments).
## Examples
### IC10 giving sphere coordinates for a vector

    dev posx=0
    dev posy=1
    dev posz=2
    dev output_dist=3
    dev output_phi=4
    dev output_theta=5

    func atan2(x,y)
        const pi = 3.14159
        if(x>0)
            return atan(y/x)
        elif(y>0)
            return pi/2 - atan(x/y)
        elif(y<0)
            return -pi/2 - atan(x/y)
        elif(x<0)
            return atan(y/x) + pi
        else
            return 0
        end
        # return is needed here unfortunatly
        return 0
    end

    main
        while(true)
            # length of vector
            output_dist.Value = sqrt(posx.Value*posx.Value + posy.Value*posy.Value + posz.Value*posz.Value)
            # Sphere coordinates
            output_phi.Value = atan2(posx.Value, posy.Value)
            output_theta.Value = asin(posz.Value / output_dist.Value)
            yield()
        end
    end


### Fibonacci number generator
    main
        var l=1
        var ll=1
        for(var i=0, i<50, ++i)
            self.Setting = l+ll
            ll=l
            l=self.Setting
            yield()
        end
    end

### Recursive Fibonacci number generator

    func fibonacci(start)
        if(start <= 2)
            return 1
        else
            return fibonacci(start-2)+fibonacci(start-1)
        end
    end

    main
        self.Setting = fibonacci(9)
    end
