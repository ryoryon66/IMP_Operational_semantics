# 引数でlog fileをつくるかどうかを指定する
# 例: ./compile.sh 1





python compiler.py > simple_asm_with_label.txt
python resolve_address.py --input simple_asm_with_label.txt --output simple_asm.txt

echo "---------------------" 

java -jar SimpleSimulator.jar   -m  simple_asm.txt

echo "---------------------"

# log fileをつくるかどうか

if [ $# -eq 0 ]; then
    echo "fin. did not make log file"
    exit 1
fi


# 標準エラー出力をファイルにリダイレクト
java -jar SimpleSimulator.jar  -d -m  simple_asm.txt 2> log.txt

echo "---------------------" 
echo "in order to see record log, please type the same value when Input? is asked"

echo "---------------------" >> log.txt
# 追記
java -jar SimpleSimulator.jar   -m  simple_asm.txt >> log.txt