# The Lost Flag Reloaded - Writeup

## Files related to solving the challenge are in root folder

## Please open issue should you have any questions. It will be added to the respective Q&A section.

Author: S051_Destroy Lai Lai's Machine (aka DLLM)

## Situation

The Lost Flag Reloaded

H0p this time did bought something else ...an oversized LED matrix display. Like last year, we really need to recover an important information on the screen, and this time not only we have the photos of his invention but also a video too! We also hooked up a Logic Analyser to interrogate those ones and zeros. We just hope the bits can run slower.

Can you please help us?

Author: Hop\
Flag Format: PUCTF25{[\x00-\x7F]*}

Hint: N/A

Attachments:\
the_lost_flag_reloaded.tar.gz\
(Stored at ./the_lost_flag_reloaded.tar.gz)

## The Beginning

After downloading and extracting `the_lost_flag_reloaded.tar.gz`, we have:

- 5 images showing the connection of the ESP32 and the logic analyzer (`Connections_*.jpg`)
- Pinout of ESP32 (`ESP32_Pinout.jpg`)
- Config of the logic analyzer (`LA_Screenshot.png`)
- logic analyzer result/trace (`trace.csv`)
- code of of the ESP32 (`TheLostFlagReloaded.ino`)
- video of the ESP32 running the code (`the_lost_flag_reloaded.mp4`)

First thing that came to my mind is just to try look at the video frame by frame to avoid all those analysis, but it seems that the video's frame rate is too low and we can't see the flag clearly.

Sadly then, we actually need to do some analysis.

## The Beginning - checkpoint Q&A

Q - Why does this Q&A look unnecessary?\
A - Because I can't think of any Q&A here

## Matching

Let's match the pins with the channels of the trace shall we?

By looking at `LA_Screenshot.png`

![LA_Screenshot.png](the_lost_flag_reloaded/LA_Screenshot.png)

and the first few lines of `TheLostFlagReloaded.ino`

```cpp
const int LEDPin_OE = 18;
const int LEDPin_LAT = 19;
const int LEDPin_CLK = 21;
const int LEDPin_R1 = 4;
const int LEDPin_G1 = 0;
const int LEDPin_B1 = 2;

const int LEDPin_A = 33;
const int LEDPin_B = 25;
const int LEDPin_C = 26;
const int LEDPin_D = 27;
const int LEDPin_E = 14;
```

We can assume that Channel 1, 2 and 5 are R, G, and B in unknown order, but the order doesn't matter.

We also need the clock though (or else the output will be noisy), which one is CLK?

Let's take a look at the `trace.csv`

```csv
2.928671040, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 0
2.928672480, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0
2.928674840, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0
2.928675600, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0
2.928675920, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 0
2.928677360, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0
2.928679720, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0
2.928680480, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0
2.928682480, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0
2.928685640, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0
2.928687600, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0
2.928690720, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0
2.928691040, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 0
2.928692480, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0
2.928694840, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0
2.928695560, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0
2.928695920, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 0
2.928697320, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0
2.928699720, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0
2.928700480, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0
2.928702480, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0
2.928705600, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0
2.928707640, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0
2.928710320, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0
2.928712280, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0
2.928715400, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0
2.928715720, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 0
2.928717200, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0
2.928719600, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0
2.928720320, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0
2.928720640, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 0
2.928722640, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0
2.928725000, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0
2.928725760, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0
2.928727200, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0
2.928730400, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0
2.928732400, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0
2.928735480, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0
2.928735840, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 0
2.928737280, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0
2.928739640, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0
2.928740360, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0
2.928740680, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 0
2.928742120, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0
2.928743920, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0
```

(I'm not putting the entire trace in here for obvious reasons)

we can see Channel 0 is high for quite a long time, that doesn't look like a clock.\
Channel 1 is colour, definitely not a clock.\
Channel 2 is also colour, also not clock.\
Channel 3 is also high for quite a long time, probably not a clock.\
Channel 4 is also high for quite a long time, skip.\
Channel 5 is colour too, skip.\
Channel 6 is doing a stable 1 0 0 1 0 0 sequance, it looks like a clock.\
Channel 7 is low for quite a long time, nope.\
Channel 8 is high for quite a long time, nope.\
Channel 9 is low for quite a long time, nope.\
Channel 10 is low for quite a long time, nope.

Now we get everything we need. RGB are in Channel 1, 2, 5, and clock is Channel 6

## Matching - checkpoint Q&A

Q - Why only RGB and CLK matters?\
A - RGB is important because it is the signal that actually shows the text out. CLK is important because we need it to distinguish when do the data get taken and outputted.\
OE and LAT is not important because from the LA screenshot, we can see that CLK basically did OE and LAT's job. ABCDE seems to be for debug purposes only.

## Decrypting

We can read the content of a csv file with `panda` and a little python

Before we write the program, it's good to clarify a few things.

1. Only the data when CLK drops from high to low will be used by the display, we can discard those that are not
2. after looking at `TheLostFlagReloaded.ino`'s `displayString` method

```cpp
void displayString(char *str, uint8_t lengthToDisplay, uint8_t color) {
  memset(frameBuffer, 0x00, 16*64);
  for(uint8_t i=0; i<lengthToDisplay; i++) {
    char display = str[i];
    for(uint8_t h=0; h<8; h++) {
      for(uint8_t b=0; b<8; b++) {
        if (font8x8_basic[display][h] & (1 << b)) {
          frameBuffer[h][b + i*8] = color;
        }else{
          frameBuffer[h][b + i*8] = 0x00;
        }
      }
    }
  }
}
```

We can see that the display is 64x16\
3. It would be useless to know the colour of the text, we don't even know which channel specifically are R G and B, so we just need to make the output black&white

Let's write the program (stored in `./emul.py)

```py
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
```

## Decrypting - checkpoint Q&A

Q - Why in the program, when emulating display, checks the display to have length of 65x16 + 6 instead of 64x16?\
A - for each frame, there are 64 pixels columns + a newline character, times 16 pixels rows, plus 6 bytes of clear screen text (`\x1b[H\x1b[J`)

Q - Why only the data when CLK drops from high to low matters?\
A - That's just some protocols thing. It is hard to know if the voltage right now is high or low without reference and calibrations, but it's easy to detect changes in voltage (ie from low to high, or high to low) as the reference is right there. In fact, the output would be the same if it's detecting low to high here (you can try), but I use high to low because thats what most hardware takes in.

## Extracting

If you have hyper reading speed, or you spent some time looking through the generated `output.txt`

You can see the flag is

`PUCTF25{50rry_1_h4v3_70_cr3473_my_0wn_d15pl4y_dr1v3r_7e3ea4ed8f0b77f6}`

## Extracting - checkpoint Q&A

Q - I don't have hyper reading speed\
A - Just slowly scroll through [output.txt](output.txt), or change the `sleep(0.01)` in the program to a longer time and look again
