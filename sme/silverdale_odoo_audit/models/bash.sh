#!/bin/sh
while getopts p:t:o:c:u: flag
do
    case "${flag}" in
        p) path=${OPTARG};;
        t) tmpfile=${OPTARG};;
        o) outfile=${OPTARG};;
		c) config=${OPTARG};;
		u) ur=${OPTARG};;
    esac
done

input="$path"
tmp="$tmpfile"

pylint -r y  "$input" > $tmpfile

report_line=false
report_start=false
while read line 
do
	if [ "$report_start" == true ]; then
		echo "$line" >> "$outfile"
		report_start=true
	elif [ "$line" == "Report" ]; then
		report_line=true
	elif [ "$report_line" == true ] && [ "$line" == "======" ]; then
		report_start=true
	elif [ "$report_start" == false ]; then
		report_line=false
	fi

done < $tmpfile
rm $tmpfile
# curl -F "data=/tmp/odoo/text.txt"  "localhost:8070/my/report/1?access_token=06cd6ce3-2800-40ee-ab8f-0ac7bc264264"
curl  -d "data=$outfile"  "$ur"