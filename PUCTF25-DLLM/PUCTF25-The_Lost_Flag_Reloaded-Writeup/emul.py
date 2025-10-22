import pandas as pd
from time import sleep

df = pd.read_csv('the_lost_flag_reloaded/trace.csv')

CLK = df[" Channel 6"]
pixel = df[' Channel 1'] | df[' Channel 2'] | df[' Channel 5']

print("\x1b[H\x1b[J") #clear screen

data = []
frame = "\x1b[H\x1b[J"
with open('output.txt', 'w') as f:
    for i in range(len(df)-1):
        if CLK[i] == 1 and CLK[i+1] == 0:
            data.append(pixel[i])
        if len(data) == 64:
            line = ""
            for j in data:
                if j:
                    line += '#'
                else:
                    line += '.'
            line += "\n"
            f.write(line)
            frame += line
            if len(frame) == 1046: #(64+1)*16+6
                print(frame)
                sleep(0.01)
                frame = "\x1b[H\x1b[J"
            data = []

