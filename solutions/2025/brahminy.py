# type: ignore
"""
The Brahminy: a Python one-liner that solves Advent of Code 2025.
https://adventofcode.com/2025

Written by Josiah Winslow
https://github.com/WinslowJosiah

Inspired by Sav Bell's programs "The Beast" and "The Basilisk"!
https://github.com/savbell/advent-of-code-one-liners

Progress:
| Day | Pt1 | Pt2 |
| --- | --- | --- |
|  01 |  Y  |  Y  |
|  02 |  Y  |  Y  |
|  03 |  Y  |  Y  |
|  04 |  Y  |  Y  |
|  05 |  Y  |  Y  |
|  06 |  N  |  N  |
|  07 |  N  |  N  |
|  08 |  N  |  N  |
|  09 |  N  |  N  |
|  10 |  N  |  N  |
|  11 |  N  |  N  |
|  12 |  N  |  N  |
"""

# NOTE Make sure your input files exist at these locations. (Also, this
# part technically makes this program not a "one-liner", but the input
# file locations could easily be hardcoded.)
z = {
    1: r"day01/input.txt",
    2: r"day02/input.txt",
    3: r"day03/input.txt",
    4: r"day04/input.txt",
    5: r"day05/input.txt",
    6: r"day06/input.txt",
    7: r"day07/input.txt",
    8: r"day08/input.txt",
    9: r"day09/input.txt",
    10: r"day10/input.txt",
    11: r"day11/input.txt",
    12: r"day12/input.txt",
}

# THE BRAHMINY
(lambda it,re,_g:[*map(lambda a:print(*a()),(lambda:((A:=[(int(a[1:]),"R">a)for a in open(z[1])],a:=50)and"Day 1:",*map(sum,zip(*([abs(d*(a<1)+((b:=a+c-2*c*d)-d)//100),(a:=b%100)<1][::-1]for c,d in A)))),lambda:((B:=[{*(a:=[*map(int,b.split("-"))]),*range(*a)}for b in open(z[2]).read().split(",")])and"Day 2:",*(sum(a for a in it.chain(*B)if re.match(fr"^(.+)\1{b}$",str(a)))for b in("","+"))),lambda:((C:=[*map(str.strip,open(z[3]))])and"Day 3:",*(sum(int((a:=lambda b,c:c<2 and max(b)or(d:=max(b[:1-c]))+a(b[b.find(d)+1:],c-1))(b,c))for b in C)for c in(2,12))),lambda:((D:={*_g(open(z[4]),".")},a:=D)and"Day 4:",len((b:=lambda:[c for c in a if len(a&{c-1,c+1,c-1j,c+1j,c-1-1j,c-1+1j,c+1-1j,c+1+1j})<4])()),len((a:=D)-[a:=a-{*b()}for _ in iter(b,[])][-1])),lambda:((E:=[*map(str.split,open(z[5]).read().split("\n\n"))],a:=sorted([*map(int,a.split("-"))]for a in E[0]))and"Day 5:",sum(any(a[b:=0]<=int(c)<=a[1]for a in a)for c in E[1]),sum(-max(a-1,b)+(b:=c)for a,c in a if c>b))))])(*map(__import__,("itertools","re")),lambda a,b="":{c*1j+e:f for c,d in enumerate(a)for e,f in enumerate(d.strip())if f not in b})