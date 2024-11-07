# Radiko-Stream

Radiko-Stream can record the [radiko.jp](https://radiko.jp/) programs outside of Japan.

```console
Radiko_stream
 ┣ data
 ┃ ┣ auth
 ┃ ┃ ┗ auth_key.bin
 ┃ ┣ json
 ┃ ┃ ┗ area.json
 ┣ utils
 ┃ ┣ __init__.py
 ┃ ┗ str2bool.py
 ┣ LICENSE
 ┣ README.md
 ┣ main.py
 ┣ radiko.py
 ┗ requirements.txt
```

## Warning

**Please do not use this project for commercial use. Only for your personal, non-commercial use.**

## Technologies

- `Python` : 3.9

# Technical Details

The authentication of PC(html5) version radkio validates user's location via IP address.

However, the android version of radkio validates user provided by GPS information, not via user's IP address.

# Getting Started

## Installation

- You can install it **locally:**
  ```console
  $ git clone https://github.com/devhaaana/Radiko-Stream.git
  $ cd Radiko-Stream
  ```

## Parameters

* `version` : Versio

  * default: `1.0.0`
* `station` : Select From Station ID for Streaming

  * default: `TBS`
* `areaFree` : Select Area Free for Streaming

  * default: `False`
* `timeFree` : Select Time Free for Streaming

  * default: `False`
* `startTime` : Start Time for Streaming

  * default: `None`
* `endTime` : End Time for Streaming

  * default: `None`
* `Save` : Select For Save

  * default: `False`

## Usage

```console
python main.py --version=1.0.0 --station=LFR --areaFree=False --timeFree=True --startTime=20241106010000 --endTime=20241106030000 --save=True
```

## Reference

[rajiko](https://github.com/jackyzy823/rajiko)
