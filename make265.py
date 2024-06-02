#
# In case I want to add 4k HDR stuff later, this was my manual setup for some HDR content
#
# ffmpeg \
# -i hdr_4k_t00.mkv \
# -max_muxing_queue_size 4096 -c:v libx265 -vtag hvc1 -pix_fmt yuv420p10le -profile:v main10 -vsync 0 -level 5.1 \
# -x265-params crf=20:vbv-bufsize=10000:vbv-maxrate=5000:selective-sao=0:
#     no-sao=1:strong-intra-smoothing=0:rect=0:aq-mode=1:hdr-opt=1:chromaloc=2:
#     repeat-headers=1:colorprim=bt2020:range=limited:transfer=smpte2084:colormatrix=bt2020nc:range=limited:
#     master-display='G(13250,34500)B(7500,3000)R(34000,16000)WP(15635,16450)L(40000000,50)':max-cll=1993,311 \
# -vf 'scale=1920x1080:flags=lanczos:in_h_chr_pos=0:in_v_chr_pos=0' \
# -v error -stats -crf 20 -map 0 -c:a copy -c:s copy \
# test_1080p_hdr_4k_downsample_h265.mkv
#

import argparse
import os
import time
import subprocess
from pathlib import Path

class AttrDict(dict):
    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value

ffmpeg_dir='z:/dev/ffmpeg/bin/'

def make_encode_commandline(args, v):
    executable = os.path.join(args.ffmpeg, 'ffmpeg.exe')  
    
    # ffmpeg.exe -i [input_file]
    arguments = [executable, '-i', v.input]
    
    #
    # Quantisation parameters for different profiles [GPU, CPU]
    #
    quant_values = {
        'default':       { 'cpu': 27, 'gpu': 25 },
        'canon':         { 'cpu': 18, 'gpu': 23 },
        'olympus':       { 'cpu': 16, 'gpu': 20 },
    }
    qp = quant_values['default']
    if args.profile in quant_values.keys():
        qp = quant_values[args.profile]
        
    print(qp)
    
    #
    # GPU Encoding - using hevc_nvenc, this obviously is NVIDIA specific, will
    # need to profile the Intel card to see what it's capable of.
    #
    # This gets about 6.5x on a GTX1080
    #
    if args.gpu:
        arguments = [executable, '-hwaccel_output_format', 'cuda', '-i', v.input] 
        arguments += ['-c:v', 'hevc_nvenc', '-preset', 'slow']
        if 0:
            # Around 2.8GB for s01e01
            # Variable bit rate
            arguments += ['-rc', 'vbr']
            # Min max quantisation. 27 good, but fairly big
            arguments += ['-cq', '27', '-qmin', '27', '-qmax', '27', '-b:v', '0']
        else:
            # 27 is good qual, 2.7GB for s01e01
            # 30 is very comparable in quality and size to 25 on x265
            arguments += ['-rc', 'constqp', '-qp', qp['gpu'], '-b:v', '0K']
        # Min max bitrate
        # arguments += ['-b:v', '2M', '-maxrate:v', '10M']
    #
    # CPU Encoding - using x265 which is still remarkably fast, but not quite
    # as quick as the GPU encoding above
    #
    # 13th Gen i7 was getting about 2.6x for 1920x1080 bluray content
    #
    else:
        # 18 and 23 show minimal differences, even in beyond compare. Doubles encoding fps
        # 25 aq 3 is 2.2GB for s01e01 which I'm happy with
        arguments += ['-c:v', 'libx265', '-preset', 'medium', '-crf', qp['cpu'], '-aq-mode', '3']
        
        # Reduce length of intra predicted frames
        arguments += ['-x265-params', 'keyint=96']

    if args.profile == 'olympus' or args.profile == 'canon':
        # Copy audio, no subs, avoid issues with timecodes - might be due to MOV files
        arguments += ['-c:a', 'copy']
    else:
        # Copy audio and sub-titles as-is
        arguments += ['-map', '0', '-c:a', 'copy', '-c:s', 'copy']
    
    # Output
    arguments += [v.base_name]
     
    return [str(x) for x in arguments]

