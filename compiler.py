import argparse
import time
from copy import deepcopy
from dataclasses import dataclass
from typing import  Union,final,Literal
from collections import Counter
from copy import deepcopy


from lark.lexer import Token
from lark.tree import Tree as ParseTree

from utils import  tree_to_string,constract_ast,is_ast_of

# recursion limit
import sys
import argparse


DEBUG = True
# DEBUG = False

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
RT3_ALC   : final = 3
RT4_ALC   : final = 4


RAX_ALC   : final = 5 # 演算結果 aexpが評価された後の値が入る

RZERO_ALC : final = 0 # 0 register


class Variables():
    """とりあえず関数、ブロックはないものとしている。
    またオフセットの限界値が256なので変数の宣言は前に固めた方がいい
    """
    
    def __init__(self,):
        self._variables : dict[str,int]= {} # 変数名 -> RBPからのオフセット
        self._offset : int = 2 # 次に書き込む場所を相対で表す *(rbp)には前のフレームのrbpが入り、*(rbp+1)には戻り先のラベルidが入るので2から始める
    
    def __contains__(self, key):
        return key in self._variables
    

    def create_variable(self,var_name:str):
        "変数領域を確保する。"
        
        if var_name in self._variables:
            return

        offset = self._offset
        self._offset += 1
        self._variables[var_name] = offset
        
        print (f"LI {RT1_ALC} {1}")
        print (f"SUB {RSP_ALC} {RT1_ALC}") # rsp -= 1
        
        return
        

    def update_variable(self,var_name:str,reg_id:RegisterID):
        """すでに確保されていることを前提して,変数の値をレジスタの値で更新する。"""
        
        if DEBUG : print (f"// update_variable called: {self._variables}")
        
        assert reg_id != RT3_ALC and reg_id != RT4_ALC , f"RT3_ALC,RT4_ALCは変数のロードに使えません。"
        

        
        if var_name in self._variables.keys():
            offset = self._variables[var_name]
            # ST
            if DEBUG: print(f"// update_variable {var_name} {reg_id} {-offset}({RBP_ALC})")
            print (f"MOV {RT3_ALC} {RBP_ALC}") # RT3_ALC = RBP_ALC
            print (f"LI {RT4_ALC} {offset}") # RT4_ALC = offset
            print (f"SUB {RT3_ALC} {RT4_ALC}") # RT3_ALC -= RT4_ALC
            
            print (f"ST {reg_id} {0}({RT3_ALC})") # *(RBP-offset) = R[reg_id]
            # print (f"ST {reg_id} {-offset}({RBP_ALC})") #既存の変数なのでrspは更新しない たぶんSTも即値マイナスでバグってそう LDと同じように書き換えたら円周率計算が動いた.
            return
        
        raise Exception(f"変数{var_name}は宣言されていません。")

    
    def load_variable(self,var_name:str,reg_id:RegisterID):
        """変数を指定されたレジスタにロードします。"""
        assert var_name in self._variables , f"変数{var_name}は宣言されていません。"
        assert reg_id != RT3_ALC and reg_id != RT4_ALC , f"RT3_ALC,RT4_ALCは変数のロードに使えません。"
        offset = self._variables[var_name]
        # LD
        # if  DEBUG : print (f"OUT {RBP_ALC}")
        
        print (f"MOV {RT3_ALC} {RBP_ALC}") # RT3_ALC = RBP_ALC
        print (f"LI {RT4_ALC} {offset}") # RT4_ALC = offset
        print (f"SUB {RT3_ALC} {RT4_ALC}") # RT3_ALC -= RT4_ALC
        
        print (f"LD {reg_id} {0}({RT3_ALC})") # R[reg_id] = *(RBP+offset)
        
        # print (f"LD {reg_id} {0-offset}({RBP_ALC})") # R[reg_id] = *(RBP+offset) # LDが即値マイナスでバグっているというissueがある。
        return
    

variables = Variables()

label_count : int = 0 # アセンブリに吐くラベルの通し番号

