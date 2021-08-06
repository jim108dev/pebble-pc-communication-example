# Pebble PC Communication Example

A lot of my apps for pebble have the same workflow:

1. Send data from the pc to the pebble app.
1. Store the data on the watch and close the connection.
1. At a later stage, display the data and gather feedback.
1. At a later stage, send the data back to the pc.

This is a learning project in order to set this process up correctly, so that it can be used as a template for other apps.

Currently:

1. The data is read from csv in form of a string and a time values and send via a Python script.
1. The demo app receives them via *AppMessage*, stores them.
1. It can display the data.
1. It updates the time and sends it back via *Data-Logging*.
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

## Usage

1. Run on the emulator

  ```sh
  cd pebble_app
  pebble build && pebble install --logs --emulator aplite

  # second terminal
  # Activate venv
  cd host_python
  ./pebble_upload.py config_emu.ini

  # Browse the emulator window
  # Download the created data
  ./pebble_download.py config_emu.ini
  ```

1. Run on the watch

  ```sh
  cd pebble_app
  pebble build && pebble install --serial /dev/rfcomm0

  # second terminal
  # Activate venv
  cd host_python
  ./pebble_upload.py config_watch.ini

  # Browse the emulator window
  # Download the created data
  ./pebble_download.py config_watch.ini
  ```

## Development

1. The config for VSCode is inside `pebble_app/.vscode`. In order to have IntelliSense `pebble_app` must be added directly with `Add Folder to Workspace`.

## Learning Questions

### Can the hole process be done in the emulator?

   Yes, the critical part is getting the port of the running emulator.

### How reliable does the upload work?

   1 of 5 times the upload works.

### Can debugging be activated during the upload?

   This does not work with the watch because both connections use the same port. It is working with the emulator.

### How reliable does the download work?

   Because *Data-Logging* is used, it works every time.

### What is the best practice on storing records?

   I have used a field to store the maximum number of records. And I am storing the records with an offset of 10.

## Problems

1. The emulator does not show debug messages right away. Reproduce with:

  ```sh
  pebble new-project pebble-test
  cd pebble-test
  pebble build && pebble install --logs --emulator aplite
  #Installing app...
  #App install succeeded.
  # no message

  #<-Left arrow key, right arrow key->
  #[18:18:59] ocess_manager.c:417> Heap Usage for App <pebble-tes: Total Size <23044B> Used <340B> Still allocated <24B>
  #[18:19:01] pebble-test.c:65> Done initializing, pushed window: 0x2001a618
  ```

## Used Packages

1. [@smallstoneapps/data-processor](https://github.com/smallstoneapps/data-processor)
1. [@smallstoneapps/utils](https://github.com/smallstoneapps/utils)
1. [pebble-packet](https://github.com/C-D-Lewis/pebble-packet)

## Sources

1. [Pebble Linux Remote](https://github.com/susundberg/pebble-linux-remote)
1. [Pebble Modular App Example](https://github.com/pebble-examples/modular-app-example/)
1. [AppMsgBridge](https://github.com/finebyte/AppMsgBridge)
