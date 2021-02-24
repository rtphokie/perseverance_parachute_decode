#!/usr/bin/env python3

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import argparse

'''
Generates a graphic based on the code included in the supersonic parachute used by the Mars Perseverance
rover

syntax: create_parachute word1 word2 word3 [word4|coordinates] -white <hex color> -red <hex color>

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

def encode_10_bit_binary(message, words=8, colors=[mcolors.to_rgba('#FFF'),mcolors.to_rgba('#F00')]):
    '''
    :param message: string or list of numbers and individual characters
    :param words: number of 10 bit words to encode, defaults to 8 to create Mars 80 segement per ring parachute
    :param colors: list of colors to use for 0 and 1 bits
    :return: list of RGBA values, last gore (panel) before padding to end of ring
    '''
    result_str = ''
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
    if type(message) is str:
        message_list = list(message)  # convert string into list of characters
    elif type(message) is list:
        message_list = message
    else:
        raise ValueError('only strings and lists supported')
    if len(message_list) > limit:
        raise ValueError(f'encoded message limited to {limit} characters')
    for character in message_list:
        if type(character) is int:
            result.append(character)
        elif character.isalpha():
            result.append(ord(character.upper())-ord('A')+1)
        else:
            raise ValueError(f"unrecognized character {character} only letters and numbers supported")
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='design a JPL parachute')

    parser.add_argument('message', action='store', nargs='*',
                         default = ['DARE', 'MIGHTY', 'THINGS',34,11,58,'N',118,10,31,'W'],
                         help='message to encode (4 words, each 8 or fewer charactrs)')
    parser.add_argument('-white', action='store', default='#FFF', help='hex color for white panels (default #FFF)')
    parser.add_argument('-red', action='store', default='#F00', help='hex color for red panels (default #F00)')

    args = parser.parse_args()
    message=[]
    lastring=[]
    for ele in args.message:
        if type(ele) is int or len(lastring)>=1:
            if len(message) < 4:
                message.append(lastring)
            lastring.append(ele)
        elif type(ele) is str:
            message.append(ele)

    from pprint import pprint
    pprint(message)

    if len(message) < 4:
        raise ValueError("please include 4 words")

    fig, ax = plt.subplots(figsize=(5, 5), dpi=300)
    ax.axis('equal')
    spacing = [(0.6, 0.45), (1.0, 0.4), (1.2, 0.25), (1.5, 0.18)] # matches Perseverance parachute porportions pretty well.

    start_degrees = 0
    for ring,radius_width in zip(message, spacing):
        if ring in [message[0], message[-1]]:
            start_degrees = 0  # first and last rings start from the top
        panels, last_panel = encode_10_bit_binary(ring, colors=[args.white, args.red])
        radius, width = radius_width
        plot_ring(panels, radius, width, rotate_clockwise_degrees=start_degrees)
        start_degrees+=((last_panel/80.0)*360)

    plt.savefig(f"{'_'.join(message[:3])}.png")
