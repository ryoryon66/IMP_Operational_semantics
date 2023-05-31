from typing import List,Final
import argparse

from prettytable import DEFAULT



DEFAULT_MUSIC_START_ADDRSS : Final = 3000
MUSIC_FILE_PATH : Final = "music_files/" + "music.txt"
PROGRAM_PATH : Final = "../simple_asm.txt"

argparser = argparse.ArgumentParser()
argparser.add_argument("--input", "-i", type=str, default=PROGRAM_PATH)
argparser.add_argument("--output", "-o", type=str, default=PROGRAM_PATH)
argparser.add_argument("--music", "-m", type=str, default=MUSIC_FILE_PATH)
argparser.add_argument("--start_address", "-s", type=int, default=DEFAULT_MUSIC_START_ADDRSS)

args = argparser.parse_args()

MUSIC_START_ADDRSS : Final = args.start_address

program : str = ""

with open(args.input, "r") as f:
    program = f.read()

program_list : List[str] = program.split("\n")

#音楽の書き込み場所まで適当な値で埋める。
assert len(program_list) < MUSIC_START_ADDRSS, f"プログラムの長さが長すぎます。音楽の書き込み場所を変更してください。もしくは他のデータが書き込まれています。"
while len(program_list) < MUSIC_START_ADDRSS:
    program_list.append("0")

def scale_to_int(scale : str) -> int:
    
    assert len(scale) >= 2 or scale == "0", f"音階は2文字以上で指定してください。エラー:{scale}"
    
    #下位3ビットはオクターブ用、上位13ビットはドレミ用
    doremi_map = {
        "ど"     : 0b0000_0000_0000_1000,
        "ど＃"   : 0b0000_0000_0001_0000,
        "れ♭"   : 0b0000_0000_0001_0000,
        "れ"     : 0b0000_0000_0010_0000,
        "れ＃"   : 0b0000_0000_0100_0000,
        "み♭"   : 0b0000_0000_0100_0000,
        "み"     : 0b0000_0000_1000_0000,
        "ふぁ"   : 0b0000_0001_0000_0000,
        "ふぁ＃" : 0b0000_0010_0000_0000,
        "そ♭"   : 0b0000_0010_0000_0000,
        "そ"     : 0b0000_0100_0000_0000,
        "そ＃"   : 0b0000_1000_0000_0000,
        "ら♭"   : 0b0000_1000_0000_0000,
        "ら"     : 0b0001_0000_0000_0000,
        "ら＃"   : 0b0010_0000_0000_0000,
        "し♭"   : 0b0010_0000_0000_0000,
        "し"     : 0b0100_0000_0000_0000,
        
        "ド"      : 0b0000_0000_0000_1000,
        "ド＃"    : 0b0000_0000_0001_0000,
        "レ♭"    : 0b0000_0000_0001_0000,
        "レ"      : 0b0000_0000_0010_0000,
        "レ＃"    : 0b0000_0000_0100_0000,
        "ミ♭"    : 0b0000_0000_0100_0000,
        "ミ"      : 0b0000_0000_1000_0000,
        "ファ"    : 0b0000_0001_0000_0000,
        "ファ＃"  : 0b0000_0010_0000_0000,
        "ソ♭"    : 0b0000_0010_0000_0000,
        "ソ"     : 0b0000_0100_0000_0000,
        "ソ＃"    : 0b0000_1000_0000_0000,
        "ラ♭"    : 0b0000_1000_0000_0000,
        "ラ"     : 0b0001_0000_0000_0000,
        "ラ＃"   : 0b0010_0000_0000_0000,
        "シ♭"   : 0b0010_0000_0000_0000,
        "シ"     : 0b0100_0000_0000_0000,
    }
    
    #　下位3ビットはオクターブ用、上位13ビットはドレミ用
    octave_map = {
        "0" : 0b0000_0000_0000_0000,
        "1" : 0b0000_0000_0000_0001,
        "2" : 0b0000_0000_0000_0010,
        "3" : 0b0000_0000_0000_0011,
        "4" : 0b0000_0000_0000_0100,
        "5" : 0b0000_0000_0000_0101,
        "6" : 0b0000_0000_0000_0110,
        "7" : 0b0000_0000_0000_0111,
    }
    
    # print (scale)
    
    # 休符の場合
    if scale == "0":
        return 0b0000_0000_0000_0001
    
    # ら1 ら#2　ら##2などの形式を仮定する。 
    assert not set(["(",")","（","）"]) & set(scale), f"音階に括弧は使用できません。エラー:{scale}"
    octave = scale[-1]
    doremi = scale[:-1]
    
    
    

    
    # 半角の # は全角に変換する。
    doremi = doremi.replace("#", "＃")
    
    # print (doremi)
    # print (octave)

    
    #オクターブが全角の場合は半角に変換する。
    if octave == "０":
        octave = "0"
    elif octave == "１":
        octave = "1"
    elif octave == "２":
        octave = "2"
    elif octave == "３":
        octave = "3"
    elif octave == "４":
        octave = "4"
    elif octave == "５":
        octave = "5"
    elif octave == "６":
        octave = "6"
    elif octave == "７":
        octave = "7"
    elif octave in ["0","1","2","3","4","5","6","7"]:
        pass
    else:
        assert octave.isdigit(), f"オクターブは半角数字で指定してください。エラー:{scale}"
        raise ValueError("オクターブは0,1,2のいずれかを指定してください。")
    
    
    
    return (doremi_map[doremi] | octave_map[octave])


notes : str = ""

with open(args.music, "r") as f:
    notes = f.read()


def sum_digit_in_paren_per_line(line: str) -> int :
    
    notes = line.split(" ")
    notes = list(filter(lambda x: x != "", notes))
    
    sound_length_sum = 0
    
    for note in notes:
        if "(" in note:
            sound_length_sum += int(note[note.find("(")+1:note.find(")")])
    
    
    return sound_length_sum
##音の数があわなかったので、デバッグ用に出力した。
note_count = 0
for i,line in enumerate(notes.split("\n")):
    
    note_count += sum_digit_in_paren_per_line(line)


    if sum_digit_in_paren_per_line(line) != 8 and sum_digit_in_paren_per_line(line) != 4:
        print ("line : ", i)
        print (line)
        print (sum_digit_in_paren_per_line(line))
        print ("______________________________________________________")

print ("note_count : ", note_count)

# 改行、半角空白、全角空白で区切る。
# 半角空白、全角空白を改行に変換する。
notes = notes.replace(" ", "\n")






notes = notes.replace("　", "\n")
# 空行を削除する。

notes_list : List[str] = notes.split("\n")
notes_list = list(filter(lambda x: x != "", notes_list))

for note in notes_list:
    
    note = note.replace("（", "(")
    note = note.replace("）", ")")
    
    sound_length = 1
    # print (note)
    
    if "(" in notes:
        # ()内の数字を取り出す。
        sound_length = int(note[note.find("(")+1:note.find(")")])
        note = note[:note.find("(")]
    

    
    # 音階を整数に変換
    for i in range(sound_length):
        program_list.append(str(scale_to_int(note)))

program_list.append("0") #null文字を追加する。

program = "\n".join(program_list)

with open(args.output, "w") as f:
    f.write(program)
