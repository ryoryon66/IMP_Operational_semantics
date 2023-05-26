def test (a,b,) {
    skip
    return a + b
};

print a;

a := test(8,6,);

print a;


b := test(7,a,);

print b;

print 101;

def sum (n,) {
    ret := 0;
    while n >= 0 do
        ret := ret + n;
        n := n - 1
    end
    return ret
};

def sumrec(m,){
    ret := 0;

    if m = 0 then  
        ret := 0
    else
        ret := sumrec(m-1,) + m
    end

    return ret
};

#print sum (100,);
# 多分いまのところローカル変数がグロバルとごっちゃになってそう
# function callの左側に足し算があるとでたらめな値になるっぽい。4000番台後半の値になることからrbpをaexprの評価結果として読んでいるという説がある。


print sumrec(3,);
print sumrec(4,);

print 57;

print sumrec (100,);

#while true do
# print sum(2,) + sum(2,);
  print sum(4,);
  a :=  3 + sum(4,);
  print a;
  print a;
  print a;
  print a # expected 3 + 10 = 13
  #a := sumrec(10,)
#end