function_call_counter : Counter = Counter() # 関数呼び出しの回数を関数名ごとにカウントする


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
    global variables
        
    
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
        if DEBUG: print (f"//codegen_com:assign")
        
        variable_name = ast.children[0].value
        aexp : Aexp = ast.children[1]
        
        codegen_aexp(aexp)
        
        # rsp += 1
        print (f"LI {RT1_ALC} {1}")
        print (f"ADD {RSP_ALC} {RT1_ALC}")
           
        variables.update_variable(variable_name,RAX_ALC)
        
        if DEBUG: print (f"//codegen_com:assign end")
        return
    
    if data == "ifelse":
        
        if DEBUG: print (f"//codegen_com:ifelse")
         
        LABEL_COUNT_FOR_THIS_IFELSE : final = label_count
        label_count += 1 # ラベルの通し番号をここで更新しておかないと内側のラベルと被る                                                             
        
        bexp : Bexp = ast.children[0]
        com1 : Com = ast.children[1]
        com2 : Com = ast.children[2]
        
        codegen_bexp(bexp)
        
        # rsp
        print (f"LI {RT1_ALC} {1}")
        print (f"ADD {RSP_ALC} {RT1_ALC}") # rsp += 1
        
        # RAXと0を比較する
        print (f"LI {RT1_ALC} {0}")
        print (f"SUB {RT1_ALC} {RAX_ALC}") # RAX = RT1 = 0かどうかを条件コードZからもらう Z=0ならelseに飛ぶ
        print (f"BE .Lelse{LABEL_COUNT_FOR_THIS_IFELSE}")
        
        codegen_com(com1)
        
        print (f"B .Lend{LABEL_COUNT_FOR_THIS_IFELSE}")
        
        
        print (f".Lelse{LABEL_COUNT_FOR_THIS_IFELSE}")
        codegen_com(com2)
        print (f".Lend{LABEL_COUNT_FOR_THIS_IFELSE}")
        
  
        
        if DEBUG: print (f"//codegen_com:ifelse end")
        
        
        return
    
    if data == "while":
        
        if DEBUG: print (f"//codegen_com:while")
        
        LABEL_COUNT_FOR_THIS_WHILE : final = label_count
        label_count += 1 # ラベルの通し番号をここで更新しておかないと内側のラベルと被る
        
        bexp : Bexp = ast.children[0]
        com : Com = ast.children[1]
        
        print (f".Lbegin{LABEL_COUNT_FOR_THIS_WHILE}")
        
        codegen_bexp(bexp)
        
        # rsp
        print (f"LI {RT1_ALC} {1}")
        print (f"ADD {RSP_ALC} {RT1_ALC}") # rsp += 1
        
        # RAXと0を比較する
        print (f"LI {RT1_ALC} {0}")
        print (f"SUB {RT1_ALC} {RAX_ALC}") # RAX = RT1 = 0かどうかを条件コードZからもらう Z=0ならendに飛ぶ
        print (f"BE .Lend{LABEL_COUNT_FOR_THIS_WHILE}")
        
        codegen_com(com)
        
        print (f"B .Lbegin{LABEL_COUNT_FOR_THIS_WHILE}")
        print (f".Lend{LABEL_COUNT_FOR_THIS_WHILE}")
        
        if DEBUG: 
            print (f"//codegen_com:while end")
        
        return

        
    
    if data == "print":
        if DEBUG : print (f"//codegen_com:print")
        aexp : Aexp = ast.children[0]
        codegen_aexp(aexp)
        print(f"OUT {RAX_ALC} // print {aexp}")
        
        # rsp
        print (f"LI {RT1_ALC} {1}")
        print (f"ADD {RSP_ALC} {RT1_ALC}") # rsp += 1
        
        if DEBUG : print (f"//codegen_com:print end")
        return
    
    
    if data == "def":
        
        global function_call_counter

        function_name = ast.children[0].value
        arg_names : list[str] = [child.value for child in ast.children[1:-2]]
        arg_count = len(arg_names)
        com : Com = ast.children[-2]
        ret_aexp : Aexp = ast.children[-1]
        
        function_call_count = function_call_counter[function_name]
        
        label_count_for_detour = label_count
        label_count += 1
        
        # 回り道
        print (f"B .definition_{function_name}:{label_count_for_detour}")
        
        function_start_labels = [ f"call_{function_name}_begin:{i}" for i in range(1,function_call_count+1)]
        
        for label in function_start_labels:
            print (f".{label}")
        
        local_variables_name  = extract_unique_var(ast)
        local_variables_name = deepcopy(local_variables_name + arg_names)
        local_variables_name = list(set(local_variables_name))
        # 辞書順にソート(ソートしないと実行するたびに順番変わるっぽい)
        local_variables_name.sort()
        # local variablesからarg_namesを除く
        for arg_name in arg_names:
            local_variables_name.remove(arg_name)
        
        #最初に引数を持ってくる。
        local_variables_name = deepcopy( arg_names + local_variables_name)
        
        outer_variables = deepcopy(variables)
        local_variable = Variables()
        
        # 変数領域の確保
        for local_variable_name in local_variables_name:
            if DEBUG :print ("//",local_variable_name)
            if DEBUG :print ("//",local_variable._variables)
            local_variable.create_variable(local_variable_name)

        
        # 関数の引数を変数領域にコピー 引数は先頭から奥に積まれている
        for i in range(arg_count):

            print ("//",local_variable._variables)
            offset = -2 - i # まだ変数への書き込みをしていないのでcallする前に積んだ引数が残っているはず TODO これが嘘で変数領域にコピーしている最中に引数を書き換えられることがあるのか
            print (f"LI {RT3_ALC} {offset}")
            print (f"MOV {RT2_ALC} {RBP_ALC}")
            print (f"ADD {RT2_ALC} {RT3_ALC}")
            
            print (f"LD {RT1_ALC} {0}({RT2_ALC})")

            # print (f"LD {RT1_ALC} {offset}({RBP_ALC})") # TODO 負の即値をいれるとバグる。issue
            local_variable.update_variable(arg_names[i],RT1_ALC)
        
        variables = deepcopy(local_variable) # 中身のコンパイルはローカル変数のみ見えるようにする
        
        codegen_com(com)
        
        codegen_aexp(ret_aexp)
        

        
        # この段階でスタックのトップとRAXの内容は一致しているはず。
        if DEBUG:
            print (f"LD {RT1_ALC} {1}({RSP_ALC})") # ret_v = *(rsp+1)
            print (f"CMP {RT1_ALC} {RAX_ALC}")
            print (f"BE .Label_DEBUG_RAX_{function_name}_end:{label_count}")
            print (f"LI {RT1_ALC} {1}")
            print (f"OUT {RZERO_ALC}")
            print (f"HLT")
            print (f".Label_DEBUG_RAX_{function_name}_end:{label_count}")
        
        # rsp codegenは勝手にrspを更新してくれるのでここでは更新しない。またRAXに返り値がはいってる。
        # print (f"LI {RT1_ALC} {1}")
        # print (f"ADD {RSP_ALC} {RT1_ALC}") # rsp += 1
        
        #今、rsp = rbp + 1 + arg_count + 1 + 1のはずである。 rbp id arg1 arg2 ... argn ret_v 
        
        variables = deepcopy(outer_variables) # 以降のコンパイルでは外側の変数が見えるようにする
        
        
        # この段階でスタックには返り先rbp,返り先ラベルid,返り値が積まれている.またRAXには返り値が入っている。
        # RT1にidを、RT2にrbpを入れる
        print (f"MOV {RT3_ALC} {RBP_ALC}")
        print (f"LI {RT4_ALC} {1}")
        print (f"SUB {RT3_ALC} {RT4_ALC}")
        print (f"LD {RT1_ALC} {0}({RT3_ALC})")
        # print (f"LD {RT1_ALC} {-1}({RBP_ALC})") # TODO 負の即値をいれるとバグる。issue
        print (f"LD {RT2_ALC} {0}({RBP_ALC})")
        
        # RAXをRBPが入っていたところに入れる RBPはRT2に退避済み
        print (f"ST {RAX_ALC} {0}({RBP_ALC})")
        
        
        # これから戻るだけなのでrbpを復元する
        print (f"MOV {RBP_ALC} {RT2_ALC}")
        # rspを更新
        if DEBUG:
            print (f"// rspを更新")
            print (f"// local_variables_name:{local_variables_name}",len (local_variables_name))
        # assert local_variables_names are unique
        assert len(local_variables_name) == len(set(local_variables_name))
        print (f"LI {RT4_ALC} {2 + len(local_variables_name)}")
        print (f"ADD {RSP_ALC} {RT4_ALC}")
        
        
        # idを参照して戻り先ラベルにジャンプ 関数ごとにおよそ128種類の戻り先を区別できる
        for i in range(1,function_call_count+1):
            print (f"LI {RT2_ALC} {i}")
            if DEBUG: print (f"OUT {RT1_ALC}","// debug return id")
            if DEBUG: print (f"OUT {RT1_ALC}","// debug return id")
            if DEBUG: print (f"OUT {RT1_ALC}","// debug return id")
            print (f"CMP {RT1_ALC} {RT2_ALC}")
            print (f"BE .call_{function_name}_end:{i}")
        
        print (f"OUT {RZERO_ALC}", "// something wrong. can't find return label")
        print ("HLT")
    
        print (f".definition_{function_name}:{label_count_for_detour}")
        
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
        if DEBUG : print (f"//codegen_aexp:var start")
        var_name : str = ast.value
        assert isinstance(var_name,str)
        variables.load_variable(var_name,RAX_ALC)
        print (f"ST {RAX_ALC} {0}({RSP_ALC})") # *(rsp+0) = RAX
        print (f"LI {RT1_ALC} {1}")
        print (f"SUB {RSP_ALC} {RT1_ALC}") # rsp -= 1
        if DEBUG : print (f"//codegen_aexp:var end")
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
    
    if data == "input":
        print (f"IN {RAX_ALC} {0}") # RAX = input()
        print (f"ST {RAX_ALC} {0}({RSP_ALC})")
        print (f"LI {RT1_ALC} {1}")
        print (f"SUB {RSP_ALC} {RT1_ALC}") # rsp -= 1
        return
    
    if data == "call":
        
        global label_count
        
        if DEBUG: print (f"//codegen_aexp:call start")
        
        if DEBUG : print (f"OUT {RSP_ALC}")
        if DEBUG : print (f"OUT {RSP_ALC}")
        
        # 今のrbpをpush
        print (f"ST {RBP_ALC} {0}({RSP_ALC})")
        print (f"LI {RT1_ALC} {1}")
        print (f"SUB {RSP_ALC} {RT1_ALC}") # rsp -= 1
        
        # idをpush
        function_id : int = ast.call_id
        
        print ("// call id",function_id)


        print (f"LI {RT1_ALC} {function_id}")
        print (f"ST {RT1_ALC} {0}({RSP_ALC})")
        
        if DEBUG: print (f"OUT {RT1_ALC}","// debug call id")
        
        
        print (f"LI {RT1_ALC} {1}")
        print (f"SUB {RSP_ALC} {RT1_ALC}") # rsp -= 1
        
        function_name : str = ast.children[0].value
        arg_aexprs = ast.children[1:]
        arg_count = len(arg_aexprs)
        
        if DEBUG : print (f"//codegen_aexp:call:arg_count",arg_count)
        
        # 引数の値を全部評価してpush
        for child in arg_aexprs:

            codegen_aexp(child)
            # codegenすれば勝手にpushされるので以下は不要
            # print (f"ST {RAX_ALC} {0}({RSP_ALC})")
            # print (f"LI {RT1_ALC} {1}")
            # print (f"SUB {RSP_ALC} {RT1_ALC}") # rsp -= 1
        
        # rbpの更新は引数を評価してからしかできない TODO ここのrbpの更新がバグってる
        print (f"MOV {RBP_ALC} {RSP_ALC}") # rbp = rsp
        print (f"LI {RT1_ALC} {arg_count + 1 + 1 + 0}") # 引数の数 + 戻りidの分 + rbpの分
        print (f"ADD {RBP_ALC} {RT1_ALC}") 
        
        # rbpとrspの関係をテストする
        if DEBUG : 
        
            label_count += 1
            print (f"MOV {RT1_ALC} {RBP_ALC}")
            print (f"SUB {RT1_ALC} {RSP_ALC}")
            print (f"LI {RT2_ALC}  {arg_count + 1 + 1 + 0}")
            print (f"CMP {RT1_ALC} {RT2_ALC}")
            print (f"BE .call_DEBUG_rbprsp{function_name}_end:{label_count}")
            print (f"OUT {RZERO_ALC}")
            print (f"OUT {RT1_ALC}")
            print (f"OUT {RT2_ALC}")
            print (f"LI {RT1_ALC} {arg_count}")
            print (f"OUT {RT1_ALC}")
            print (f"HLT")
            print (f".call_DEBUG_rbprsp{function_name}_end:{label_count}")
            
            pass
        
        if DEBUG :
            print (f"OUT {RT1_ALC}","// debug rbp")
            print (f"OUT {RBP_ALC}","// debug rbp")
            print (f"OUT {RSP_ALC}","// debug rsp")
            
            # print (f"LD {RT1_ALC} {3}({RBP_ALC})")
            # print (f"OUT {RT1_ALC}","// debug rbp[0]")
            
            # print (f"LD {RT1_ALC} {4}({RBP_ALC})") #なぜか無引数だとここが戻りrbpになってる。
            # print (f"OUT {RT1_ALC}","// debug rbp[0]")
        
        # 関数呼び出し
        print (f"B .call_{function_name}_begin") # 関数の先頭に飛ぶ
        

        print (f".call_{function_name}_end:{function_id}") # 関数から戻ってくる用
        
        if DEBUG : print (f"//end of call {function_name}")
        
        if DEBUG : print (f"OUT {RAX_ALC}","// debug call return value")
        
        # 戻り値をpush
        print (f"ST {RAX_ALC} {0}({RSP_ALC})")
        print (f"LI {RT1_ALC} {1}")
        print (f"SUB {RSP_ALC} {RT1_ALC}") # rsp -= 1

        
        return
        
        # raise NotImplementedError("call")
    
    
    raise Exception(f"codegen_aexp cannot handle {data}")


