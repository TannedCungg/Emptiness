#!/bin/bash

source /home/pi/mambaforge/etc/profile.d/conda.sh
source /home/pi/.bashrc
conda activate TannedCung
export BROKER=127.0.0.1
cd /home/pi/TannedCung/BluetoothPlayer/
while true; do
    echo "[INFO]: starting media serving..."
    /bin/bash -c "python Playing_service.py"
    echo "[INFO]: media service off, restarting..."
    sleep 1
done
