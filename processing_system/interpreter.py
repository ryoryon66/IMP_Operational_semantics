import argparse
import time
from copy import deepcopy
from dataclasses import dataclass
from typing import  Union


from lark.lexer import Token
from lark.tree import Tree as ParseTree

from utils import  tree_to_string,constract_ast

# recursion limit
import sys

sys.setrecursionlimit(10 ** 9)
    


@dataclass
class FunctionInfo:
    args : list[str]
    com : Union[ParseTree,Token] # com
    aexp_returned : Union[ParseTree,Token] # return aexp
    
    def __repr__(self):
        return f"fun({[str(arg) for arg in self.args]})"
    
    def __str__(self):
        return f"fun({self.args})"

class Env:
    def __init__(self):
        self.env : list[tuple[str,Union[int,FunctionInfo]]] = [] # list of tuples (key,value)
    
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
        label = label.replace("{","\\{")
        label = label.replace("}","\\}")
        
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
            if self.exp.data in ["def","assign"]:
                color = "green"
            if self.exp.data == "seq":
                color = "black"
            if self.exp.data == "print":
                color = "orange"
            
            if self.exp.data in ["add","sub","mul","call"]:
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
    
    def eval(self) -> Union[Union[int,FunctionInfo],bool,Env]:
        
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
        
        is_aexp = data in ["aexp","term","factor","add","sub","mul","call"]
        is_bexp = data in ["bexp","batom","and","or","not","eq","lt"]
        is_com = data in ["com","skip","assign","ifelse","while","seq","print","def"]
        
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
            self.ancestors.append(ancestor)
            new_env[var] = ancestor.eval()
            
            self.res = new_env
            
            return new_env
        if data == "ifelse":
            bexp = self.exp.children[0]
            com1 = self.exp.children[1]
            com2 = self.exp.children[2]
            
            ancestor1 = DeriviationTreeNode(bexp,deepcopy(self.env))
            self.ancestors.append(ancestor1)
            
            
            if ancestor1.eval():
                ancestor2 = DeriviationTreeNode(com1,deepcopy(self.env))
            else:
                ancestor2 = DeriviationTreeNode(com2,deepcopy(self.env))
            
 
            self.ancestors.append(ancestor2)
            self.res = ancestor2.eval()
            
            return self.res
        
        if data == "while":
            
            bexp = self.exp.children[0]
            com = self.exp.children[1]
            
            ancestor1 = DeriviationTreeNode(bexp,deepcopy(self.env))
            self.ancestors.append(ancestor1)
            
            if not ancestor1.eval():
                self.res = deepcopy(self.env)
                return deepcopy(self.env)
            else:
                ancestor2 = DeriviationTreeNode(com,deepcopy(self.env))

                self.ancestors.append(ancestor2)
                env1 = ancestor2.eval()
                ancestor3 = DeriviationTreeNode(self.exp,env1)
                self.ancestors.append(ancestor3)
                env2 = ancestor3.eval()
                self.res = env2
                return env2
        
        if data == "seq":
            ancestor1 = DeriviationTreeNode(self.exp.children[0],deepcopy(self.env))
            self.ancestors.append(ancestor1)
            ancestor2 = DeriviationTreeNode(self.exp.children[1],deepcopy(ancestor1.eval()))
            self.ancestors.append(ancestor2)
            self.res = ancestor2.eval()
            return self.res
        if data == "print":
            ancestor1 = DeriviationTreeNode(self.exp.children[0],deepcopy(self.env))
            self.ancestors.append(ancestor1)
            line = self.exp._meta.line
            print (f"line{line}",ancestor1.eval())
            self.res = deepcopy(self.env)
            return deepcopy(self.env)
        
        if data == "def":
            var = self.exp.children[0].value
            args = [x.value for x in self.exp.children[1:-2]]
            com = self.exp.children[-2]
            aexp_returned = self.exp.children[-1]
            
            new_env = deepcopy(self.env)
            new_env[var] = FunctionInfo(args,com,aexp_returned)
            
            self.res = new_env
            return new_env
            

        if data == "com":
            raise Exception("com should be removed")
    
        raise Exception("Unknown token type")

    def eval_aexp(self) -> Union[int,FunctionInfo]:
        
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
            self.ancestors.append(ancestor1)
            self.ancestors.append(ancestor2)
            res = ancestor1.eval() + ancestor2.eval()
            self.res = res
            return res
        
        if data == "sub":
            ancestor1 = DeriviationTreeNode(self.exp.children[0],deepcopy(self.env))
            ancestor2 = DeriviationTreeNode(self.exp.children[1],deepcopy(self.env))
            self.ancestors.append(ancestor1)
            self.ancestors.append(ancestor2)
            res = ancestor1.eval() - ancestor2.eval()
            self.res = res
            return res
        
        if data == "mul":
            ancestor1 = DeriviationTreeNode(self.exp.children[0],deepcopy(self.env))
            ancestor2 = DeriviationTreeNode(self.exp.children[1],deepcopy(self.env))
            self.ancestors.append(ancestor1)
            self.ancestors.append(ancestor2)
            res = ancestor1.eval() * ancestor2.eval()
            self.res = res
            return res
        
        if data == "call":

            func_name = self.exp.children[0].value # function name
            args_aexps = self.exp.children[1:] # arguments passed
            # args_ancestors = []
            
            function_info = self.env[func_name]
            env_passed = Env() # environment passed to the function

            for aexp, arg_name in zip(args_aexps,function_info.args):
                arg_node = DeriviationTreeNode(aexp,self.env)
                self.ancestors.append(arg_node)
                evaluated_v = arg_node.eval()
                assert isinstance(arg_name,str)
                env_passed[arg_name] = evaluated_v
            env_passed[func_name] = function_info #関数自身も引数に追加　再帰呼び出しのため
            
            #self.ancestors += args_ancestors
            
            com = function_info.com
            com_node = DeriviationTreeNode(com,env_passed)
            self.ancestors.append(com_node) #関数の本体をancestorsに追加
            env_returned = com_node.eval()
            assert isinstance(env_returned,Env)
          
            
            aexp_returned = function_info.aexp_returned
            aexp_node = DeriviationTreeNode(aexp_returned,env_returned)
            self.ancestors.append(aexp_node) #関数の返り値をancestorsに追加
            res = aexp_node.eval()
            assert isinstance(res,int)
            self.res = res
            return res
            
            
            
        print (data) 
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
            self.ancestors.append(ancestor1)
            self.ancestors.append(ancestor2)
            res = ancestor1.eval() and ancestor2.eval()
            self.res = res
            return res
        
        if data == "or":
            ancestor1 = DeriviationTreeNode(self.exp.children[0],deepcopy(self.env))
            ancestor2 = DeriviationTreeNode(self.exp.children[1],deepcopy(self.env))
            self.ancestors.append(ancestor1)
            self.ancestors.append(ancestor2)
            res = ancestor1.eval() or ancestor2.eval()
            self.res = res
            return res
        
        if data == "not":
            ancestor1 = DeriviationTreeNode(self.exp.children[0],deepcopy(self.env))
            self.ancestors.append(ancestor1)
            res = not ancestor1.eval()
            self.res = res
            return res
        
        if data == "eq":
            ancestor1 = DeriviationTreeNode(self.exp.children[0],deepcopy(self.env))
            ancestor2 = DeriviationTreeNode(self.exp.children[1],deepcopy(self.env))
            self.ancestors.append(ancestor1)
            self.ancestors.append(ancestor2)
            res = ancestor1.eval() == ancestor2.eval()
            self.res = res
            return res
        
        if data == "lt":
            ancestor1 = DeriviationTreeNode(self.exp.children[0],deepcopy(self.env))
            ancestor2 = DeriviationTreeNode(self.exp.children[1],deepcopy(self.env))
            self.ancestors.append(ancestor1)
            self.ancestors.append(ancestor2)
            res = ancestor1.eval() < ancestor2.eval()
            self.res = res
            return res
        
        if data == "le":
            raise Exception("Currently not supported. le is supported only for compiler")

        print (data)
        raise Exception("Unknown token type")



