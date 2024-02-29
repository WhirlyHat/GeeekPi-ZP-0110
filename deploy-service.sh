#!/bin/bash

################################################################
SCRIPT_FULLPATH="$(realpath $0)"
SCRIPT_DIR="$(dirname "${SCRIPT_FULLPATH}")"
################################################################
SVC_DIR="/etc/systemd/system/"
SVC_NAME="pwm-fan-control.service"
EXE_PATH="${SCRIPT_DIR}/service/pwm-fan-control.py"
################################################################
promptAnswer="c"
################################################################

## Function: Display custom error messages ##
show-error() {
    echo "" ; echo "Error: $1" ; echo ""
    exit 1
}

## Function: Prompt user for Y/N answer ##
get-prompt() {
    while true
    do
        read -N1 -t15 -p "$1 (y/N): "
        if [ $? -gt 128 ]; then
            printf "\nTimed out waiting for a user response.\n"
            promptAnswer="c"
            break
        fi
        case $REPLY in
            [yY]) printf "\n\n" ; promptAnswer="${REPLY}" ; break ;;
            [nN]) printf "\n\n" ; promptAnswer="${REPLY}" ; break ;;
            *) printf "\nPlease type \'y\' or \'n\' to continue.\n" ;;
        esac
    done
}

## Function: Create the service unit file ##
new-service() {
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

    # Check if unit file was successfully created
    if ! [ -f "${SVC_DIR}${SVC_NAME}" ]; then
        show-error "Failed to create the service unit file."
    fi
}

## Function: Stop and remove the service ##
remove-service() {
    printf "Removing the service..."
    if systemctl is-active --quiet ${SVC_NAME}; then
        systemctl --quiet stop ${SVC_NAME} &> /dev/null || show-error "Unable to stop the service."
        systemctl --quiet disable ${SVC_NAME} &> /dev/null || show-error "Unable to disable the service."
    fi

    if [ -f "${SVC_DIR}${SVC_NAME}" ]; then
        rm ${SVC_DIR}${SVC_NAME} &> /dev/null || show-error "Failed to remove service unit file."
    fi
    printf "DONE\n"
}

## Function: Load and start the service ##
set-service() {
    # Reload and reset systemd
    printf "Reloading systemd daemon: "
    systemctl --quiet daemon-reload &> /dev/null || show-error "Unable to reload systemd."
    printf "DONE\n"

    # Enable the service
    printf "Enabling service %s: " ${SVC_NAME}
    systemctl --quiet enable ${SVC_NAME} &> /dev/null || show-error "Failed to enable the service."
    printf "DONE\n"

    # Start the service
    printf "Starting service %s: " ${SVC_NAME}
    systemctl --quiet start ${SVC_NAME} &> /dev/null || show-error "Unable to start the service."
    printf "DONE\n"
}

# Detect previous service installation #
printf "\nFinding previous %s installation: " ${SVC_NAME}
if [ -f "${SVC_DIR}${SVC_NAME}" ]; then
    # Prompt service overwrite
    printf "FOUND\n"
    get-prompt "Do you want to overwrite?"
    if [ ${promptAnswer} != 'y' ] && [ ${promptAnswer} != 'Y' ]; then
        exit 0
    fi
    remove-service
else
    # Prompt service install
    printf "NOT FOUND\n"
    get-prompt "Proceed with new service installation?"
    if [ ${promptAnswer} != 'y' ] && [ ${promptAnswer} != 'Y' ]; then
        exit 0
    fi
fi

# Set the python file to executable
sudo chmod +x ${EXE_PATH} &> /dev/null || show-error "Failed to set file permissions: ${EXE_PATH}"

# Install a new instance of service #
printf "Creating a new service unit: " ; new-service ; printf "%s%s\n" ${SVC_DIR} ${SVC_NAME}
printf "Loading and starting the service...\n" ; set-service

# Verify the service is active
if systemctl is-active --quiet $SVC_NAME; then
    echo "Service ${SVC_NAME} successfully enabled and started!"
    exit 0
else
    show-error "Failed to complete service deployment. Aborting."
fi
