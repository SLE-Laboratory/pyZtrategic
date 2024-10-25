#csv_headers($file, $sequence)
csv_headers() {
    local filename=$1
    shift
    echo "--," | head -c -1 >> $filename
    for v in "$@"
    do 
        echo "$v," | head -c -1 >> $filename
    done 
    echo "" >> $filename
}


#sequence of values to iterate
sequenceLet=$(seq 2 2 16)


timeLet='timeLet.log'
memoryLet='memoryLet.log'

#----------
#----
#--- Time benchmarks  
#----
#----------

source .venv/bin/activate

#time
#Let
echo "Beginning time benchmarks for Let in file $timeLet..."
csv_headers $timeLet $sequenceLet

echo "Let," | head -c -1 >> $timeLet
for input_size in $sequenceLet
do 
    { /usr/bin/time -p python3 let.py $input_size > /dev/null; } 2>&1 | grep real | grep -Eo '[0-9]+([.][0-9]+)?' | head -c -1 >> $timeLet
    echo "," | head -c -1 >> $timeLet
done
echo "" >> $timeLet

echo "Done!"


#----------
#----
#--- Memory benchmarks  
#----
#----------

#memory
#Let
echo "Beginning memory benchmarks for Let in file $memoryLet..."
csv_headers $memoryLet $sequenceLet

echo "$program," | head -c -1 >> $memoryLet
for input_size in $sequenceLet
do 
    { /usr/bin/time -v python3 let.py $input_size > /dev/null; } 2>&1 | grep "Maximum resident" | sed "s/[^0-9]\+\([0-9]\+\).*/\1/"  | head -c -1 >> $memoryLet
    echo "," | head -c -1 >> $memoryLet
done
echo "" >> $memoryLet

echo "Done!"