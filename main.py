from lark import Lark
from lark.tree import Tree as ParseTree
from lark.lexer import Token
from typing import Union,DefaultDict

# use default dict
from collections import defaultdict
Env = DefaultDict[str, int]
env : Env = defaultdict(lambda: 0)


lark_grammar = ""

with open("syntax.lark", "r") as f:
    lark_grammar = f.read()

parser = Lark(lark_grammar, start='com', parser='lalr')

# print (parser.parse("""
# 関数 main() {
#     出力("Hello World!")
# }
# """).pretty())



# print (parser.parse(program).pretty())

def calculate_aexp(aexp : Union[ParseTree,Token]) -> int:

    if isinstance(aexp, Token):
        if aexp.type == "NUM":
            return int(aexp.value)
        elif aexp.type == "VAR":
            ID = aexp.value
            return env[ID]
        raise Exception("Unknown token type")

    data = aexp.data
    
    if data == "add":
        return calculate_aexp(aexp.children[0]) + calculate_aexp(aexp.children[1])
    elif data == "sub":
        return calculate_aexp(aexp.children[0]) - calculate_aexp(aexp.children[1])
    elif data == "mul":
        return calculate_aexp(aexp.children[0]) * calculate_aexp(aexp.children[1])
    elif data == "aexp":
        return calculate_aexp(aexp.children[0])
    elif data == "term":
        return calculate_aexp(aexp.children[0])
    elif data == "factor":
        return calculate_aexp(aexp.children[0])

def calculate_bexp(bexp : Union[ParseTree,Token]) -> bool:
    
    
    if isinstance(bexp, Token):
        if bexp.type == "TRUE":
            return True
        elif bexp.type == "FALSE":
            return False
        raise Exception("Unknown token type")
    
    data = bexp.data
    
    if data == "bexp":
        return calculate_bexp(bexp.children[0])
    elif data == "band":
        return calculate_bexp(bexp.children[0])
    elif data == "bor":
        return calculate_bexp(bexp.children[0])
    elif data == "bnot":
        return calculate_bexp(bexp.children[0])
    elif data == "batom":
        return calculate_bexp(bexp.children[0])
    elif data=="or":
        return calculate_bexp(bexp.children[0]) or calculate_bexp(bexp.children[1])
    elif data == "and":
        return calculate_bexp(bexp.children[0]) and calculate_bexp(bexp.children[1])
    elif data == "not":
        return not calculate_bexp(bexp.children[0])
    elif data == "eq":
        return calculate_aexp(bexp.children[0]) == calculate_aexp(bexp.children[1])
    elif data == "lt":
        return calculate_aexp(bexp.children[0]) < calculate_aexp(bexp.children[1])
    
    raise Exception("Unknown bexp type")
    
def calculate_command(command : Union[ParseTree,Token]) -> None:
    
    if isinstance(command, Token):
        if command.type == "SKIP":
            return None
        raise Exception("Unknown token type")
    
    data = command.data
    
    if data == "com":
        calculate_command(command.children[0])
        return
    elif data == "seq":
        calculate_command(command.children[0])
        calculate_command(command.children[1])
        return None
    elif data=="assign":
        assert isinstance(command.children[0], Token)
        ID = command.children[0].value
        env[ID] = calculate_aexp(command.children[1])
        return None
    elif data == "ifelse":
        is_satisfied = calculate_bexp(command.children[0])
        if is_satisfied:
            return calculate_command(command.children[1])
        else:
            return calculate_command(command.children[2])
    elif data == "while":
        is_satisfied = calculate_bexp(command.children[0])
        
        while is_satisfied:
            calculate_command(command.children[1])
            is_satisfied = calculate_bexp(command.children[0])
        
        return None
    
    elif data == "print":
        res = calculate_aexp(command.children[0])
        print (res)
        return None

    raise Exception("Unknown command type")
    
    
program = ""

with open("program.txt", "r") as f:
    program = f.read()



tree = parser.parse(program,start="com")
# print (tree)
# print (tree.data)
# for child in tree.children:
#     print (child)
#     print (child.data)
    
print (calculate_command(tree))

print (tree.pretty())

# print default dict
print (dict(env))