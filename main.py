from lark import Lark
from lark.tree import Tree as ParseTree
from lark.lexer import Token
from typing import Union,DefaultDict

# use default dict
from collections import defaultdict
Env = DefaultDict[str, int]
env : Env = defaultdict(lambda: 0)




def run_code (code : str) :
    IMP_grammar = ""

    with open("syntax.lark", "r") as f:
        IMP_grammar = f.read()

    parser = Lark(IMP_grammar, start='com', parser='lalr',propagate_positions=True)
    parse_tree = parser.parse(code)
    # print (parse_tree.pretty())
    res_env = calculate_command(parse_tree,env)
    

    
    
    
    return res_env

def calculate_aexp(aexp : Union[ParseTree,Token],env:Env) -> int:
    
    if isinstance(aexp, Token):
        if aexp.type == "NUM":
            return int(aexp.value)
        elif aexp.type == "VAR":
            ID = str(aexp.value)
            assert isinstance(ID, str)
            return env[ID]
        raise Exception("Unknown token type")

    data = aexp.data
    
    if data == "add":
        return calculate_aexp(aexp.children[0],env) + calculate_aexp(aexp.children[1],env)
    elif data == "sub":
        return calculate_aexp(aexp.children[0],env) - calculate_aexp(aexp.children[1],env)
    elif data == "mul":
        return calculate_aexp(aexp.children[0],env) * calculate_aexp(aexp.children[1],env)
    elif data == "aexp":
        return calculate_aexp(aexp.children[0],env)
    elif data == "term":
        return calculate_aexp(aexp.children[0],env)
    elif data == "factor":
        return calculate_aexp(aexp.children[0],env)

def calculate_bexp(bexp : Union[ParseTree,Token],env:Env) -> bool:
    
    
    if isinstance(bexp, Token):
        if bexp.type == "TRUE":
            return True
        elif bexp.type == "FALSE":
            return False
        raise Exception("Unknown token type")
    
    data = bexp.data
    
    if data == "bexp":
        return calculate_bexp(bexp.children[0],env)
    elif data == "band":
        return calculate_bexp(bexp.children[0],env)
    elif data == "bor":
        return calculate_bexp(bexp.children[0],env)
    elif data == "bnot":
        return calculate_bexp(bexp.children[0],env)
    elif data == "batom":
        return calculate_bexp(bexp.children[0],env)
    elif data=="or":
        return calculate_bexp(bexp.children[0],env) or calculate_bexp(bexp.children[1],env)
    elif data == "and":
        return calculate_bexp(bexp.children[0],env) and calculate_bexp(bexp.children[1],env)
    elif data == "not":
        return not calculate_bexp(bexp.children[0],env)
    elif data == "eq":
        return calculate_aexp(bexp.children[0],env) == calculate_aexp(bexp.children[1],env)
    elif data == "lt":
        return calculate_aexp(bexp.children[0],env) < calculate_aexp(bexp.children[1],env)
    
    raise Exception("Unknown bexp type")
    
def calculate_command(command : Union[ParseTree,Token],env:Env) -> Env:
    
    if isinstance(command, Token):
        if command.type == "SKIP":
            return env
        raise Exception("Unknown token type")
    
    data = command.data
    
    if data == "com":
        return calculate_command(command.children[0],env)
        
    elif data == "seq":
        newenv = calculate_command(command.children[0],env)
        return calculate_command(command.children[1],newenv)
    elif data=="assign":
        assert isinstance(command.children[0], Token)
        ID = command.children[0].value
        env[ID] = calculate_aexp(command.children[1],env)
        return env
    elif data == "ifelse":
        is_satisfied = calculate_bexp(command.children[0],env)
        if is_satisfied:
            return calculate_command(command.children[1],env)
        else:
            return calculate_command(command.children[2],env)
    elif data == "while":
        is_satisfied = calculate_bexp(command.children[0],env)
        
        while is_satisfied:
            env = calculate_command(command.children[1],env)
            is_satisfied = calculate_bexp(command.children[0],env)
        
        return env
    
    elif data == "print":
        res = calculate_aexp(command.children[0],env)
        print("line",command._meta.line,":",res)
        return env

    raise Exception("Unknown command type")
    
    
program = ""

with open("program.txt", "r") as f:
    program = f.read()


run_code(program)

