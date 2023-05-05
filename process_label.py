import argparse
import re




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
    
    # print (code_with_label)
    
    # remove all the comments first 
    # comments start with "//" and end with "\n"
    code_with_label = re.sub(r"//.*\n", "\n", code_with_label)
    
    # print (code_with_label)
    
    # separate each line
    instractions = code_with_label.split("\n")
    
    # .から始まるラベルで連続する行はまとめて空白で区切って結合する
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
    
    # print (67 * "-")
    
    # print (code_with_label)
    
    def find_target_line(label_name:str) -> int:
        assert label_name.count("@") == 0
        assert label_name.count(".") == 0
        target = "@" + label_name
        for target_line in range(len(instractions_merged)):
            if instractions_merged[target_line].count(target) > 0:
                return target_line
        # unreachable error
        assert False, "label " + label_name + " is not found"
    
    for pc in range(len(instractions_merged)):
        
        # .が入っている個数を数える
        dot_count = instractions_merged[pc].count(".")
        if dot_count == 0:
            continue
        assert dot_count == 1
        
        label_name = instractions_merged[pc].split(".")[1]
        
        target_line = find_target_line(label_name)
        
        d = target_line - (pc + 1)
        instractions_merged[pc] = instractions_merged[pc].replace(f".{label_name}", f"{d}")
        instractions_merged[pc] += " // " + "might jump to " + label_name
        
        if d < - 2 ** 7 or d > 2 ** 7 - 1:
            raise Exception(f"jump distance is too far... displacement = {d} in binary = {bin(d)}")
    
    # print (67 * "-")
    
    code_without_label = "\n".join(instractions_merged)
    
    # print (code_without_label)
    
    # save to file
    with open(args.output, "w") as f:
        f.write(code_without_label)
 
    