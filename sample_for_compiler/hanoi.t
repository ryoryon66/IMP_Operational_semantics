

def mult(a,b,){
    ret := 0;
    while b > 0 do
        ret := ret + a;
        b := b - 1
    end

    return ret
};

# def div(a,b,){
#     ret := 0;
#     while a >= b do
#         a := a - b;
#         ret := ret + 1
#     end

#     return ret
# };

# def mod(a,b,){
#     while a >= b do
#         a := a - b
#     end

#     return a
# };

def pow(a,b,){
    ret := 1;
    while b > 0 do
        ret := mult (ret,a,);
        b := b - 1
    end

    return ret
};

def simulate_hanoi(state,from,to,disk_to_move,){ # state 000-999 from 0 to 2 to 0 to 2, disk_to_move この操作で動かすディスクの枚数
    ret_state := state;
    
    # print  57;
    # print state;
    # print from;
    # print to;
    # print disk_to_move;
    # print 57;

    base_from := pow(10,from,);
    base_to := pow(10,to,);

    # print base_from;
    # print base_to;

    mid := 3 - from - to;

    if disk_to_move = 1 then
        # 土台をfromからtoへ移動
        ret_state := ret_state - base_from + base_to;
        operation_count := operation_count + 1;
        print -1
    else 

        # diskの移動 fromからmidへ
        ret_state := simulate_hanoi(ret_state,from,mid,disk_to_move-1,);

        # 土台をfromからtoへ移動
        # ret_state := ret_state - base_from + base_to;
        ret_state := simulate_hanoi(ret_state,from,to,1,);

        # diskの移動 midからtoへ

        ret_state := simulate_hanoi(ret_state,mid,to,disk_to_move-1,)
    end;

    print ret_state;



    skip

    



    return ret_state
    # return 1
};

n :=<input>;
state :=  mult(n,10,) ;
state := state + 100 + 100 +  100 + 100  +  100 + 100  +  100 + 100 +  100 + 100 ;

print state;

state := simulate_hanoi(state,1,0,n,);

print state;

while true do
    state := n;
    print 91;
    state := simulate_hanoi(state,0,1,n,)
end;



# print mult (4,4,);

# print div (12,3,);

# print mod (10,3,);

# print pow (2,10,);

# a := 10;
# b := 3;

# while a >= b do
#     a := a - b
# end;

# print a;




skip