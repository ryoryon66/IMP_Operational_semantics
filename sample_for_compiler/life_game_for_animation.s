grid_ptr := (1 << 12) - 14; # 4082 ~ 4087 シミュレーション自体はここで行う
spare_grid_ptr := (1 << 12) - 26; # 4070 ~ 4075一時領域
display_ptr := (1 << 12) - 4; #4092 ~ 4095 # 表示用領域



#縦上から i　横右からjの形式でライフゲームの初期盤面を指定


#______________________________________________________________________________

# #ハチの巣
# * (display_ptr)     := bin: 0000000000000000;
# * (display_ptr + 1) := bin: 0000110000000000;
# * (display_ptr + 2) := bin: 0001001000000000;
# * (display_ptr + 3) := bin: 0000110000000000;



# #ブロック
# * (display_ptr)     := bin: 0000000000000000;
# * (display_ptr + 1) := bin: 0000000000000000;
# * (display_ptr + 2) := bin: 0000000000000011;
# * (display_ptr + 3) := bin: 0000000000000011;



#グライダーとブロック 4かける8だとろくなシミュレーションにならない。 5かける８でも十分広い時のシミュレーションとは異なり消滅する。
* (display_ptr)     := bin: 0000000000000000;
* (display_ptr + 1) := bin: 0011100000110000;
* (display_ptr + 2) := bin: 0010000000110000;
* (display_ptr + 3) := bin: 0001000000000000;



#ブリンカー
* (display_ptr)     := bin: 0000000000000000;
* (display_ptr + 1) := bin: 1000000000111000;
* (display_ptr + 2) := bin: 1000000000000000;
* (display_ptr + 3) := bin: 1000000000000000;



#グライダー 4かける8だとろくなシミュレーションにならない。
* (display_ptr)     := bin: 0000000000000000;
* (display_ptr + 1) := bin: 0011100000000000;
* (display_ptr + 2) := bin: 0010000000000000;
* (display_ptr + 3) := bin: 0001000000000000;

#__________________________________________________________________________________________________




* (grid_ptr)   :=  * (display_ptr);
* (grid_ptr + 1) :=  * (display_ptr + 1);
* (grid_ptr + 2) :=  * (display_ptr + 2);
* (grid_ptr + 3) :=  * (display_ptr + 3);
* (grid_ptr + 4) :=  bin: 0000000000000000;


print * (grid_ptr);
print * (grid_ptr + 1);
print * (grid_ptr + 2);
print * (grid_ptr + 3);
print * (grid_ptr + 4);



turn := 0;

#誕生
#死んでいるセルに隣接する生きたセルがちょうど3つあれば、次の世代が誕生する。
#生存
#生きているセルに隣接する生きたセルが2つか3つならば、次の世代でも生存する。
#過疎
#生きているセルに隣接する生きたセルが1つ以下ならば、過疎により死滅する。
#過密
#生きているセルに隣接する生きたセルが4つ以上ならば、過密により死滅する。



turn_end := 100;

while turn < turn_end do
    turn := turn + 1;

    #print turn;

    i := 4;
    j := 15;

    # spareの方に生存判定を記述する。

    while i >= 0 do 

        next_state := bin: 0000000000000000;

        j := 15;

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

        *(spare_grid_ptr + i) := next_state;

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
    * (grid_ptr + 4) := * (spare_grid_ptr + 4);



    print * (grid_ptr);
    print * (grid_ptr + 1);
    print * (grid_ptr + 2);
    print * (grid_ptr + 3);
    print * (grid_ptr + 4);



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
    return remainder(val,2,)
};
def remainder(a,b,){
    while a >= b do
        a := a - b
    end
    return a
};
def get_elem_ij_from_memory(i,j,grid_ptr){ # i 0 ~ 3 j 0 ~ 15 tested gridの最初の要素の番地を引数に入れること
    pointer := grid_ptr;
    pointer := pointer + i
    return ithbit_of( (* (pointer) ) , j, )
};
def count_neibor(i,j,) {

    ptr := (1 << 12) - 14; # grid_ptr

    iplus := remainder (i + 1,5,);
    iminus := remainder (i + 10 - 1,5,);
    jplus := remainder (j + 1,16,);
    jminus := remainder (j + 16 - 1,16,);
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
    ret := ret + get_elem_ij_from_memory(next_i,next_j,ptr);

    next_i := iplus;
    next_j := jminus;
    ret := ret + get_elem_ij_from_memory(next_i,next_j,ptr);
    
    next_i := iminus;
    next_j := jplus;
    ret := ret + get_elem_ij_from_memory(next_i,next_j,ptr);

    next_i := iminus;
    next_j := jminus;
    ret := ret + get_elem_ij_from_memory(next_i,next_j,ptr);

    skip
    return ret
};

skip
