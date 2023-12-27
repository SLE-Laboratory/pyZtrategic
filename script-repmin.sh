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
sequenceRepMin=$(seq 5000 5000 40000)


timeRepMin='timeRepMin.log'
memoryRepMin='memoryRepMin.log'

#----------
#----
#--- Time benchmarks  
#----
#----------

source .venv/bin/activate

#time
#Repmin
echo "Beginning time benchmarks for Repmin in file $timeRepMin..."
csv_headers $timeRepMin $sequenceRepMin

echo "Repmin," | head -c -1 >> $timeRepMin
for input_size in $sequenceRepMin
do 
    { /usr/bin/time -p python3 repmin.py $input_size > /dev/null; } 2>&1 | grep real | grep -Eo '[0-9]+([.][0-9]+)?' | head -c -1 >> $timeRepMin
    echo "," | head -c -1 >> $timeRepMin
done
echo "" >> $timeRepMin

echo "Done!"


#----------
#----
#--- Memory benchmarks  
#----
#----------

#memory
#Repmin
echo "Beginning memory benchmarks for Repmin in file $memoryRepMin..."
csv_headers $memoryRepMin $sequenceRepMin

echo "$program," | head -c -1 >> $memoryRepMin
for input_size in $sequenceRepMin
do 
    { /usr/bin/time -v python3 repmin.py $input_size > /dev/null; } 2>&1 | grep "Maximum resident" | sed "s/[^0-9]\+\([0-9]\+\).*/\1/"  | head -c -1 >> $memoryRepMin
    echo "," | head -c -1 >> $memoryRepMin
done
echo "" >> $memoryRepMin

echo "Done!"