#!/bin/bash

################################################################
SCRIPT_FULLPATH="$(realpath $0)"
SCRIPT_DIR="$(dirname "${SCRIPT_FULLPATH}")"
################################################################
SVC_DIR="/etc/systemd/system/"
SVC_NAME="pwm-fan-control.service"
EXE_PATH="${SCRIPT_DIR}/service/pwm-fan-control.py"
################################################################

# TEST VARIABLES
# Commented out ; Used to troubleshoot
#echo "CONSTANT / VARIABLE VALUES" 
#echo "=========================="
#echo "Script full path : $SCRIPT_FULLPATH"
#echo "Script directory : $SCRIPT_DIR"
#echo "Service directory: $SVC_DIR"
#echo "Service name     : $SVC_NAME"
#echo "Target executable: $EXE_PATH"
#echo ""

## Display custom error messages ##
error-exit() {
    echo "Error: $1"
    exit 1
}

## Create the service unit file ##
create-unit() {
    # echo "create-unit function:" # Commented out ; Used to troubleshoot
    echo "Creating a new service unit: ${SVC_DIR}${SVC_NAME}"
    cat <<EOF | sudo tee "${SVC_DIR}${SVC_NAME}" &> /dev/null 
[Unit]
Description=PWM Fan Control
After=multi-user.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 ${EXE_PATH}
Restart=always
KillSignal=SIGINT

[Install]
WantedBy=multi-user.target
EOF

    # Verify that unit file is created
    if [ -e ${SVC_DIR}${SVC_NAME} ]; then
        echo "Successfully created service unit file."
        return 0
    else
        error-exit "Failed to create service unit file."
    fi
}

## Stop and remove the service ##
delete-service() {
    #echo "delete-service function:" # Commented out ; Used to troubleshoot
    echo "Deleting the service: ${SVC_NAME}"
    systemctl --quiet stop ${SVC_NAME} &> /dev/null || error-exit "Unable to stop the service."
    systemctl --quiet disable ${SVC_NAME} &> /dev/null || error-exit "Unable to disable the service."
}

## Load and start the service ##
add-service() {
    #echo "add-service function:" # Commented out ; Used to troubleshoot

    # Remove existing service
    if systemctl is-active --quiet $SVC_NAME; then
        delete-service
    fi

    # Create service unit file
    create-unit

    # Set the python file to executable
    sudo chmod +x ${EXE_PATH} &> /dev/null || echo "Setting chmod failed"

    # Reload and reset systemd
    echo "Reloading systemd daemon..."
    systemctl --quiet daemon-reload &> /dev/null || error-exit "Unable to reload systemd."
    
    # Enable and start the service
    echo "Enabling the service: ${SVC_NAME}"
    systemctl --quiet enable ${SVC_NAME} &> /dev/null || error-exit "Unable to enable the service."
    echo "Starting the service: ${SVC_NAME}"
    systemctl --quiet start ${SVC_NAME} &> /dev/null || error-exit "Unable to start the service."
}

## Detect existing service installation ##
if [ -e ${SVC_DIR}${SVC_NAME} ]; then
    echo "Existing service installation found."
    echo "Do you want to overwrite? (Y/n)"
    read -r answer
    if [ ${answer} = 'y' ] || [ ${answer} = 'Y' ]; then
        add-service
    else
        exit 0
    fi
else
    echo "Proceed with new service installation? (Y/n)"
    read -r answer
    if [ ${answer} = 'y' ] || [ ${answer} = 'Y' ]; then
        add-service
    else
        exit 0
    fi
fi

## Verify the service is active
if systemctl is-active --quiet $SVC_NAME; then
    echo "Service ${SVC_NAME} successfully enabled and started!"
    exit 0
else
    error-exit "Failed to complete service deployment. Aborting."
fi
