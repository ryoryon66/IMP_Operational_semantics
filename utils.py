from typing import  Union
from typing_extensions import Literal

from lark import Lark, Token, Transformer
from lark.lexer import Token
from lark.tree import Tree as ParseTree

# recursion limit
import sys

sys.setrecursionlimit(10 ** 9)


class RemoveRedundant(Transformer):
    def aexp(self,children):
        if len(children) == 1:
            return children[0]
        raise Exception("aexp")
    
    def term(self,children):
        if len(children) == 1:
            return children[0]
        raise Exception("term")

    def factor(self,children):
        if len(children) == 1:
            return children[0]
        raise Exception("factor")
    
    def atom(self,children):
        if len(children) == 1:
            return children[0]
        raise Exception("atom")
    
    def bexp(self,children):
        if len(children) == 1:
            return children[0]
        raise Exception("bexp")
    
    def gt(self,children):
        assert len(children) == 2
        
        #  0 > 1 は 1 < 0 と同じ
        return ParseTree("lt",children[::-1])
    
    def ge(self,children):
        assert len(children) == 2
        
        #  0 >= 1 は 1 <= 0 と同じ
        return ParseTree("le",children[::-1])
    
    def band(self,children):
        if len(children) == 1:
            return children[0]
        raise Exception("band")
    
    def bor(self,children):
        if len(children) == 1:
            return children[0]
        raise Exception("bor")

    def bnot(self,children):
        if len(children) == 1:
            return children[0]
        raise Exception("bnot")
    
    def batom(self,children):
        if len(children) == 1:
            return children[0]
        raise Exception("batom")

    def com(self,children):
        if len(children) == 1 and isinstance(children[0],Token):
            return children[0]
        raise Exception("com")


def tree_to_string(tree:Union[ParseTree,Token]):
    
    if isinstance(tree, Token):
        return tree.value
    
    data = tree.data
    is_aexp = data in ["aexp","term","factor","add","sub","mul","call","input","lshift","rshift"]
    is_bexp = data in ["bexp","batom","and","or","not","eq","lt"]
    is_com = data in ["com","skip","assign","ifelse","while","seq","print","def"]
    
    if is_aexp:
        return aexp_tree_to_string(tree)
    if is_bexp:
        return bexp_tree_to_string(tree)
    if is_com:
        return com_tree_to_string(tree)
    
    print (data)
    raise Exception("Unknown token type")

def aexp_tree_to_string(tree:Union[ParseTree,Token]):
    
    if isinstance(tree, Token):
        return tree.value
    
    data = tree.data
    
    if data == "add":
        return aexp_tree_to_string(tree.children[0]) + "+" + aexp_tree_to_string(tree.children[1])
    elif data == "sub":
        return aexp_tree_to_string(tree.children[0]) + "-" + aexp_tree_to_string(tree.children[1])
    elif data == "mul":
        return "(" + aexp_tree_to_string(tree.children[0]) + ")*(" + aexp_tree_to_string(tree.children[1]) + ")"
    elif data == "aexp":
        return "" + aexp_tree_to_string(tree.children[0]) + ""
    elif data == "term":
        return "" + aexp_tree_to_string(tree.children[0]) + ""
    elif data == "factor":
        return "" + aexp_tree_to_string(tree.children[0]) + ""
    
    if data == "call":
        funcname = tree.children[0].value
        args = tree.children[1:]
        args_str = " ".join([aexp_tree_to_string(arg) for arg in args])
        
        return funcname + "(" + args_str + ")"
    
    if data == "input":
        return "input"

    print (data)
    
    raise Exception("Unknown token type")
            
