# HoI4 DrawIO Converter

Originaly made by Flaxbeard, then fixed by NIKA.

HoI4 DrawIO Converter is a tool to generate hoi4 focus file from drawio xml data.

## Download
Download exe file from github [releases](https://github.com/yuto-moriizumi/Hoi4-DrawIO-Converter/releases) page

## Usage
1. Open [draw.io](https://app.diagrams.net/) then design natinal focus with square and arrows. Make sure that the boxes are located evenly spaced.![like this](https://static.wikia.nocookie.net/ssw-developers/images/7/75/NF%E5%A4%89%E6%8F%9B%E6%A9%9F.png/revision/latest/scale-to-width-down/547?cb=20220105010048&path-prefix=ja)
1. Write focus titles in your square boxes. Both English and Japanese are allowed.
1. Open Extras -> Edit Diagram then copy xml data
1. Lanch exe file and paste the xml you copied into the textarea
1. Click "Run Program" then you will get focus file and localisation file in output box which will be created.

## Build

Use pyinstaller to build exe file

```
pyinstaller DrawIoConverter.py --onefile --noconsole
```
