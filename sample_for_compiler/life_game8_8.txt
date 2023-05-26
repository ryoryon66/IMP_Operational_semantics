grid_ptr := (1 << 12) - 14; # 4082 ~ 4086 シミュレーション自体はここで行う
spare_grid_ptr := (1 << 12) - 26; # 4070 ~ 4074一時領域
display_ptr := (1 << 12) - 4; #4092 ~ 4095 # 表示用領域

setstr (4060) "lifegame";



#縦上から i　横右からjの形式でライフゲームの初期盤面を指定
#左側がi = 0 ~ 3　右側が i = 4 ~ 7


#______________________________________________________________________________



#グライダー 4かける8だとろくなシミュレーションにならない。
#* (display_ptr)     := bin: 0000000000000000;
#* (display_ptr + 1) := bin: 0011100000000000;
#* (display_ptr + 2) := bin: 0010000000000000;
#* (display_ptr + 3) := bin: 0001000000000000;

#ハチの巣とブロック　固定物体が二つ ついでにブロック生成のテストも兼ねる。
#* (display_ptr)     := bin: 0000000000000000;
#* (display_ptr + 1) := bin: 0001100011000000;
#* (display_ptr + 2) := bin: 0010010010000000;
#* (display_ptr + 3) := bin: 0001100000000000;


#ブリンカー 正常に動く
#* (display_ptr)     := bin: 0000000000000000;
#* (display_ptr + 1) := bin: 1000000000000000;
#* (display_ptr + 2) := bin: 1000000000000111;
#* (display_ptr + 3) := bin: 1000000000000000;

#グライダーとブロック 爆発してから消滅する。　面白い挙動。
#* (display_ptr)     := bin: 0000000000000000;
#* (display_ptr + 1) := bin: 0011100000010000;
#* (display_ptr + 2) := bin: 0010000000110000;
#* (display_ptr + 3) := bin: 0001000000000000;

#市松模用 次のターンで消滅するのでつまらない。
#* (display_ptr)     := bin: 0101010101010101;
#* (display_ptr + 1) := bin: 1010101010101010;
#* (display_ptr + 2) := bin: 0101010101010101;
#* (display_ptr + 3) := bin: 1010101010101010;

#グライダー 二個　干渉して最終的に固定物体ボートが1つ生成される。派手ではある。
#* (display_ptr)     := bin: 0000000000000000;
#* (display_ptr + 1) := bin: 1110000111000000;
#* (display_ptr + 2) := bin: 1000000100000000;
#* (display_ptr + 3) := bin: 0100000010000000;

#　軽量級宇宙船　うごくけど見にくいな
* (display_ptr)     := bin: 1001000000000000;
* (display_ptr + 1) := bin: 0000100000000000;
* (display_ptr + 2) := bin: 1000100000000000;
* (display_ptr + 3) := bin: 0111100000000000;

#　中量級宇宙船　うごくけど見にくいな 重量級以降は横幅の問題で爆発する。
#* (display_ptr)     := bin: 1000100000000000;
#* (display_ptr + 1) := bin: 0000010000000000;
#* (display_ptr + 2) := bin: 1000010000000000;
#* (display_ptr + 3) := bin: 0111110000100000;



# random2 短期間でブリンカー　1の確率0.5

* (display_ptr)     := 29479;
* (display_ptr + 1) := 7218;
* (display_ptr + 2) := -19274;
* (display_ptr + 3) := 13114;

# random1 1の確率 0.25 50ターン程度で消滅する。

* (display_ptr)     := 321;
* (display_ptr + 1) := -28652;
* (display_ptr + 2) := 2608;
* (display_ptr + 3) := 5216;







#__________________________________________________________________________________________________




* (grid_ptr)     :=  * (display_ptr);
* (grid_ptr + 1) :=  * (display_ptr + 1);
* (grid_ptr + 2) :=  * (display_ptr + 2);
* (grid_ptr + 3) :=  * (display_ptr + 3);



print * (grid_ptr);
print * (grid_ptr + 1);
print * (grid_ptr + 2);
print * (grid_ptr + 3);



turn := 0;

#誕生
#死んでいるセルに隣接する生きたセルがちょうど3つあれば、次の世代が誕生する。
#生存
#生きているセルに隣接する生きたセルが2つか3つならば、次の世代でも生存する。
#過疎
#生きているセルに隣接する生きたセルが1つ以下ならば、過疎により死滅する。
#過密
#生きているセルに隣接する生きたセルが4つ以上ならば、過密により死滅する。



turn_end := <input>;