def bexp_tree_to_string(tree:Union[ParseTree,Token]):
    
    if isinstance(tree, Token):
        return tree.value
    
    data = tree.data
    
    if data == "and":
        return "(" + bexp_tree_to_string(tree.children[0]) + ")and(" + bexp_tree_to_string(tree.children[1]) + ")"
    elif data == "or":
        return "(" + bexp_tree_to_string(tree.children[0]) + ")or(" + bexp_tree_to_string(tree.children[1]) + ")"
    elif data == "not":
        return "not(" + bexp_tree_to_string(tree.children[0]) + ")"
    
    elif data == "bexp":
        return "" + bexp_tree_to_string(tree.children[0]) + ""
    elif data == "batom":
        return "" + bexp_tree_to_string(tree.children[0]) + ""
    elif data == "bnot":
        return "" + bexp_tree_to_string(tree.children[0]) + ""
    elif data == "bor":
        return "" + bexp_tree_to_string(tree.children[0]) + ""
    elif data == "band":
        return "" + bexp_tree_to_string(tree.children[0]) + ""
    elif data == "eq":
        return "" + aexp_tree_to_string(tree.children[0]) + "=" + aexp_tree_to_string(tree.children[1]) + ""
    elif data ==  "lt":
        return "(" + aexp_tree_to_string(tree.children[0]) + "<" + aexp_tree_to_string(tree.children[1]) + ")"
    elif data == "le":
        return "(" + aexp_tree_to_string(tree.children[0]) + "<=" + aexp_tree_to_string(tree.children[1]) + ")"
    print (tree.pretty())
    raise Exception("Unknown token type")

def com_tree_to_string(tree:Union[ParseTree,Token]):
    
    if isinstance(tree, Token):
        return "skip"
    
    data = tree.data
    
    if data == "skip":
        return "skip"
    elif data == "assign":
        return "" + tree.children[0].value + ":=" + aexp_tree_to_string(tree.children[1]) + ""
    elif data == "ifelse":
        return "if " + bexp_tree_to_string(tree.children[0]) + " then " + com_tree_to_string(tree.children[1]) + " else " + com_tree_to_string(tree.children[2]) + "end"
    elif data == "seq":
        return "" + com_tree_to_string(tree.children[0]) + ";" + com_tree_to_string(tree.children[1]) + ""
    elif data == "while":
        return "while " + bexp_tree_to_string(tree.children[0]) + " do " + com_tree_to_string(tree.children[1]) + "end"
    elif data == "com":
        return "" + com_tree_to_string(tree.children[0]) + ""
    elif data == "print":
        return "print " + aexp_tree_to_string(tree.children[0]) + ""
    
    if data == "def":
        func_name = tree.children[0].value
        args = tree.children[1:-2]
        args_str = ""
        for arg in args:
            args_str += arg.value + " "
        com_str = com_tree_to_string(tree.children[-2])
        returned_aexp_str = aexp_tree_to_string(tree.children[-1])
        return "def "+func_name+"{...}"
        return "def " + func_name + "(" + args_str + "){" + com_str + "; return " + returned_aexp_str + "}"
    
    print (tree.pretty())
    raise Exception("Unknown token type")


def constract_ast (code : str,start : Literal["com","aexp","bexp"] = "com",grammar_file : str = "syntax.lark") -> ParseTree:
    IMP_grammar = ""

    with open(grammar_file, "r") as f:
        IMP_grammar = f.read()

    parser = Lark(IMP_grammar, start=start, parser='lalr',propagate_positions=True)
    try:
        parse_tree = parser.parse(code)
    except Exception as e:

        import traceback
        traceback.print_exc(1)
        print (e)

        exit (1)
    simplified_tree = RemoveRedundant().transform(parse_tree)
    
    return simplified_tree

def is_ast_of(ast:Union[ParseTree,Token]) -> Literal["com","aexp","bexp"]:
    if isinstance(ast, Token):
        if ast.type in ["NUM","VAR","CHAR","BINARY"]:
            return "aexp"
        
        if ast.type in ["TRUE","FALSE"]:
            return "bexp"
        
        if ast.type in ["SKIP"]:
            return "com"
        
        raise Exception("Unknown token type " + ast.type)
    
    data = ast.data
    
    if data in ["add","sub","mul","call","input","ptr_read","rshift","lshift"]:
        return "aexp"
    
    if data in ["and","or","not","eq","lt","le"]:
        return "bexp"
    
    if data in ["assign","ifelse","seq","while","print","def","ptr_assign","setstr"]:
        return "com"
    
    raise Exception("Unknown token type")

