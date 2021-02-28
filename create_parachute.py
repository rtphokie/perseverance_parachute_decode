#!/usr/bin/env python3
import io
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageOps
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import argparse
import re
from pprint import pprint

'''
Generates a graphic based on the code included in the supersonic parachute used by the Mars Perseverance
rover

syntax: create_parachute word1 word2 word3 [word4|coordinates]

where coordinates are of the format deg min sec [N|S] deg min sec [E|W], eg:
34 11 58 N 118 10 31 W
'''


def plot_ring(encoding, radius, width, rotate_clockwise_degrees=0):
    '''

    :param encoding: list of RGBA colors (defaults to white and red) to plot
    :param radius: outer radius of the pie chart
    :param width: width of the ring, creates a doughnut chart as a result
    :param rotate_clockwise_degrees: where to start the plot, enables starting the next ring where the
                                     previous one ends
    :return: nothing
    '''
    # creates a pie plot of a given radius and width (aka a doughnut plot)
    sizes = np.full(shape=len(encoding), fill_value=1, dtype=np.int32)
    mypie, _ = ax.pie(sizes, radius=radius, colors=encoding, counterclock=False,
                      startangle=-rotate_clockwise_degrees+90) # matplotlib starts pie charts from the right (east)
    plt.setp(mypie, width=width, edgecolor='black')

def encode_10_bit_binary(message, colors=[mcolors.to_rgba('#FFF'),mcolors.to_rgba('#F00')]):
    '''
    :param message: string or list of numbers and individual characters
    :param words: number of 10 bit words to encode, defaults to 8 to create Mars 80 segement per ring parachute
    :param colors: list of colors to use for 0 and 1 bits
    :return: list of RGBA values, last gore (panel) before padding to end of ring
    '''
    result_str = ''
    if type(message) is str and len(message) <= 8:
        words=8
    else:
        words=len(message)
    for character in encode_int(message):
        result_str +=  f"{character:010b}" # build out binary string
    phraseend = len(result_str) # last gore encoded (used to as starting position for next ring)
    if len(result_str) < words*10:
        result_str+='000' # each phrase ends with 3 white gores
    result_str+="1"*((words*10)-len(result_str))  # pad remaining gores with 1's

    result_list = []
    for char in list(result_str):
        result_list.append(colors[int(char)])  # build up list of encoded colors
    return result_list, phraseend

def encode_int(message, limit=8):
    '''
    :param message: string or list of integers and individual characters
    :param limit: number of 10 bit words to include in each line (default: 8)
    :return: list of integers
    '''
    result=[]
    message_list=[]
    if type(message) is str:
        message_list = list(message)  # convert string into list of characters
    elif type(message) is list:
        for x in message:
            if x.isnumeric():
                message_list.append(int(x))
            else:
                message_list.append(x)
    else:
        raise ValueError('only strings and lists supported')
    if len(message_list) > limit:
        print (f'warning: using more than the 80 panels per ring to encode "{message}"')
    for character in message_list:
        if type(character) is int:
            result.append(character)
        elif character.isalpha():
            result.append(ord(character.upper())-ord('A')+1)
        else:
            raise ValueError(f"unrecognized character {character} only letters and numbers supported")
    return result


def fig2img(fig):
    '''
    :param fig: matplotlib figure
    :return: PIL image
    '''
    buf = io.BytesIO()
    fig.savefig(buf)
    buf.seek(0)
    img = Image.open(buf)
    return img


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='design a JPL parachute')

    parser.add_argument('message', action='store', nargs='*',
                        default = ['DARE', 'MIGHTY', 'THINGS','34','11','58','N','118','10','31','W'],
                        help='message to encode (4 words, each 8 or fewer charactrs)')
    parser.add_argument('-white', action='store', default='#FFF', help='hex color for white panels (default #FFF)')
    parser.add_argument('-red', action='store', default='#F00', help='hex color for red panels (default #F00)')

    args = parser.parse_args()
    message = []
    nextposition=0
    for i, word in enumerate(args.message):
        if nextposition > i:
            continue
        lookaheadstr=' '.join(args.message[i:len(args.message)])
        pattern = '((\d{1,3}\s+){3}[NSEW])[aehorstu]*\s*'
        rematch = re.match(pattern, lookaheadstr)
        if rematch:
            sublist = args.message[i:i+8]
            message.append(sublist) # add as list of ints and chars to aid binary conversion
            nextposition=i+8
            print(f"ring {i+1}: {' '.join(sublist)}")
        else:
            message.append(word)
            print(f"ring {i+1}: {word}")

    if len(message) < 4:
        raise ValueError("please include 4 words")

    fig, ax = plt.subplots(figsize=(5, 5), dpi=300)
    ax.axis('equal')

    spacing = [(0.6, 0.45), (1.0, 0.4), (1.2, 0.25), (1.5, 0.18)] # (radius, width) matches Perseverance parachute porportions pretty well.

    start_degrees = 0
    ring_images=[]

    fig, ax = plt.subplots(figsize=(5, 5), dpi=300)
    for ring,radius_width in zip(message, spacing):
        if ring in [message[0], message[-1]]:
            start_degrees = 0  # first and last rings start from the top
        panels, last_panel = encode_10_bit_binary(ring, colors=[args.white, args.red])
        radius, width = radius_width
        plot_ring(panels, radius, width, rotate_clockwise_degrees=start_degrees)
        start_degrees+=((last_panel/80.0)*360)


    filename = f"{'_'.join(args.message)}.png"
    plt.savefig(filename)
    print(f"saved as {filename}")
