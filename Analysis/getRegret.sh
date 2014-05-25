#!/bin/bash

for f in subGames/*
do
echo $f
python ../../GameAnalysis/Regret.py $f < 182-summary.json
done
