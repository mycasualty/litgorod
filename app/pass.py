from string import ascii_uppercase
from itertools import cycle

ps = list('WGVSXYQ')[::-1]

letter = ps.pop()
ss = ''
c =10
for l in cycle(ascii_uppercase):
    if l == letter:
        c = 0
    elif c == 4:
        ss += l
        if ps:
            letter = ps.pop()
            c = 10
        else:
            print(ss)
            input('all')
    c += 1
