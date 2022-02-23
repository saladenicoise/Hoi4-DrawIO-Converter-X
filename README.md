# HoI4 DrawIO Converter

Originaly made by Flaxbeard, then fixed by NIKA.

HoI4 DrawIO Converter is a tool to generate hoi4 focus file from drawio xml data.

## Usage
1. Open [draw.io] then design natinal focus with square and arrows
2. Write focus titles in your square boxes. Both English and Japanese are allowed.
3. Open Extras -> Edit Diagram then copy xml data
4. Lanch exe file and paste the xml you copied into the textarea
5. Click "Run Program" then you will get focus file and localisation file in output box which will be created.

## Build

Use pyinstaller to build exe file

```
pyinstaller DrawIoConverter.py --onefile --noconsole
```