def run_code (code : str) :
    
    simplified_tree = constract_ast(code)
    print ("constructing deriviation tree...")
    
    from collections import Counter
    eval_count_for_line = Counter()
    
    def count_nodes(tree):
        if isinstance(tree.exp,Token):
            return 1
        eval_count_for_line[tree.exp.meta.line] += 1
        return 1 + sum([count_nodes(child) for child in tree.ancestors])
    
    def print_profile():
        print ("eval frequency for each line")
        # sort
        eval_count_for_line_list = sorted(eval_count_for_line.items(), key=lambda x:-x[1])
        total = sum(eval_count_for_line.values())
        for line, count in eval_count_for_line_list:
            print ("line {} : {} ({:.2f}%)".format(line,count,count/total*100))
            
        return
    
    deriviation_tree = DeriviationTreeNode(simplified_tree,Env())
    try:
        res = deriviation_tree.eval()
    except KeyboardInterrupt:
        print ("Keyboard Interruption!!!")
        print ("number of nodes in deriviation tree (aborted) : {}".format(count_nodes(deriviation_tree)))
        
        print_profile()
        exit ()
        
    print ("finished constructing deriviation tree")

    print ("number of nodes in deriviation tree : {}".format(count_nodes(deriviation_tree)))
    
    print_profile()

    return deriviation_tree


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="input file path")

    program_file_path = parser.parse_args().input

    if program_file_path == None:
        print("input file path is not specified")
        print ("use --input option")
        exit()

    program = ""

    with open(program_file_path, "r") as f:
        program = f.read()


    tree = run_code(program)
    print ("_" * 20)
    dot_graph = tree.out_to_dot()

    # save as txt
    print ("saving deriviation tree to file...")
    output_file_name = program_file_path.replace(".txt","_deriviation_tree.txt")
    with open(output_file_name, "w") as f:
        f.write(dot_graph)
    print ("finished saving deriviation tree to file")