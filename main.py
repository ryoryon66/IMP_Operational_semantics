from lark import Lark
from lark.tree import Tree as ParseTree
from lark.lexer import Token
from typing import Union,DefaultDict
from copy import deepcopy
import time
from lark import Transformer,Tree,Token

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
        if len(children) == 1 and isinstance(children[0],Token):
            return children[0]
        raise Exception("factor")
    
    def bexp(self,children):
        if len(children) == 1:
            return children[0]
        raise Exception("bexp")
    
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

    def com(self,children):
        if len(children) == 1 and isinstance(children[0],Token):
            return children[0]
        raise Exception("com")

class Env:
    def __init__(self):
        self.env : list[tuple] = [] # list of tuples (key,value)
    
    def __getitem__(self, key):
        
        for k,v in reversed(self.env):
            if k == key:
                return v
            
        self.env.append((key,0))
        return 0
    
    def __setitem__(self, key, value):
        self.env.append((key,value))
    
    def __repr__(self):
        return self.get_simple_str()
    
    def __str__(self):
        return self.get_simple_str()
    
    def get_simple_str(self):
        # remove duplicates
        env_d = dict()
        for k,v in self.env:
            env_d[k] = v
        
        env = []
        for k,v in env_d.items():
            env.append((k,v))
        
        return str(env)


