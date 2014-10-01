#!/bin/bash

COUNTER=0
printf '[\n' >> checkACYD3D.json
for f in subGames/*
do
echo $COUNTER
COUNTER=$((COUNTER+1))
r=$(python ../../GameAnalysis/Regret.py $f < ./Input_files/check3.json)
printf '{"filename":"%s","regrets":"%s"},\n' "$f" "$r" >> checkACYD3D.json
done
printf ']' >> checkACYD3D.json
