import argparse
import time
from copy import deepcopy
from dataclasses import dataclass
from typing import  Union,final,Literal


from lark.lexer import Token
from lark.tree import Tree as ParseTree

from utils import  tree_to_string,constract_ast,is_ast_of

# recursion limit
import sys

sys.setrecursionlimit(10 ** 9)

Aexp = Union[Token,ParseTree]
Bexp = Union[Token,ParseTree]
Com = Union[Token,ParseTree]

# レジスタ番号
RegisterID = Literal[0,1,2,3,4,5,6,7]

# レジスタの割り当てALC Allocation
RSP_ALC   : final = 7 # 次に書き込む場所
RBP_ALC   : final = 6 # ベースレジスタ このレジスタからのオフセットで変数を指定する 返り先のアドレスを保存する
RT1_ALC   : final = 1
RT2_ALC   : final = 2
RAX_ALC   : final = 3 # 演算結果 aexpが評価された後の値が入る

RZERO_ALC : final = 0 # 0 register


class Variables():
    """とりあえず関数、ブロックはないものとしている。
    またオフセットの限界値が256なので変数の宣言は前に固めた方がいい
    """
    
    def __init__(self):
        self._variables : dict[str,int]= {} # 変数名 -> RBPからのオフセット
        self._offset : int = 1 # 次に書き込む場所を相対で表す
    
    def __contains__(self, key):
        return key in self._variables

    def update_variable(self,var_name:str,reg_id:RegisterID):
        """新規変数の時のみrspを更新してくれます。
        """
        
        if var_name in self._variables:
            offset = self._variables[var_name]
            # ST
            print (f"ST {reg_id} {offset}({RBP_ALC})") #既存の変数なのでrspは更新しない
            return
        
        # 新規変数
        offset = self._offset
        self._offset += 1
        self._variables[var_name] = offset
        # ST
        print (f"ST {reg_id} {offset}({RBP_ALC})")
        
        # 変数用でメモリを確保したのでスタックを伸ばす
        print (f"LI {RT1_ALC} {1}")
        print (f"SUB {RSP_ALC} {RT1_ALC}") # rsp -= 1
        return
            
    
    def load_variable(self,var_name:str,reg_id:RegisterID):
        """変数を指定されたレジスタにロードします。"""
        assert var_name in self._variables , f"変数{var_name}は宣言されていません。"
        offset = self._variables[var_name]
        # LD
        print (f"LD {reg_id} {offset}({RBP_ALC})") # R[reg_id] = *(RBP+offset)
        return
    

variables = Variables()


def codegen(ast : Union[ParseTree,Token]):
    kind = is_ast_of(ast)
    
    if kind == "aexp":
        codegen_aexp(ast)
        return
    
    if kind == "bexp":
        pass
    
    if kind == "com":
        codegen_com(ast)
        return
    
    raise Exception(f"codegen cannot handle {kind}")

def codegen_com(ast:Com):
    
    if isinstance(ast,Token):
        if ast.type == "SKIP":
            return
        raise Exception(f"codegen_com cannot handle {ast}")
    
    data = ast.data
    
    if data == "seq":
        com1 : Com = ast.children[0]
        com2 : Com = ast.children[1]
        
        codegen_com(com1)
        codegen_com(com2)
        return
    
    if data == "assign":
        variable_name = ast.children[0].value
        aexp : Aexp = ast.children[1]
        
        codegen_aexp(aexp)
        variables.update_variable(variable_name,RAX_ALC)
        return
        
    
    if data == "print":
        aexp : Aexp = ast.children[0]
        codegen_aexp(aexp)
        print(f"OUT {RAX_ALC} // print")
        return
    
    raise Exception(f"codegen_com cannot handle {data}")
        
    

def codegen_aexp(ast:Aexp):
    """aexpをコンパイルします。
    
    注意:評価後はRAXに結果が入っている。
    またスタックのtopに評価結果がpushされる(rspも更新)。
    
    """
    
    if isinstance(ast,Token) and ast.type == "NUM":
        print (f"LI {RT1_ALC} {ast.value}") # RT1 = ast.value
        print (f"ST {RT1_ALC} {0}({RSP_ALC})") # *(rsp+0) = RT1
        print (f"MOV {RAX_ALC} {RT1_ALC}") # RAX = RT1
        print (f"LI {RT1_ALC} {1}")
        print (f"SUB {RSP_ALC} {RT1_ALC}") # rsp -= 1
        return
    
    if isinstance(ast,Token) and ast.type == "VAR":
        var_name : str = ast.value
        assert isinstance(var_name,str)
        variables.load_variable(var_name,RAX_ALC)
        print (f"ST {RAX_ALC} {0}({RSP_ALC})") # *(rsp+0) = RAX
        print (f"LI {RT1_ALC} {1}")
        print (f"SUB {RSP_ALC} {RT1_ALC}") # rsp -= 1
        return

    data = ast.data
    
    if data == "add":
        codegen_aexp(ast.children[0]) # aexp compile... rsp -= 1
        codegen_aexp(ast.children[1]) # aexp compile... rsp -= 1
        print (f"LD {RT1_ALC} {1}({RSP_ALC})") # RT1 = *(rsp+1)
        print (f"LD {RAX_ALC} {2}({RSP_ALC})") # RAX = *(rsp+2)
        print (f"ADD {RAX_ALC} {RT1_ALC}") # RAX += RT1
        print (f"ST {RAX_ALC} {2}({RSP_ALC})") # *(rsp+2) = RAX
        print (f"LI {RT1_ALC} {1}")
        print (f"ADD {RSP_ALC} {RT1_ALC}") # rsp += 1
        return
        
    
    if data == "sub":
        codegen_aexp(ast.children[0])
        codegen_aexp(ast.children[1])
        print (f"LD {RT1_ALC} {1}({RSP_ALC})") # RT1 = *(rsp+1)
        print (f"LD {RAX_ALC} {2}({RSP_ALC})") # RAX = *(rsp+2)
        print (f"SUB {RAX_ALC} {RT1_ALC}") # RAX -= RT1
        print (f"ST {RAX_ALC} {2}({RSP_ALC})") # *(rsp+2) = RAX
        print (f"LI {RT1_ALC} {1}")
        print (f"ADD {RSP_ALC} {RT1_ALC}") # rsp += 1
        
        return 
    
    print (data)
    raise Exception(f"codegen_aexp cannot handle {data}")

def init_register():
    print (f"LI {RBP_ALC} {1}")
    print (f"SLL {RBP_ALC} {10}") # RBP = 1024
    print (f"MOV {RSP_ALC} {RBP_ALC}") # RSP = RBP
    print (f"LI {RT1_ALC} {1}")
    print (f"SUB {RSP_ALC} {RT1_ALC}") # RSP = RSP - 1
    return


def run_compiler(program:str):
    tree = constract_ast(program,"com")
    
    init_register()
    
    codegen(tree)
    
    print (f"OUT {RAX_ALC}")
    
    print (f"HLT")
    
    return
    


if __name__ == "__main__":
    
    # program = "(8 + 2) - (3 + 4) + (5 - (6 + 7))"
    # program = "print 1 + 2 - (8 + 4)"
    # program = "x := 1 + 2 - (8 + 4); print x + x + x"
    # program = "x := 7; y := x + 2 + x; print x-y"
    # program = "x := 7; y := x; print x-y; print x + y"
    program = "x := 7; y := 7; print x-7"
    program = "x := 1; if x = 1 then print 100 else print 200 end"
    

    
    run_compiler(program)



# program = "(8 + 2) - (3 + 4) + (5 - (6 + 7))"    
# program = "skip"