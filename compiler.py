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

label_count : int = 0 # アセンブリに吐くラベルの通し番号


def codegen(ast : Union[ParseTree,Token]):
    kind = is_ast_of(ast)
    
    if kind == "aexp":
        codegen_aexp(ast)
        return
    
    if kind == "bexp":
        codegen_bexp(ast)
        return
    
    if kind == "com":
        codegen_com(ast)
        return
    
    raise Exception(f"codegen cannot handle {kind}")

def codegen_com(ast:Com):
    
    global label_count
    
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
    
    if data == "ifelse":
        
        bexp : Bexp = ast.children[0]
        com1 : Com = ast.children[1]
        com2 : Com = ast.children[2]
        
        codegen_bexp(bexp)
        
        # RAXと0を比較する
        print (f"LI {RT1_ALC} {0}")
        print (f"SUB {RT1_ALC} {RAX_ALC}") # RAX = RT1 = 0かどうかを条件コードZからもらう Z=0ならelseに飛ぶ
        print (f"BE .Lelse{label_count}")
        
        codegen_com(com1)
        
        print (f"B .Lend{label_count}")
        
        
        print (f".Lelse{label_count}")
        codegen_com(com2)
        print (f".Lend{label_count}")
        
        label_count += 1
        
        
        return

        
    
    if data == "print":
        aexp : Aexp = ast.children[0]
        codegen_aexp(aexp)
        print(f"OUT {RAX_ALC} // print {aexp}")
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


def codegen_bexp(ast:Bexp):
    """インタプリタのときとは違って、コンパイラの方ではAexpと同じように整数が返ってくると考えてコンパイルする. true=1,false=0として扱う.
    """
    
    if isinstance(ast,Token) and ast.type == "TRUE":
        print (f"LI {RAX_ALC} {1}") # RAX = 1
        print (f"ST {RAX_ALC} {0}({RSP_ALC})") # *(rsp+0) = RAX
        print (f"SUB {RSP_ALC} {RAX_ALC}") # rsp -= 1　RAXを使って短縮
        # print (f"LI {RT1_ALC} {1}")
        # print (f"SUB {RSP_ALC} {RT1_ALC}")
        return
    
    if isinstance(ast,Token) and ast.type == "FALSE":
        print (f"LI {RAX_ALC} {0}") # RAX = 0
        print (f"ST {RAX_ALC} {0}({RSP_ALC})") # *(rsp+0) = RAX
        print (f"LI {RT1_ALC} {1}")    # RT1 = 1
        print (f"SUB {RSP_ALC} {RT1_ALC}") # rsp -= 1
        return
    
    data = ast.data
    
    if data == "eq":
        aexp1 = ast.children[0]
        aexp2 = ast.children[1]
        
        codegen_aexp(aexp1)
        codegen_aexp(aexp2)
        
        print (f"LD {RT1_ALC} {2}({RSP_ALC})") # RT1 = *(rsp+2)
        # RAXから引き算して、RAXが0か判定する
        print (f"SUB {RAX_ALC} {RT1_ALC}") # RAX -= RT1
        
        # フラグレジスタを使いたいけどそういう命令がない...
        #　0は符号反転しても符号が変わらないつまりx or -xの符号ビットが0となる唯一の数(これxorでもいいのか？コーナーケースがあるかも　TODO)
        print (f"LI {RT1_ALC} {0}")
        print (f"SUB {RT1_ALC} {RAX_ALC}") # RT1 = 0 - RAX
        print (f"OR {RAX_ALC} {RT1_ALC}") # RAX or RAX
        print (f"SRL {RAX_ALC} {15}") # RAX >>= 15 論理シフト　等号成立なら0になる XORをとって反転
        print (f"LI {RT1_ALC} {1}")
        print (f"XOR {RAX_ALC} {RT1_ALC}") # RAX ^= RT1 等号成立なら1になる
        
        print (f"ST {RAX_ALC} {2}({RSP_ALC})") # *(rsp+2) = RAX
        print (f"LI {RT1_ALC} {1}")
        print (f"ADD {RSP_ALC} {RT1_ALC}") # rsp += 1
        
        return
        

    
    if data == "lt":
        
        # フラグレジスタを使いたいけどそういう命令がない...
        #　引き算して符号が分かったら勝ちかな。setl欲しい。。。
        # 論理→シフト15ビットで符号が分かる
        # 引き算してからシフトして、0かどうかで判断するかな。
        
        raise Exception("lt is not implemented")
    
    if data == "and":
        bexp1 = ast.children[0]
        bexp2 = ast.children[1]
        
        codegen_bexp(bexp1)
        codegen_bexp(bexp2)
        
        # bexp1の結果をRT1にLD
        print (f"LD {RT1_ALC} {2}({RSP_ALC})") # RT1 = *(rsp+2)
        # RAXにbexp2の結果が入っているので、RT1とのANDをとる
        print (f"AND {RAX_ALC} {RT1_ALC}") # RAX = RAX & RT1
        # RAXを*(rsp+2)にST
        print (f"ST {RAX_ALC} {2}({RSP_ALC})") # *(rsp+2) = RAX
        
        # pop 2 push 1なのでrspを1減らす
        print (f"LI {RT1_ALC} {1}")
        print (f"SUB {RSP_ALC} {RT1_ALC}") # rsp -= 1
        return
    
    if data == "or":
        bexp1 = ast.children[0]
        bexp2 = ast.children[1]
        
        codegen_bexp(bexp1)
        codegen_bexp(bexp2)
        
        # bexp1の結果をRT1にLD
        print (f"LD {RT1_ALC} {2}({RSP_ALC})") # RT1 = *(rsp+2)
        # RAXにbexp2の結果が入っているので、RT1とのANDをとる
        print (f"OR {RAX_ALC} {RT1_ALC}") # RAX = RAX & RT1
        # RAXを*(rsp+2)にST
        print (f"ST {RAX_ALC} {2}({RSP_ALC})") # *(rsp+2) = RAX
        
        # pop 2 push 1なのでrspを1減らす
        print (f"LI {RT1_ALC} {1}")
        print (f"SUB {RSP_ALC} {RT1_ALC}") # rsp -= 1
        return
    
    if data == "not":
        bexp = ast.children[0]
        codegen_bexp(bexp)
        
        # 1をLIして、RAXとのXORをとる
        print (f"LI {RT1_ALC} {1}") # RT1 = 1
        print (f"XOR {RAX_ALC} {RT1_ALC}") # RAX = RAX ^ RT1
        print (f"ST {RAX_ALC} {0}({RSP_ALC})") # *(rsp+0) = RAX
        
        # pop 1 push 1なのでrspは変わらない
        
        return
    
    raise Exception(f"codegen_bexp cannot handle {data}")


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
    
    # print (f"OUT {RAX_ALC}")
    
    print (f"HLT")
    
    return
    


