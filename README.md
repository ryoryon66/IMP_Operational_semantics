# IMP_Operational_semantics


IMPの操作的意味論の可視化インタプリタ。
実験3のためにコンパイラも書きました。

# install

```
git clone https://github.com/ryoryon66/IMP_Operational_semantics.git
apt -y install imagemagick
pip install -r requirements.txt
```

proceccing_system内にコンパイラ、インタプリタがあります。

# インタプリタ

## 使用方法

```
python processing_system/interpreter.py --input プログラムへのパス
```

## 可視化例

```
X := 2;
Z := 0;

while not X = 0 do
    Z := Z + X;
    X := X - 1
end;

print Z
```
![sum_deriviation_tree](https://github.com/ryoryon66/IMP_Operational_semantics/assets/46624038/04618123-8ee6-4d02-b0a3-0b126ac46442)

```
#最大公約数をもとめる
a := 10;
b := 5;
i := 0;

while not (a = b) do
    if a < b then
        c := b;
        b := a;
        a := c
    else
        skip
    end;
    
    i := i + 1;
    a := a - b
end;

print i;
print a;

skip
```

![GCD_deriviation_tree](https://github.com/ryoryon66/IMP_Operational_semantics/assets/46624038/0cae044d-25e8-4f84-9d7d-8a89be612b81)


```
#高階関数
def sum (f,x,){
    ans := 0;
    if 0 < x then
        ans := f(x,) + sum(f,x-1,)
    else
        ans := 0
    end

    return ans
};

def sq(x,){
    skip
    return x*x
};

#def tri (x,){
#    skip
#    return x*x *x
#};

ans := sum(sq,2,);
print ans;

skip
```
![hofun_deriviation_tree](https://github.com/ryoryon66/IMP_Operational_semantics/assets/46624038/d186a5f5-ce77-453c-b1ff-371e41aed6aa)

```
a := 1;
while true do
    a := a + 1
end

#deriviation treeは途中でkeybord interruptionで打ち切った結果
#途中で打ち切っても以下のように途中まで導出木を書いてくれる
```

![eternalwhile_deriviation_tree](https://github.com/ryoryon66/IMP_Operational_semantics/assets/46624038/bef662d5-c2e1-4408-af4f-864c3301d93d)

# コンパイラ

## 使い方



