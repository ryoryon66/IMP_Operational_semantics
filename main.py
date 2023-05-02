import time
from copy import deepcopy
from typing import DefaultDict, Union

from lark import Lark, Token, Transformer, Tree
from lark.lexer import Token
from lark.tree import Tree as ParseTree


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
    
    def batom(self,children):
        if len(children) == 1:
            return children[0]
        raise Exception("batom")

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
    
    def __contains__(self, key):
        for k,v in reversed(self.env):
            if k == key:
                return True
        return False
    
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


class DeriviationTreeNode:
    
    def __init__(self,exp:Union[ParseTree,Token],env:Env):
        self.exp = exp
        self.env = env
        
        self.ancestors : list[DeriviationTreeNode] = []
        self._id = str(time.time()).replace(".","")
        self.res = None
        return

    def get_node_label (self):

        label = "<"+ tree_to_string(self.exp) +","+str(self.env)+">" + "→" + str(self.res)
        label = label.replace("\"","")
        label = label.replace("\'","")
        label = label.replace("<","\\<")
        label = label.replace(">","\\>")
        
        return label

    def out_to_dot(self):
        out = ""
        out += "digraph G {\n"
        out += "node [shape=record];\n"
        out += self._out_to_dot()
        out += "}"
        return out
    
    def _out_to_dot(self):

        out = ""
        color = "black"
        
        if isinstance(self.exp, Token):
            if self.exp.type in ["NUM","VAR"]:
                color = "purple"
            if self.exp.type in ["TRUE","FALSE"]:
                color = "brown"
            if self.exp.type in ["SKIP"]:
                color = "orange"
        else:
            if self.exp.data == "while":
                color = "red"
            if self.exp.data == "ifelse":
                color = "blue"
            if self.exp.data == "assign":
                color = "green"
            if self.exp.data == "seq":
                color = "black"
            if self.exp.data == "print":
                color = "orange"
            
            if self.exp.data in ["add","sub","mul"]:
                color = "purple"
            
            if self.exp.data in ["eq","lt","and","or","not"]:
                color = "brown"
        
        
        out += self._id + " [label=\"{" + self.get_node_label() + "}\""
        out += " color=\"" + color + "\""
        #　枠の幅
        out += " penwidth=\"" + "3.0" + "\""

        out += " style=\"filled\""
        # fillcolor
        out += " fillcolor=\"" + "gray" + "\""
        
        out += "];\n"
        
        for anc in self.ancestors:
            out += anc._out_to_dot()
            out += anc._id + " -> " + self._id + ";\n"
        return out
    
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
            self.res = deepcopy(self.env)
            return deepcopy(self.env)
        
        data = self.exp.data
        

        if data == "assign":
            
            var = self.exp.children[0].value
            aexp = self.exp.children[1]
            
            ancestor = DeriviationTreeNode(aexp,deepcopy(self.env))
            
            new_env = deepcopy(self.env)
            new_env[var] = ancestor.eval()
            
            self.ancestors.append(ancestor)
            self.res = new_env
            
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
            self.res = ancestor2.eval()
            
            return self.res
        
        if data == "while":
            
            bexp = self.exp.children[0]
            com = self.exp.children[1]
            
            ancestor1 = DeriviationTreeNode(bexp,deepcopy(self.env))
            
            if not ancestor1.eval():
                self.ancestors.append(ancestor1)
                self.res = deepcopy(self.env)
                return deepcopy(self.env)
            else:
                ancestor2 = DeriviationTreeNode(com,deepcopy(self.env))
                self.ancestors.append(ancestor1)
                self.ancestors.append(ancestor2)
                env1 = ancestor2.eval()
                ancestor3 = DeriviationTreeNode(self.exp,env1)
                env2 = ancestor3.eval()
                self.ancestors.append(ancestor3)
                self.res = env2
                return env2
        
        if data == "seq":
            ancestor1 = DeriviationTreeNode(self.exp.children[0],deepcopy(self.env))
            ancestor2 = DeriviationTreeNode(self.exp.children[1],deepcopy(ancestor1.eval()))
            
            self.ancestors.append(ancestor1)
            self.ancestors.append(ancestor2)
            self.res = ancestor2.eval()
            return self.res
        if data == "print":
            ancestor1 = DeriviationTreeNode(self.exp.children[0],deepcopy(self.env))
            print (ancestor1.eval())
            self.ancestors.append(ancestor1)
            self.res = deepcopy(self.env)
            return deepcopy(self.env)

        if data == "com":
            raise Exception("com should be removed")
    
        raise Exception("Unknown token type")

    def eval_aexp(self) -> int:
        
        if isinstance(self.exp, Token):
            t = self.exp.type
            
            if t == "NUM":
                self.res = int(self.exp.value)
                return int(self.exp.value)
            
            if t == "VAR":
                if not self.exp.value in self.env:
                    self.res = 0
                    
                    return 0
                self.res = self.env[self.exp.value]
                return self.env[self.exp.value]
            
            raise Exception("Unknown token type")
        
        data = self.exp.data
        
        if data == "add":
            ancestor1 = DeriviationTreeNode(self.exp.children[0],deepcopy(self.env))
            ancestor2 = DeriviationTreeNode(self.exp.children[1],deepcopy(self.env))
            res = ancestor1.eval() + ancestor2.eval()
            self.ancestors.append(ancestor1)
            self.ancestors.append(ancestor2)
            self.res = res
            return res
        
        if data == "sub":
            ancestor1 = DeriviationTreeNode(self.exp.children[0],deepcopy(self.env))
            ancestor2 = DeriviationTreeNode(self.exp.children[1],deepcopy(self.env))
            res = ancestor1.eval() - ancestor2.eval()
            self.ancestors.append(ancestor1)
            self.ancestors.append(ancestor2)
            self.res = res
            return res
        
        if data == "mul":
            ancestor1 = DeriviationTreeNode(self.exp.children[0],deepcopy(self.env))
            ancestor2 = DeriviationTreeNode(self.exp.children[1],deepcopy(self.env))
            res = ancestor1.eval() * ancestor2.eval()
            self.ancestors.append(ancestor1)
            self.ancestors.append(ancestor2)
            self.res = res
            return res
        
        raise Exception("Unknown token type")

    def eval_bexp(self) -> bool:
        
        if isinstance(self.exp, Token):
            t = self.exp.type
            
            if t == "TRUE":
                self.res = True
                return True
            
            if t == "FALSE":
                self.res = False
                return False
            
            raise Exception("Unknown token type")

        data = self.exp.data
        
        if data == "and":
            ancestor1 = DeriviationTreeNode(self.exp.children[0],deepcopy(self.env))
            ancestor2 = DeriviationTreeNode(self.exp.children[1],deepcopy(self.env))
            res = ancestor1.eval() and ancestor2.eval()
            self.ancestors.append(ancestor1)
            self.ancestors.append(ancestor2)
            self.res = res
            return res
        
        if data == "or":
            ancestor1 = DeriviationTreeNode(self.exp.children[0],deepcopy(self.env))
            ancestor2 = DeriviationTreeNode(self.exp.children[1],deepcopy(self.env))
            res = ancestor1.eval() or ancestor2.eval()
            self.ancestors.append(ancestor1)
            self.ancestors.append(ancestor2)
            self.res = res
            return res
        
        if data == "not":
            ancestor1 = DeriviationTreeNode(self.exp.children[0],deepcopy(self.env))
            res = not ancestor1.eval()
            self.ancestors.append(ancestor1)
            self.res = res
            return res
        
        if data == "eq":
            ancestor1 = DeriviationTreeNode(self.exp.children[0],deepcopy(self.env))
            ancestor2 = DeriviationTreeNode(self.exp.children[1],deepcopy(self.env))
            res = ancestor1.eval() == ancestor2.eval()
            self.ancestors.append(ancestor1)
            self.ancestors.append(ancestor2)
            self.res = res
            return res
        
        if data == "lt":
            ancestor1 = DeriviationTreeNode(self.exp.children[0],deepcopy(self.env))
            ancestor2 = DeriviationTreeNode(self.exp.children[1],deepcopy(self.env))
            res = ancestor1.eval() < ancestor2.eval()
            self.ancestors.append(ancestor1)
            self.ancestors.append(ancestor2)
            self.res = res
            return res

        print (data)
        raise Exception("Unknown token type")

def tree_to_string(tree:Union[ParseTree,Token]):
    
    if isinstance(tree, Token):
        return tree.value
    
    data = tree.data
    is_aexp = data in ["aexp","term","factor","add","sub","mul"]
    is_bexp = data in ["bexp","batom","and","or","not","eq","lt"]
    is_com = data in ["com","skip","assign","ifelse","while","seq","print"]
    
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
        return "while " + bexp_tree_to_string(tree.children[0]) + " do(" + com_tree_to_string(tree.children[1]) + ")"
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
    
    print ("constructing deriviation tree...")
    
    deriviation_tree = DeriviationTreeNode(simplified_tree,Env())
    res = deriviation_tree.eval()
    
    print ("finished constructing deriviation tree")
    
    return deriviation_tree

    
program = ""

with open("sum.txt", "r") as f:
    program = f.read()


tree = run_code(program)
print ("_" * 20)
dot_graph = tree.out_to_dot()

# save as txt
with open("sum_deriviation_tree.txt", "w") as f:
    f.write(dot_graph)
    