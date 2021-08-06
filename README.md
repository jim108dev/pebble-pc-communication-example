# Pebble PC Template

A lot of my apps for pebble have the same workflow:

1. Send data from the pc to the pebble app.
1. Store the data on the watch and close the connection.
1. At a later stage, display the data and gather feedback.
1. At a later stage, send the data back to the pc.

This is a learning project in order to set this process up correctly, so that it can be used as a template for other apps.

Currently:

1. The data is read from csv in form of a string and a time values and send via a Python script.
1. The demo app receives them, stores them, display a summary.
1. It can display the data.
1. It updates the time and sends it back.
1. The data is received and stored to csv via a Python script.

## Install

1. Install Pebble SDK (see [(jim108dev/lessons-learned)](https://github.com/jim108dev/lessons-learned/blob/main/LL-PEBBLE.md)).

1. Install OS dependencies

  ```sh
  apt-get install python-enum34 python-six python-serial
  ```
  
1. Install repository 's software

  ```sh
    git clone https://github.com/jim108dev/pebble-pc-template.git
    
    # Because libpebble2 does not work with python 3.7 a python 2.7 virtual environment is created.
    # ([Errno 2] No such file or directory: '/dev/rfcomm0  ; bluetooth transport')
    cd pebble-pc-template/host_python
    virtualenv --python=/usr/bin/python2.7 venv
    bash
    source venv/bin/activate
    pip install -r requirements.txt
    deactivate
  ```

1. Install on the emulator

  ```sh
  pebble build && pebble install --logs --emulator aplite
  ```

1. Install on the device over bluetooth

  ```sh
  # Enable bluetooth and pair the device
  # Replace B0:B4:48:93:68:71 with your own device
  bluetoothctl
  scan on 
  pair B0:B4:48:93:68:71
  exit
  # Open comm
  sudo rfcomm bind 0 B0:B4:48:93:68:71 1
  
  cd pebble_app
  pebble build && pebble install --serial /dev/rfcomm0

## Usage

1. Upload to the watch

  ```sh
  # Activate venv
  cd host_python
  ./pebble_upload.py config.ini
  ```

1. Download the data from the watch
  
  ```sh
  cd ./host_python
  ./pebble_download.py config.ini
  ```

## Development

[STEPS-PEBBLE-PC-TEMPLATE.md](./STEPS-PEBBLE-PC-TEMPLATE.md) contains *Steps for Reproduction*.

## Learning Questions

### Can the hole process be done in the emulator?

### How reliable does the upload work?

### Can debugging be activated during the upload?

### How reliable does the download work?

### What is the best practice on storing records?

## Used Packages

1. [@smallstoneapps/data-processor](https://github.com/smallstoneapps/data-processor)
1. [@smallstoneapps/utils](https://github.com/smallstoneapps/utils)
1. [pebble-packet](https://github.com/C-D-Lewis/pebble-packet)

## Sources

1. [Pebble Linux Remote](https://github.com/susundberg/pebble-linux-remote)
1. [Pebble Modular App Example](https://github.com/pebble-examples/modular-app-example/)