def encode_video(i, args, v):
    print("%3d %40s -> %-40s (profile: %s)"%(i, v.input_name, v.base_name, args.profile))
    
    command = make_encode_commandline(args, v)
    print(command)
    
    start = time.time()
    output=subprocess.Popen(command)
    output.communicate()
    end = time.time()
    print('-'*10, ' Total Time for video encode', end - start)

def check_input_params(args, filename, episode=None):
    base_dir = args.input_dir
    (input_name, extn) = os.path.splitext(os.path.basename(filename))
    input_filename = os.path.join(base_dir, input_name + extn)
    base_name = input_name

    if extn.lower() not in ['.mkv', '.mp4', '.avi', '.mpg', '.mov']:
        print("Skipping file", filename, "unexpected extension '", extn, "'")
        return None
    
    # Base name over-ride
    if args.name:
        base_name=args.name
 
    # Add codec tag(s)
    base_name += '_h265'
    if args.gpu:
        base_name += '_nvenc'
        
    if args.season:
        base_name += '_s%02de%02d'%(args.season, episode)
        
    base_name = base_name + '.' + args.extn
    
    params = AttrDict()
    params.base_dir = base_dir
    params.base_name = base_name
    params.extn = args.extn
    params.input = input_filename
    params.input_name = input_name + extn
    return params

def process_encodes(args, files):
    # Generate filenames starting at a specific episode number
    episode=1
    if args.season and args.episode:
        episode = args.episode

    # Generate filenames and parameters
    videos=[]
    for filename in files:
        params = check_input_params(args, filename, episode)
        if params:
            videos.append(params)
            episode += 1
    
    # Check that the input to output mapping is good before starting
    print("Videos to process:")
    i = 0
    for v in videos:
        print("%3d %40s -> %-40s"%(i, v.input_name, v.base_name))
        i += 1
        
    input("Press Enter to continue...")
        
    # Start the fans please
    print("Execute encodes:")
    i = 0
    for v in videos:
        encode_video(i, args, v)
        i += 1

def main():
    parser = argparse.ArgumentParser(description='Convert sets of videos to h265 to save space. Mov->h265 can be 1/10th the size, VC1 to 265 a 1/3rd')
    parser.add_argument('--name', default=None, type=str, help='Basename to use for output files')
    parser.add_argument('--input', default='rgb_syn_test/upscale', type=str, help='Input file or folder.')
    parser.add_argument('--season', default=None, type=int, help='Season number')
    parser.add_argument('--episode', default=None, type=int, help='If using season number, specify the starting episode for this sequence')
    parser.add_argument('--profile', default='tv', type=str, help='Profile - one of tv, hd, uhd, canon, olympus')
    parser.add_argument('--ffmpeg', default=ffmpeg_dir, type=str, help='Directory to ffmpeg bin dir')
    parser.add_argument('--extn', default='mkv', type=str, help='Output container extension to use, mkv or mp4 typically')
    parser.add_argument('--gpu', action="store_true", help="Use h264_nvenc or hvec_nvenc cuda accellerated encoding")
    # Add pixfmt option instead of defaulting, i.e. yuv420p yuv420p10le
    args = parser.parse_args()
    
    args.input = Path(args.input).resolve()
    args.ffmpeg = Path(args.ffmpeg).resolve()
    
    args.input_dir = args.input
    if not os.path.isdir(args.input):
        args.input_dir = os.path.dirname(args.input)
    
    if (os.path.isdir(args.input)):
        files = list(x for x in args.input.iterdir() if x.is_file())
    else:
        files = [args.input]
        
    process_encodes(args, files)
    
if __name__ == "__main__":
    main()