#!/usr/bin/env python3
# red = 1, white = 0
# source: https://www.youtube.com/watch?v=ZbTJ_YCTDLI&ab_channel=NASAJetPropulsionLaboratory
chute = [
    "RRRRRRRRRRRRRRRRRRRRwwwwwwwRwwwwwwwwwwwRwwwwwRwwRwwwwwwwwRwRwwwRRRRRRRRRRRRRRRRR",
    "wwwRRRRRRRRRRRRRRRRRwwwwwwRRwRwwwwwwRwwRwwwwwwwRRRwwwwwwRwwwwwwwwRwRwwwwwwwRRwwR",
    "wwwwwRwRwwwwwwwwRwwwwwwwwwRwwRwwwwwwRRRwwwwwwwwRRRwwwwwRwwRRwwwRRRRRRRRRRRRRRRRR",
    "wwwwRwwwRwwwwwwwRwRRwwwwRRRwRwwwwwwwRRRwwwwRRRwRRwwwwwwwRwRwwwwwwRRRRRwwwwwRwRRR"
];

chunk_size=10 # characters are in blocks of 10 , with first 3 gores always white in characters
ring_no=0
for ring in chute:
    ring_no+=1
    data = []
    panels=ring.replace('R','1').replace('w','0')
    for i in range(0, len(panels), chunk_size):
        character_binary=panels[i:i + chunk_size]
        character_binary=character_binary[3:] # first 3 (white) panels are character separators, can be ignored
        chunk_int = int(character_binary, 2)  # convert binary to integer
        chunk_ascii = chr(chunk_int + 64)     # convert to an ascii character (65 = A)
        if chunk_int == 127:
            # blocks of 10 red panels act as stops, should not be included in message.
            continue
        elif ring_no < 4: # inner 3 rings are letters
            data.append({'ascii': chunk_ascii,
                         'int': chunk_int,
                         'binary': character_binary,
                         })
        else:  # outer ring includes integers and ascii characters
            if chunk_ascii in ['N', 'E', 'S', 'W'] :
                data.append({'ascii': chunk_ascii,
                             'int': chunk_int,
                             'binary': character_binary,
                             })
            else:
                data.append({'ascii': str(chunk_int),
                             'int': ' ',
                             'binary': character_binary,
                             })

    for line in ['binary', 'int', 'ascii']:
        for c in data:
            print(f"{c[line]:^7}", end=' ')
        print("")
