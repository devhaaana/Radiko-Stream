import warnings
warnings.filterwarnings(action='ignore')
import argparse

from radiko import *
from utils import *


def setting_argument():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--version', type=str, default='1.0.0', help='Version')
    parser.add_argument('--station', type=str, default='LFR', help='Stream Station ID')
    parser.add_argument('--areaFree', type=str2bool, default=False, help='Stream Area Free')
    parser.add_argument('--timeFree', type=str2bool, default=False, help='Stream Time Free')
    parser.add_argument('--startTime', type=str, default=None, help='Stream Start Time')
    parser.add_argument('--endTime', type=str, default=None, help='Stream End Time')
    parser.add_argument('--save', type=str2bool, default=False, help='Save mp4 File')
    
    args = parser.parse_args()
    
    return args


if __name__ == '__main__':
    args = setting_argument()
    
    # print(args)
    
    radiko = Radiko(args)
    if args.save == True:
        stream = radiko.save_mp4()
    else:
        stream = radiko.get_Full_Stream_URL()
 