if __name__ == "__main__":
    
    # program = "(8 + 2) - (3 + 4) + (5 - (6 + 7))"
    # program = "print 1 + 2 - (8 + 4)"
    # program = "x := 1 + 2 - (8 + 4); print x + x + x"
    # program = "x := 7; y := x + 2 + x; print x-y"
    # program = "x := 7; y := x; print x-y; print x + y"
    # program = "x := 7; y := 7; print x-7"
    # program = "skip;skip;skip"
    # program = "int1 := 2 - (3 + 5);int2 := 4;print int1 + int2;skip;print int1 + int2 - int1"
    # program = "x := 1; if x = 1 then print 100 else print 90 end"
    program = "x := 1; if x = 1 then print 100 else print x end"
    
    program = """
                a := 2;
                b := 3;

                if a + b = 4 or a + b = 6 then
                    print 0
                else 
                    print a + b; # 5
                    print b;     # 3
                    c := a - b + 1; # 0
                    if c = 0 then
                        print 101
                    else
                        print 102
                    end
                end;

                print 100;
                print -34;
                a := 0 - b;
                print a + ( (b - 9) + c); # -9

                skip
                
                # expected output
                # output on 110 : 5
                # output on 115 : 3
                # output on 172 : 101
                # output on 185 : 100
                # output on 191 : -34
                # output on 243 : -9

                
                
            """

    

    
    run_compiler(program)



# program = "(8 + 2) - (3 + 4) + (5 - (6 + 7))"    
# program = "skip"
# program = "false or true and not false"
#program = "3 = 1 + 3"
# program = "x := 1; if x = 1 then print 100 else print 90 end"