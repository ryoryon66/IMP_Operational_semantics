# this is lifegame debug program
import copy
import enum

from matplotlib.pyplot import step

def base_change(n):
    #入力された符号付き整数を符号付き二進数16桁に変換する
    if n < 0:
        n = 2**16 + n
    return format(n,'016b')

# 一つの盤面が何行で表されるか。
NUM_ROW = 4


while True:
    print ("Input the state of cells in 16 bit signed integer")
    state = []
    for i in range(NUM_ROW):
        try:
            s = input()
        except EOFError:
            import sys
            import time
            time.sleep(0.1)
            # erase previous line and move cursor to the beginning of the line
            print ("\033[1A\033[2K", end="")
                
            sys.exit()

        if "Input" in s:
            s = s.split (":")[2]

        s = s.split(":")[1] if ":" in s else s
        s = int(s)
        state.append(s)
    
    for i, s in enumerate(state):
        output = ""
        for i in range(16):
            output += "#" if base_change(s)[i] == "1" else "."
        print (output)
        
    
    