def codegen_bexp(ast:Bexp):
    """インタプリタのときとは違って、コンパイラの方ではAexpと同じように整数が返ってくると考えてコンパイルする. true=1,false=0として扱う.
    """
    global label_count
    
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
        
        label_name = f"eq_label_{label_count}"
        label_count += 1
        
        print (f"LD {RT1_ALC} {2}({RSP_ALC})") # RT1 = *(rsp+2)
        print (f"LD {RT2_ALC} {1}({RSP_ALC})") # RT2 = *(rsp+1)
        
        print (f"LI {RAX_ALC} {1}") # RAX = 1
        
        print (f"CMP {RT1_ALC} {RT2_ALC}") 
        print (f"BE .{label_name}") # RT1 == RT2ならばlabel_nameに飛ぶ
        
        print (f"LI {RAX_ALC} {0}") # RT1 != RT2ならばRAX = 0
        
        print (f".{label_name}")
        
        
        
        print (f"ST {RAX_ALC} {2}({RSP_ALC})") # *(rsp+2) = RAX
        print (f"LI {RT1_ALC} {1}")
        print (f"ADD {RSP_ALC} {RT1_ALC}") # rsp += 1
        
        return
        

    
    if data == "lt":
        
        aexp1 = ast.children[0]
        aexp2 = ast.children[1]
        
        codegen_aexp(aexp1)
        codegen_aexp(aexp2)
        
        label_name = f"lt_label_{label_count}"
        label_count += 1
        
        print (f"LD {RT1_ALC} {2}({RSP_ALC})") # RT1 = *(rsp+2)
        print (f"LD {RT2_ALC} {1}({RSP_ALC})") # RT2 = *(rsp+1)
        
        print (f"LI {RAX_ALC} {1}") # RAX = 1
        
        print (f"CMP {RT1_ALC} {RT2_ALC}")
        print (f"BLT .{label_name}") # RAX < RT1なら飛ぶ
        
        print (f"LI {RAX_ALC} {0}") # RAX = 0
        
        print (f".{label_name}")
        
        print (f"ST {RAX_ALC} {2}({RSP_ALC})") # *(rsp+2) = RAX
        print (f"LI {RT1_ALC} {1}")
        print (f"ADD {RSP_ALC} {RT1_ALC}") # rsp += 1
        
        return
        
        
    
    if data == "le": # aexp1 <= aexp2 
        
        aexp1 = ast.children[0]
        aexp2 = ast.children[1]
        
        codegen_aexp(aexp1)
        codegen_aexp(aexp2)
        
        label_name = f"le_label_{label_count}"
        label_count += 1
        
        print (f"LD {RT1_ALC} {2}({RSP_ALC})") # RT1 = *(rsp+2)
        print (f"LD {RT2_ALC} {1}({RSP_ALC})") # RT2 = *(rsp+1)
        
        print (f"LI {RAX_ALC} {1}") # RAX = 1
        
        print (f"CMP {RT1_ALC} {RT2_ALC}")
        print (f"BLE .{label_name}") # RAX <= RT1なら飛ぶ
        
        print (f"LI {RAX_ALC} {0}") # RAX = 0

        
        print ("." + label_name)
        
        
        print (f"ST {RAX_ALC} {2}({RSP_ALC})") # *(rsp+2) = RAX
        print (f"LI {RT1_ALC} {1}")
        print (f"ADD {RSP_ALC} {RT1_ALC}") # rsp += 1
        
        return
        
    
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
        print (f"ST {RAX_ALC} {-1}({RSP_ALC})") # *(rsp-1) = RAX
        
        # pop 1 push 1なのでrspは変わらない
        
        return
    
    raise Exception(f"codegen_bexp cannot handle {data}")