env : Env = Env()
class DeriviationTreeNode:
    
    def __init__(self,exp:Union[ParseTree,Token],env:Env):
        self.exp = exp
        self.env = env
        
        self.ancestors : list[DeriviationTreeNode] = []
        self._id = str(time.time()).replace(".","")
        self.res = None
        return

    def get_node_label (self):
        return "<"+self.exp +  ","+self.env+">" + "->" + str(self.res)
    
    def eval(self) -> Union[int,bool,Env]:
        
        if isinstance(self.exp, Token):
            is_aexp = self.exp.type in ["NUM","VAR"]
            is_bexp = self.exp.type in ["TRUE","FALSE"]
            is_com = self.exp.type in ["SKIP"]
            
            if is_aexp:
                return self.eval_aexp()
            if is_bexp:
                return self.eval_bexp()
            if is_com:
                return self.eval_com()
        
        data = self.exp.data
        
        is_aexp = data in ["aexp","term","factor","add","sub","mul"]
        is_bexp = data in ["bexp","batom","and","or","not","eq","lt"]
        is_com = data in ["com","skip","assign","ifelse","while","seq","print"]
        
        if is_aexp:
            return self.eval_aexp()
        if is_bexp:
            return self.eval_bexp()
        if is_com:
            return self.eval_com()
        
        print (self.exp)
        raise Exception("Unknown token type")
    
    def eval_com(self) -> Env:
        
        if isinstance(self.exp, Token):
            return deepcopy(self.env)
        
        data = self.exp.data
        

        if data == "assign":
            
            var = self.exp.children[0].value
            aexp = self.exp.children[1]
            
            ancestor = DeriviationTreeNode(aexp,deepcopy(self.env))
            
            new_env = deepcopy(self.env)
            new_env[var] = ancestor.eval()
            
            self.ancestors.append(ancestor)
            
            return new_env
        if data == "ifelse":
            bexp = self.exp.children[0]
            com1 = self.exp.children[1]
            com2 = self.exp.children[2]
            
            ancestor1 = DeriviationTreeNode(bexp,deepcopy(self.env))
            
            
            if ancestor1.eval():
                ancestor2 = DeriviationTreeNode(com1,deepcopy(self.env))
            else:
                ancestor2 = DeriviationTreeNode(com2,deepcopy(self.env))
            
            self.ancestors.append(ancestor1)
            self.ancestors.append(ancestor2)
            
            return ancestor2.eval()
        if data == "while":
            
            bexp = self.exp.children[0]
            com = self.exp.children[1]
            
            ancestor1 = DeriviationTreeNode(bexp,deepcopy(self.env))
            
            if not ancestor1.eval():
                self.ancestors.append(ancestor1)
                return deepcopy(self.env)
            else:
                ancestor2 = DeriviationTreeNode(com,deepcopy(self.env))
                self.ancestors.append(ancestor1)
                self.ancestors.append(ancestor2)
                env1 = ancestor2.eval()
                ancestor3 = DeriviationTreeNode(self.exp,env1)
                env2 = ancestor3.eval()
                self.ancestors.append(ancestor3)
                return env2
        
        if data == "seq":
            ancestor1 = DeriviationTreeNode(self.exp.children[0],deepcopy(self.env))
            ancestor2 = DeriviationTreeNode(self.exp.children[1],deepcopy(ancestor1.eval()))
            
            self.ancestors.append(ancestor1)
            self.ancestors.append(ancestor2)
            return ancestor2.eval()
        if data == "print":
            ancestor1 = DeriviationTreeNode(self.exp.children[0],deepcopy(self.env))
            print (ancestor1.eval())
            self.ancestors.append(ancestor1)
            return deepcopy(self.env)

        if data == "com":
            raise Exception("com should be removed")
    
        raise Exception("Unknown token type")

    def eval_aexp(self) -> int:
        
        if isinstance(self.exp, Token):
            t = self.exp.type
            
            if t == "NUM":
                return int(self.exp.value)
            
            if t == "VAR":
                return self.env[self.exp.value]
            
            raise Exception("Unknown token type")
        
        data = self.exp.data
        
        if data == "add":
            ancestor1 = DeriviationTreeNode(self.exp.children[0],deepcopy(self.env))
            ancestor2 = DeriviationTreeNode(self.exp.children[1],deepcopy(self.env))
            res = ancestor1.eval() + ancestor2.eval()
            self.ancestors.append(ancestor1)
            self.ancestors.append(ancestor2)
            return res
        
        if data == "sub":
            ancestor1 = DeriviationTreeNode(self.exp.children[0],deepcopy(self.env))
            ancestor2 = DeriviationTreeNode(self.exp.children[1],deepcopy(self.env))
            res = ancestor1.eval() - ancestor2.eval()
            self.ancestors.append(ancestor1)
            self.ancestors.append(ancestor2)
            return res
        
        if data == "mul":
            ancestor1 = DeriviationTreeNode(self.exp.children[0],deepcopy(self.env))
            ancestor2 = DeriviationTreeNode(self.exp.children[1],deepcopy(self.env))
            res = ancestor1.eval() * ancestor2.eval()
            self.ancestors.append(ancestor1)
            self.ancestors.append(ancestor2)
            return res
        
        raise Exception("Unknown token type")

    def eval_bexp(self) -> bool:
        
        if isinstance(self.exp, Token):
            t = self.exp.type
            
            if t == "TRUE":
                return True
            
            if t == "FALSE":
                return False
            
            raise Exception("Unknown token type")

        data = self.exp.data
        
        if data == "and":
            ancestor1 = DeriviationTreeNode(self.exp.children[0],deepcopy(self.env))
            ancestor2 = DeriviationTreeNode(self.exp.children[1],deepcopy(self.env))
            res = ancestor1.eval() and ancestor2.eval()
            self.ancestors.append(ancestor1)
            self.ancestors.append(ancestor2)
            return res
        
        if data == "or":
            ancestor1 = DeriviationTreeNode(self.exp.children[0],deepcopy(self.env))
            ancestor2 = DeriviationTreeNode(self.exp.children[1],deepcopy(self.env))
            res = ancestor1.eval() or ancestor2.eval()
            self.ancestors.append(ancestor1)
            self.ancestors.append(ancestor2)
            return res
        
        if data == "not":
            ancestor1 = DeriviationTreeNode(self.exp.children[0],deepcopy(self.env))
            res = not ancestor1.eval()
            self.ancestors.append(ancestor1)
            return res
        
        if data == "eq":
            ancestor1 = DeriviationTreeNode(self.exp.children[0],deepcopy(self.env))
            ancestor2 = DeriviationTreeNode(self.exp.children[1],deepcopy(self.env))
            res = ancestor1.eval() == ancestor2.eval()
            self.ancestors.append(ancestor1)
            self.ancestors.append(ancestor2)
            return res
        
        if data == "lt":
            ancestor1 = DeriviationTreeNode(self.exp.children[0],deepcopy(self.env))
            ancestor2 = DeriviationTreeNode(self.exp.children[1],deepcopy(self.env))
            res = ancestor1.eval() < ancestor2.eval()
            self.ancestors.append(ancestor1)
            self.ancestors.append(ancestor2)
            return res
    
        raise Exception("Unknown token type")

def tree_to_string(tree:Union[ParseTree,Token]):
    
    if isinstance(tree, Token):
        return tree.value
    
    data = tree.data
    is_aexp = data in ["aexp","term","factor","add","sub","mul"]
    is_bexp = data in ["bexp","batom","and","or","not"]
    is_com = data in ["com","skip","assign","if","while","seq"]
    
    if is_aexp:
        return aexp_tree_to_string(tree)
    if is_bexp:
        return bexp_tree_to_string(tree)
    if is_com:
        return com_tree_to_string(tree)
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
        return "" + aexp_tree_to_string(tree.children[0]) + "<" + aexp_tree_to_string(tree.children[1]) + ""
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
        return "if " + bexp_tree_to_string(tree.children[0]) + " then " + com_tree_to_string(tree.children[1]) + " else " + com_tree_to_string(tree.children[2]) + ""
    elif data == "seq":
        return "" + com_tree_to_string(tree.children[0]) + ";" + com_tree_to_string(tree.children[1]) + ""
    elif data == "while":
        return "while" + bexp_tree_to_string(tree.children[0]) + "do(" + com_tree_to_string(tree.children[1]) + ")"
    elif data == "com":
        return "" + com_tree_to_string(tree.children[0]) + ""
    elif data == "print":
        return "print " + aexp_tree_to_string(tree.children[0]) + ""
    
    print (tree.pretty())
    raise Exception("Unknown token type")




