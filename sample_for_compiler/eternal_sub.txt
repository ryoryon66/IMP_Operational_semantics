def test(a,b,){
    ret := a + b
    return ret
};

def double(a,){
    skip
    return a
};

def empty(){
    skip
    return 1
};

a := 1;

while true do
    a := 90;
    a := a + a;
    a := a - a;
    if 1 + a = a + a then
        print 1
    else
       a := a
    end;
    a := test(a,a,);
    a := empty(); a := empty();
    a := a + a + a + a + a;
    a := double(a,);

    i := 5;
    j := 15;

    while i >= 0 do 
        ptr := 4090;
        * (ptr - i ) := i;
        while j >= 0 do
            j := j - 1;
            a := double(a);
            a := double(a);
            a := double(double(double(a)))
        end;

        i := i - 1;
        skip
    end;


    skip
end