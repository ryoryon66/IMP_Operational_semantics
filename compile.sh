python compiler.py > simple_asm_with_label.txt
python process_label.py --input simple_asm_with_label.txt --output simple_asm.txt

echo "---------------------" 

java -jar SimpleSimulator.jar   -m  simple_asm.txt

echo "---------------------"


# 標準エラー出力をファイルにリダイレクト
java -jar SimpleSimulator.jar  -d -m  simple_asm.txt 2> log.txt

echo "---------------------" 
echo "in order to see record log, please type the same value when Input? is asked"

echo "---------------------" >> log.txt
# 追記
java -jar SimpleSimulator.jar   -m  simple_asm.txt >> log.txt