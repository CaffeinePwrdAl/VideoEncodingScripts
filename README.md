# Video Encoding Scripts
This repository contains some scripts to help perform some video re-encoding tasks, such as converting MOV files from my digital cameras to h265 to save space.
Mostly this is using ffmpeg and similar free tools
## make265.py
This uses some settings I've tweaked to give me the level of quality I want vs. file size reduction. This for my taste is perceptually un-noticable, has good encoding speed, and decent file-size reduction.

```
> python make265.py --help
usage: make265.py [-h] [--name NAME] [--input INPUT] [--season SEASON] [--episode EPISODE] [--profile PROFILE] [--ffmpeg FFMPEG]
                  [--extn EXTN] [--gpu]

Convert sets of videos to h265 to save disk space, and for posting online to save bandwidth and meet file size limits (Whatsapp and Discord)

options:
  -h, --help         show this help message and exit
  --name NAME        Basename to use for output files
  --input INPUT      Input file or folder.
  --season SEASON    Season number
  --episode EPISODE  If using season number, specify the starting episode for this sequence
  --profile PROFILE  Profile - one of tv, hd, uhd, canon, olympus
  --ffmpeg FFMPEG    Directory to ffmpeg bin dir
  --extn EXTN        Output container extension to use, mkv or mp4 typically
  --gpu              Use h264_nvenc or hvec_nvenc cuda accellerated encoding
```

### Examples

Olympus - MOV -> MP4, keep audio. 27.6mb -> 7.7mb
Canon 70D - MOV -> MP4, keep audio. 101MB -> 21MB