def run_code (code : str) :
    IMP_grammar = ""

    with open("syntax.lark", "r") as f:
        IMP_grammar = f.read()

    parser = Lark(IMP_grammar, start='com', parser='lalr',propagate_positions=True)
    parse_tree = parser.parse(code)
    simplified_tree = RemoveRedundant().transform(parse_tree)
    
    # res = evaluate(simplified_tree,Env())
    

    # print (simple.pretty())
    # print ("_" * 20)
    # print (parse_tree.pretty())
    
    
    
    print ("tree mode")
    
    deriviation_tree = DeriviationTreeNode(simplified_tree,Env())
    res = deriviation_tree.eval()
    
    print (res)
    
    return deriviation_tree

def evaluate(exp:Union[ParseTree,Token],env:Env) -> Union[int,bool,Env]:
    
    if isinstance(exp, Token):
        is_aexp = exp.type in ["NUM","VAR"]
        is_bexp = exp.type in ["TRUE","FALSE"]
        is_com = exp.type in ["SKIP"]
        
        if is_aexp:
            return calculate_aexp(exp,env)
        elif is_bexp:
            return calculate_bexp(exp,env)
        elif is_com:
            return calculate_command(exp,env)
        raise Exception("Unknown token type")
    
    data = exp.data
    
    is_aexp = data in ["add","sub","mul","aexp","term","factor"]
    is_bexp = data in ["bexp","band","bor","bnot","batom"]
    is_com = data in ["com","skip","assign","ifelse","while","seq","print"]
    
    if is_aexp:
        return calculate_aexp(exp,env)
    elif is_bexp:
        return calculate_bexp(exp,env)
    elif is_com:
        return calculate_command(exp,env)
    raise Exception("Unknown token type")

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
    # elif data == "aexp":
    #     return calculate_aexp(aexp.children[0],env)
    # elif data == "term":
    #     return calculate_aexp(aexp.children[0],env)
    # elif data == "factor":
    #     return calculate_aexp(aexp.children[0],env)
    
    raise Exception("Unknown token type")

def calculate_bexp(bexp : Union[ParseTree,Token],env:Env) -> bool:
    
    
    if isinstance(bexp, Token):
        if bexp.type == "TRUE":
            return True
        elif bexp.type == "FALSE":
            return False
        raise Exception("Unknown token type")
    
    data = bexp.data
    
    # if data == "bexp":
    #     return calculate_bexp(bexp.children[0],env)
    # elif data == "band":
    #     return calculate_bexp(bexp.children[0],env)
    # elif data == "bor":
    #     return calculate_bexp(bexp.children[0],env)
    # elif data == "bnot":
    #     return calculate_bexp(bexp.children[0],env)
    # elif data == "batom":
    #     return calculate_bexp(bexp.children[0],env)
    if data=="or":
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
    
    # if data == "com":
    #     return calculate_command(command.children[0],env)
        
    if data == "seq":
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

# IMP_grammar = ""

# with open("syntax.lark", "r") as f:
#     IMP_grammar = f.read()

# parser = Lark(IMP_grammar, start='aexp', parser='lalr',propagate_positions=True)


# # test aexp_tree_to_string
# aexp_tree = parser.parse("x + 1 * 2 + (3 + 4) * 7")
# print(tree_to_string(aexp_tree))
# Transformer = RemoveRedundant()
# simpligied = Transformer.transform(aexp_tree)
# print (tree_to_string(simpligied))

# print (aexp_tree.pretty())
# print ("_" * 20)
# print (simpligied.pretty())


# # test bexp_tree_to_string
# parser = Lark(IMP_grammar, start='bexp', parser='lalr',propagate_positions=True)
# bexp_tree = parser.parse("x <1 and y = 2 or not z = 3")
# print(tree_to_string(bexp_tree))

# simple = RemoveRedundant().transform(bexp_tree)
# print(tree_to_string(simple))

# print (bexp_tree.pretty())
# print ("_" * 20)
# print (simple.pretty())

# # test com_tree_to_string
# parser = Lark(IMP_grammar, start='com', parser='lalr',propagate_positions=True)
# com_tree = parser.parse(r'x := 1; if x < 1 then x := 2 else x := 3;while x < 10 do (x := x + 1;print x)')
# print(tree_to_string(com_tree))

# simple = RemoveRedundant().transform(com_tree)
# print(tree_to_string(simple))

# print (com_tree.pretty())
# print ("_" * 20)
# print (simple.pretty())