def init_register():
    print (f"LI {RBP_ALC} {1}")
    print (f"SLL {RBP_ALC} {12}") # RBP = 1024,2048,4096
    print (f"MOV {RSP_ALC} {RBP_ALC}") # RSP = RBP
    print (f"LI {RT1_ALC} {2}")
    print (f"SUB {RSP_ALC} {RT1_ALC}") # RSP = RSP - 2
    return


def count_function_call_and_add_id(ast):
    """関数呼び出しを数えながらidをつける"""
    global function_call_counter # Counter object
    
    
    if isinstance(ast,Token):
        return
    
    if ast.data == "call":
        function_name = ast.children[0].value
        function_call_counter[function_name] += 1
        ast.call_id = function_call_counter[function_name]
        return
    
    for child in ast.children:
        count_function_call_and_add_id(child)

    return


def extract_unique_var(ast) -> list[str]:
    if isinstance(ast,Token):
            return []
    
    if ast.data == "assign":
        var = ast.children[0].value
        return [var]
    
    
    res = []
    for child in ast.children:
        res += extract_unique_var(child)
    
    # uniqueにする
    res = list(set(res))
    # sortする
    res.sort()
    return res

def run_compiler(program:str):
    tree = constract_ast(program,"com", "syntax_for_compiler.lark")
    
    init_register()
    
    # 変数のメモリを全て確保する
    

    
    
    
    unique_var = extract_unique_var(tree)
    
    # print (unique_var)
    
    for var in unique_var:
        variables.create_variable(var)
    
    count_function_call_and_add_id(tree)
    
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
    program = "x := 1; if x <= 1 then print 100 else print x end"
    
    program = """
            # this code calculates GCD of 2 inputs. a should be larger or equal to b.
            
            a := <input>; 
            b := <input>;
            i := 0;
            
            while not a = b do
                
                if a <= b then
                    tmp := a;
                    a := b;
                    b := tmp
                else 
                    skip
                end;
                
                a := a - b;
                i := i + 1
            end;
            
            print i;
            print a
            
            """
    
    program = """
            # this code calculates GCD of 2 inputs. a should be larger or equal to b.
            
            a := <input>; 
            b := <input>;
            i := 0;
            
            while not a = b do
                
                if a <= b then
                    if i <= 5 then
                        dummy := 1 + 2 + 3 -1 - 2 - 3;
                        dummy := 1 + 2 + 3 -1 - 2 - 3;
                        dummy := 1 + 2 + 3 -1 - 2 - 3;
                        dummy := 1 + 2 + 3 -1 - 2 - 3;
                        dummy := 1 + 2 + 3 -1 - 2 - 3;
                        dummy := 57;
                        skip
                    else 
                        dummy := 1 + 2 + 3 -1 - 2 - 3;
                        dummy := 1 + 2 + 3 -1 - 2 - 3;
                        dummy := 1 + 2 + 3 -1 - 2 - 3;
                        dummy := 89;
                        skip
                    end; 
                    tmp := a;
                    a := b;
                    b := tmp
                else 
                    skip
                end;
                
                a := a - b;
                i := i + 1
            end;
            
            print i;
            print a
            
            """

    # program = """
        
    #     while true do print 6 end
    #     """
    
    program = """
    
    n := <input>;
    i := n - 1;
    print -1;
    while 2 <= i do
        r := n;
        while i <= r do
            r := r - i
        end;
        if r = 0 then
            print i
        else
            skip
        end;
        i := i - 1
    end
    
    """
    
    # use argparse to get the file name
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="input file name")
    args = parser.parse_args()
    
    # read the file
    with open(args.file, "r") as f:
        program = f.read()
    

    run_compiler(program)



