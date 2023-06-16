# IMP_Operational_semantics


IMPの操作的意味論の可視化インタプリタ。
実験3のためにコンパイラも書きました。

# install

```
git clone https://github.com/ryoryon66/IMP_Operational_semantics.git
pip install -r requirements.txt
```
実行

# インタプリタ

```
実行方法
```

## 例

```
S := S;
X := 2;
Z := 0;

while not X = 0 do(
    Z := Z + X;
    X := X - 1
)
```

![graphviz (1)](https://user-images.githubusercontent.com/46624038/235734572-1489a8e6-05ac-4a46-94e6-dee9f75251c5.svg)

```
a := 10;
b := 5;
i := 0;

while (not (a = ((b)))) do(
    i := i + 1;
    if a < b then
        c := b;
        b := a;
        a := c
    else
        skip
    ;
    a := a - b
);

gcd := a;
print gcd
```

![graphviz (3)](https://user-images.githubusercontent.com/46624038/235734994-a3846882-e15e-4a5a-ad3c-35d39944fe6f.svg)

# コンパイラ

TODO
