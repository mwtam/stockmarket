#!/usr/bin/env python3

def main():
    info = []

    P1 = 0
    P1M = 1
    P1S = 2
    P2 = 3
    P2M = 4
    P2S = 5
    N = 6
    P = 7

    #target = "ID:trend_1"
    target = "ID:val_1"

    with open('deal.log', 'r') as f:
        for i, l in enumerate(f):
            l = l.strip()
            deal = l.split('\t')

            if deal[P1] == target:
                print(f'{i}\t{deal[P1M]}\t{deal[P1S]}\tB\t{deal[N]}\t{deal[P]}')
            if deal[P2] == target:
                print(f'{i}\t{deal[P2M]}\t{deal[P2S]}\tS\t{deal[N]}\t{deal[P]}')

if __name__ == "__main__":
    main()