# program = "(8 + 2) - (3 + 4) + (5 - (6 + 7))"    
# program = "skip"
# program = "false or true and not false"
#program = "3 = 1 + 3"
# program = "x := 1; if x = 1 then print 100 else print 90 end"


# program = """
#             a := <input>;
#             b := 3;

#             if a + b = 4 or a + b = 6 then
#                 print 0
#             else 
#                 print a + b; # 5
#                 print b;     # 3
#                 c := a - b + 1; # 0
#                 if c = 0 then
#                     print 101
#                 else
#                     print 102
#                 end
#             end;

#             print 100;
#             print -34;
#             a := 0 - b;
#             print a + ( (b - 9) + c); # -9

#             skip
            
#             # expected output if input is 2
#             # output on 110 : 5
#             # output on 115 : 3
#             # output on 172 : 101
#             # output on 185 : 100
#             # output on 191 : -34
#             # output on 243 : -9

            
            
#         """

# program = """
#         n := <input>;
#         i := 0;
#         sum := 0;
        
#         while not i = n + 1 do
#             sum := sum + i;
#             i := i + 1;
            
#             if i = 5 then
#                 print sum
#             else
#                 skip;
#                 skip;
#                 skip
#             end
#         end;
        
#         print sum
        
#         """


    # program = """
    #         # this code calculates GCD of 2 inputs. a should be larger or equal to b.
            
    #         a := <input>; 
    #         b := <input>;
    #         i := 0;
            
    #         while not a = b do
                
    #             if a <= b then
    #                 if i <= 50 then
    #                     dummy := 1 + 2 + 3 -1 - 2 - 3;
    #                     dummy := 1 + 2 + 3 -1 - 2 - 3;
    #                     dummy := 1 + 2 + 3 -1 - 2 - 3;
    #                     dummy := 1 + 2 + 3 -1 - 2 - 3;
    #                     dummy := 1 + 2 + 3 -1 - 2 - 3;
    #                     dummy := 57;
    #                     print dummy
    #                 else 
    #                     dummy := 1 + 2 + 3 -1 - 2 - 3;
    #                     dummy := 1 + 2 + 3 -1 - 2 - 3;
    #                     dummy := 1 + 2 + 3 -1 - 2 - 3;
    #                     dummy := -57;
    #                     print dummy
    #                 end; 
    #                 tmp := a;
    #                 a := b;
    #                 b := tmp
    #             else 
    #                 skip
    #             end;
                
    #             a := a - b;
    #             i := i + 1
    #         end;
            
    #         print i;
    #         print a
            
    #         """
    
    