while turn < turn_end do
    turn := turn + 1;

    # spareの初期化
    * (spare_grid_ptr)     :=   0;
    * (spare_grid_ptr + 1) :=   0;
    * (spare_grid_ptr + 2) :=   0;
    * (spare_grid_ptr + 3) :=   0;

    #print turn;

    i := 8  - 1;
    j := 8 -  1;

    # spareの方に生存判定を記述する。

    while i >= 0 do 

        next_state := bin: 0000000000000000;

        j := 8 - 1;

        while j >= 0 do

            next_state := next_state << 1 ;

            count := count_neibor(i,j);
            is_survived := get_elem_ij_from_memory(i,j,grid_ptr);

            alive := is_survived;

            # 誕生
            if is_survived = 0 and count = 3 then
                alive := 1
            else
                skip
            end;

            # 生存
            if is_survived = 1 and (count = 2 or count = 3) then
                alive := 1
            else
                skip
            end;

            # 過疎
            if is_survived = 1 and count <= 1 then
                alive := 0
            else
                skip
            end;

            # 過密
            if is_survived = 1 and count >= 4 then
                alive := 0
            else
                skip
            end;

            next_state := next_state + alive;


            j := j - 1

        end;

        if i < 4 then
             * (spare_grid_ptr + i) := (* (spare_grid_ptr + i) ) +  (next_state << 8)
        else
            * (spare_grid_ptr + i - 4) := (* (spare_grid_ptr + i - 4) ) +  next_state
        end;

        i := i - 1

    end;



    # コピーする。

    * (display_ptr)     := * (spare_grid_ptr);
    * (display_ptr + 1) := * (spare_grid_ptr + 1);
    * (display_ptr + 2) := * (spare_grid_ptr + 2);
    * (display_ptr + 3) := * (spare_grid_ptr + 3);

    * (grid_ptr)     := * (spare_grid_ptr);
    * (grid_ptr + 1) := * (spare_grid_ptr + 1);
    * (grid_ptr + 2) := * (spare_grid_ptr + 2);
    * (grid_ptr + 3) := * (spare_grid_ptr + 3);

    print * (grid_ptr);
    print * (grid_ptr + 1);
    print * (grid_ptr + 2);
    print * (grid_ptr + 3);


    skip
end;




#ポインタの後に足し算をするときにはカッコをつけないとsyntaxが全体で* aexpになってしまう。



def ithbit_of(val,n,){ # tested
    m := n;
    while m > 0 do
        val := val >> 1;
        m := m - 1
    end;
    if n = 0 then
        #符号ビットがあるとあまりの計算でバグるので符号ビットを闇に葬る。
        val := val << 1;
        val := val >> 1
    else
        skip
    end
    return (val << 15) >> 15
    #return remainder(val,2,)
};


def get_elem_ij_from_memory(i,j,grid_ptr){ # i 0 ~ 3 j 0 ~ 15 tested gridの最初の要素の番地を引数に入れること

    if i < 4 then
        j := j + 8
    else
        i := i - 4
    end;

    pointer := grid_ptr;
    pointer := pointer + i

    return ithbit_of( (* (pointer) ) , j, )
};
def count_neibor(i,j,) {

    ptr := (1 << 12) - 14; # grid_ptr

    #iplus := remainder (i + 1,8,);
    #iminus := remainder (i + 16 - 1,8,);
    #jplus := remainder (j + 1,8,);
    #jminus := remainder (j + 16 - 1,8,);

    iplus := ((i + 1) << 13) >> 13;
    iminus := ((i + 16 - 1) << 13) >> 13;
    jplus := ((j + 1) << 13) >> 13;
    jminus := ((j + 16 - 1) << 13) >> 13;


    ret := 0;

    next_i := i;
    next_j := jplus;
    ret := ret + get_elem_ij_from_memory(next_i,next_j,ptr);

    next_i := i;
    next_j := jminus;
    ret := ret + get_elem_ij_from_memory(next_i,next_j,ptr);

    next_i := iplus;
    next_j := j;
    ret := ret + get_elem_ij_from_memory(next_i,next_j,ptr);

    next_i := iminus;
    next_j := j;
    ret := ret + get_elem_ij_from_memory(next_i,next_j,ptr);

    next_i := iplus;
    next_j := jplus;
    ret := ret + get_elem_ij_from_memory2(next_i,next_j,ptr);

    next_i := iplus;
    next_j := jminus;
    ret := ret + get_elem_ij_from_memory2(next_i,next_j,ptr);
    
    next_i := iminus;
    next_j := jplus;
    ret := ret + get_elem_ij_from_memory2(next_i,next_j,ptr);

    next_i := iminus;
    next_j := jminus;
    ret := ret + get_elem_ij_from_memory2(next_i,next_j,ptr);

    skip
    return ret
};

def get_elem_ij_from_memory2(i,j,grid_ptr){ # i 0 ~ 3 j 0 ~ 15 tested gridの最初の要素の番地を引数に入れること

    if i < 4 then
        j := j + 8
    else
        i := i - 4
    end;

    pointer := grid_ptr;
    pointer := pointer + i

    return ithbit_of( (* (pointer) ) , j, )
};

skip
