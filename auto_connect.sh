#!/bin/bash

# Function to check if device is connected
check_device_connected() {
    bluetoothctl << EOF | grep -q "Connected: yes"
    info 9C:D6:AF:26:04:A0
    exit
EOF
}

# Start Bluetooth control tool and connect
bluetoothctl << EOF
power on
connect 9C:D6:AF:26:04:A0
exit
EOF

# Check if connected and continuously attempt to reconnect if disconnected
while true; do
    if ! check_device_connected; then
        echo "Device disconnected. Reconnecting..."
        bluetoothctl << EOF
        power on
        connect 9C:D6:AF:26:04:A0
        exit
EOF
    fi
    sleep 10  # Wait for 10 seconds before checking again
done
