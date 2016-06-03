#!/usr/bin/env bash
set -x
N=${1:-4}

source ../virtualenv/bin/activate
for (( c=1; c<=${N}; c++ ))
do
    python NetTE${c}.py -f smallnet.dat
    python NetTE${c}.py -f network.dat
done
