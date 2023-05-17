import argparse
from typing import Union
import re

DISPLACEMENT_MIN = -128
DISPLACEMENT_MAX = 127

#  unique label name generator
class LabelGenerator:
    def __init__(self):
        self.label_count = 0
        self.label_prefix = "label_unique_"
    
    def generate(self) -> str:
        self.label_count += 1
        return self.label_prefix + str(self.label_count)
    
    def __repr__(self) -> str:
        return self.label_prefix + str(self.label_count)
    
    def __str__(self) -> str:
        return self.label_prefix + str(self.label_count)
    

label_generator = LabelGenerator()

def preprocess_raw_code(code_with_label :str) -> str:
    """
    コンパイラの吐き出したコードに以下のような前処理を施し、その結果を返す。
    全てのもともとのコメントを削除する。
    出発元ラベルは.から始まっておりB .labelのように書かれている。
    到達先ラベルは@から始まっており、instraction ... // @label1 @label2 のように書かれている。
    """
    
    # remove all the comments first 
    # comments start with "//" and end with "\n"
    code_with_label = re.sub(r"//.*\n", "\n", code_with_label)
    
    # print (code_with_label)
    
    # separate each line
    instractions = code_with_label.split("\n")
    
    # .から始まるラベルで連続する行はまとめて空白で区切って結合する ラベルが連続する場合は同じ行にまとめてしまいたい
    instractions_merged : list[str] = []

    for i in range(len(instractions)):
        if len(instractions[i]) == 0:
            continue
        
        if instractions[i][0] == ".":
            if instractions_merged[-1][0] == ".":
                instractions_merged[-1] += " " + instractions[i]
                continue
            else :
                instractions_merged.append(instractions[i])
                continue
        
        instractions_merged.append(instractions[i])
    
    # ジャンプ元とジャンプ先の区別をつけやすくするためにジャンプ先の.を@に置き換える
    for i in range(len(instractions_merged)):
        if instractions_merged[i][0] == ".":
            instractions_merged[i] = instractions_merged[i].replace(".", "@")
    
    instractions_merged.append("HLT")
    
    # ここまでジャンプ先ラベルたちは一行を占有していたが、次の命令の後ろにコメントとして書くことにする
    for i in range(len(instractions_merged)):
        if instractions_merged[i][0] == "@":
            assert i+1 < len(instractions_merged)
            instractions_merged[i+1] = instractions_merged[i+1] + " // " + instractions_merged[i]
            instractions_merged[i] = "moved to comment of next line"
    
    instractions_merged = [line for line in instractions_merged if line != "moved to comment of next line"]
    
    code_with_label = "\n".join(instractions_merged)
    
    
    return code_with_label



def find_destination_line(code : str, label_name : str) -> int:
    """前処理済みのコードから、ラベル名を指定して@label_nameの行番号を返す
    """
    
    instractions = code.split("\n")
    
    # assert do not appear same label name twice
    label_name_set = set()
    for pc in range(len(instractions)):
        if "." + label_name in instractions[pc]:
            label_name_set.add(label_name)
    
    if len(label_name_set) > 1:
        raise Exception(f"same label name {label_name} appears twice")
    
    for pc in range (len(instractions)):
        if "@" + label_name in instractions[pc]:
            return pc
    
    raise Exception(f"cannot find destination label {label_name}")


def detect_too_far_labels(code : str) -> Union[str, None]:
    """かけ離れているラベルの名前を返す。ない時はNoneでNoneが返ってこればラベル名を相対アドレスに書き換える工程へ進む。
    ラベルは負の方向にはDISPLACEMENT_MIN,正の方向にはDISPLACEMENT_MAXまで飛べることに注意。
    """
    
    all_label_appearence : list[tuple[str,int]] = []
    
    instractions = code.split("\n")
    
    for pc in range(len(instractions)): # extract from .labelname
        if "." in instractions[pc]:
            label_name = instractions[pc].split(".")[1].split(" ")[0].split(r'/')[0]
            all_label_appearence.append( (label_name, pc) )
            
    for label_name, pc in all_label_appearence:
        destination_line = find_destination_line(code, label_name)
        d = destination_line - (pc + 1)
        
        if d < DISPLACEMENT_MIN or d > DISPLACEMENT_MAX:
            return label_name
    
    return None
    


