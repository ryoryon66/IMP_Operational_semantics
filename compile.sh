# 引数でプログラムへのパスを受け取り、コンパイルして実行する
# 例: ./compile.sh program_path 

# programファイルへのパスをコマンドライン引数から取得
program_path=$1


python processing_system/compiler.py  $program_path > simple_asm_with_label.txt
python  processing_system/resolve_address.py --input simple_asm_with_label.txt --output simple_asm.txt


# simpleasmの行数をわかりやすく出力 コンパイル後の行数は:という形式で出力される
echo "---------------------"
echo "simple_asm.txt"
wc -l simple_asm.txt | awk '{print $1}' | xargs echo "simple_asm.txt has"  "lines"

python music/add_music.py --input simple_asm.txt --output simple_asm.txt --music ./music/music_files/greengreens.txt --s 3000
# python music/add_music.py --input simple_asm.txt --output simple_asm.txt --music ./music/music_files/legend_of_zelda.txt --s 3500 カービーの後にcopilot君の趣味か何かでゼルダ出てきて草

python music/add_music.py --input simple_asm.txt --output simple_asm.txt --music ./music/music_files/kouonchu.txt --s 3320

echo "---------------------" 

java -jar SimpleSimulator.jar   -m  simple_asm.txt

echo "---------------------"




# # 標準エラー出力をファイルにリダイレクト
# java -jar SimpleSimulator.jar  -d -m  simple_asm.txt 2> log.txt

# echo "---------------------" 
# echo "in order to see record log, please type the same value when Input? is asked"

# echo "---------------------" >> log.txt
# # 追記
# java -jar SimpleSimulator.jar   -m  simple_asm.txt >> log.txt