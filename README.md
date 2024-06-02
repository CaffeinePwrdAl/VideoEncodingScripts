# Video Encoding Scripts
This repository contains some scripts to help perform some video re-encoding tasks, such as converting MOV files from my digital cameras to h265 to save space.
Mostly this is using ffmpeg and similar free tools

## make265.py
This uses some settings I've tweaked to give me the level of quality I want vs. file size reduction. This for my taste is perceptually un-noticable, has good encoding speed, and decent file-size reduction.

```
> python make265.py --help
usage: make265.py [-h] [--name NAME] [--input INPUT] [--season SEASON] [--episode EPISODE] [--profile PROFILE] [--ffmpeg FFMPEG]
                  [--extn EXTN] [--gpu]

Convert sets of videos to h265 to save disk space.

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

* Olympus E-PL8 - MOV -> MP4

| Codec | Image |
| :---: | :---: |
| .mov (original, 27.6mb) | <img alt="Still from video from Olympus E-PL8" src="images/japfest_2024_mov.png?raw=true" width="100%" title="Still from video from Olympus E-PL8"> |
| .mp4 (h265, 7.7mb) | <img alt="Still from video re-encoded as h265" src="images/japfest_2024_h265.png?raw=true" width="100%" title="Still from video re-encoded as h265"> |
| diff (tol=5/255) | <img alt="Diff of images" src="images/japfest_2024_diff.png?raw=true" width="100%" title="Diff of images"> |

* Canon 70D - MOV -> MP4, keep audio. 101MB -> 21MB