def insert_jump_helper(code : str, label_name : str,) -> str:
    """
    遠すぎるラベルのちょうど真ん中にジャンプするためのラベルを挿入する。
    """
    
    line_from = -1
    line_to = -1
    
    instractions = code.split("\n")
    for pc in range(len(instractions)):
        if "@" + label_name in instractions[pc]:
            line_to = pc
        if "." + label_name in instractions[pc]:
            line_from = pc
    
    print (f"line_from = {line_from}, line_to = {line_to}, label_name = {label_name}")
    
    assert line_from != -1 and line_to != -1
    # assert abs (line_from - line_to) > 100, "よっぽど入り組んでない限り100行以上離れているはず"
    
    mid = line_from + (line_to - line_from) // 2
    altnative_label = label_generator.generate() + "_altnative"
    
    # fromの方を新しいラベル名に置き換えて中間行にも新しいラベル名を挿入する
    # その後、toの方に元のラベル名を使って無条件ジャンプするようにする
    instractions[line_from] = instractions[line_from].replace("." + label_name, "." + altnative_label)
    
    # print (f"changed line {line_from} to {instractions[line_from]}")
    
    
    label_for_detour : str  = label_generator.generate() + "_for_detour"
    
    # mid 行目に　以下のようなコードを挿入する。
    
    """
    もともと書かれていたコード(mid-1行目)
    B .label_for_detour
    B .label_name // @altnative_label
    もともと書かれていたコード // @label_for_detour
    """
    
    new_instractions =  instractions[:mid] + \
                        [f"B .{label_for_detour}", f"B .{label_name} // @{altnative_label}"] + \
                        [ instractions[mid] + f" // @{label_for_detour}"] + \
                        instractions[mid+1:]
    
    new_code = "\n".join(new_instractions)
    
    return new_code
    
    


def replace_label_with_displacement(code : str, label_name : str) -> str:
    """ラベル名を相対アドレスに書き換える
    """
    
    instractions = code.split("\n")
    
    destination_line = find_destination_line(code, label_name)
    

    
    line_from = -1
    for pc in range(len(instractions)):
        if "." + label_name in instractions[pc]:
            # assert line_from == -1, f"同じラベル名(from: {label_name})が複数回出現している...?コンパイラでは同じラベル名を使っていない。"
            line_from = pc
    
    displacement = 10 ** 18
    for pc in range(len(instractions)):
        if "@" + label_name in instractions[pc]:
            assert displacement == 10 ** 18, f"同じラベル名(to: {label_name})が複数回出現している。行先のラベルが二つ以上あるのはおかしい。"   
            displacement = destination_line - (line_from + 1)
    
    instractions[line_from] = instractions[line_from].replace("." + label_name, f"{displacement}")
    new_code = "\n".join(instractions)
    
    return new_code


if __name__ == "__main__":
    
    # receive target file name
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="target file name")
    parser.add_argument("--output", help="output file name")
    args = parser.parse_args()

    if args.input is None or args.output is None:
        print ("Please specify target file name")
        exit(1)
    
    # read target file
    code_with_label = ""
    with open(args.input, "r") as f:
        code_with_label = f.read()
    
    
    code_with_label = preprocess_raw_code(code_with_label)
    
    
    # 相対ジャンプができるように補助ラベルを挿入する
    while True:
        label_name = detect_too_far_labels(code_with_label)
        if label_name is None:
            break
        code_with_label = insert_jump_helper(code_with_label, label_name)

    print (code_with_label)
    # 最後に全てのラベルをdisplacementに置き換えて相対ジャンプを可能にする。
    
    label_names = []
    instractions = code_with_label.split("\n")
    
    for pc in range(len(instractions)):
        if "." in instractions[pc]:
            label_name = instractions[pc].split(".")[1].split(" ")[0].split(r'/')[0]
            label_names.append(label_name)
    
    # print (label_names)
    
    for label_name in label_names:
        code_with_label = replace_label_with_displacement(code_with_label, label_name)
    
    assert code_with_label.count(".") == 0, "there are still labels...?"
    code_without_label = code_with_label
    
    # save to file
    with open(args.output, "w") as f:
        f.write(code_without_label)
