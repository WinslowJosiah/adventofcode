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
|  06 |  Y  |  Y  |
|  07 |  Y  |  Y  |
|  08 |  Y  |  Y  |
|  09 |  Y  |  Y  |
|  10 |  Y  |  Y  |
|  11 |  Y  |  Y  |
|  12 |  Y  | N/A |
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
    10: r"day10/test.txt",  # very slow on real input!
    11: r"day11/input.txt",
    12: r"day12/input.txt",
}

# THE BRAHMINY
(lambda ft,it,ma,re,_e,_i,_m,_o,_p,_s,_u:[*_m(lambda a:print(*a()),(lambda:((A:=[(_i(a[1:]),"R">a)for a in _o(z[1])],a:=50)and"Day 1:",*_m(_u,zip(*([abs(d*(a<1)+((b:=a+c-2*c*d)-d)//100),(a:=b%100)<1][::-1]for c,d in A)))),lambda:((B:=[{*(a:=[*_m(_i,_p(b,"-"))]),*range(*a)}for b in _p(_o(z[2]).read(),",")])and"Day 2:",*(_u(a for a in it.chain(*B)if re.match(fr"^(.+)\1{b}$",str(a)))for b in("","+"))),lambda:((C:=[*_m(str.strip,_o(z[3]))])and"Day 3:",*(_u(_i((a:=lambda b,c:c<2 and max(b)or(d:=max(b[:1-c]))+a(b[b.find(d)+1:],c-1))(b,c))for b in C)for c in(2,12))),lambda:((D:={a*1j+c for a,b in _e(_o(z[4]))for c,d in _e(b)if"."<d},a:=D)and"Day 4:",len((b:=lambda:[c for c in a if len(a&{c-1,c+1,c-1j,c+1j,c-1-1j,c-1+1j,c+1-1j,c+1+1j})<4])()),len((a:=D)-[a:=a-{*b()}for _ in iter(b,[])][-1])),lambda:((E:=[*_m(_p,_p(_o(z[5]).read(),"\n\n"))],a:=_s([*_m(_i,_p(a,"-"))]for a in E[0]))and"Day 5:",_u(any(a[b:=0]<=_i(c)<=a[1]for a in a)for c in E[1]),_u(-max(a-1,b)+(b:=c)for a,c in a if c>b)),lambda:((F:=[*_p(_o(z[6]).read(),"\n")])and"Day 6:",*(_u(({"+":_u,"*":ma.prod}[b])(_m(_i,a))for a,b in zip(c,_p(F[-1])))for c in(zip(*_m(_p,F[:-1])),[["".join(a)for a in c]for b,c in it.groupby(zip(*F[:-1]),key=lambda c:{*c}!={" "})if b]))),lambda:((a:=0)or"Day 7:",_u((b:=9**25,c:=1)and _u((c:=b*c,d:=(e>"S")*a//c%b*c,a:=a+d*~-b+(e=="S")*c+d//b)and d>0 for e in e)for e in _o(z[7])),a%~-b),lambda:((a:=0,b:=0,c:={(c:=(*_m(_i,_p(a,",")),)):frozenset([c])for a in _o(z[8])})and"Day 8:",[b or(c.update(zip(d:=c[f]|c[g],[d]*len(d))),999-e or(a:=ma.prod(_s(_m(len,{*c.values()}))[-3:])),d=={*c}and(b:=f[0]*g[0]))for e,(f,g)in _e(_s(it.combinations(c,2),key=lambda a:ma.dist(*a)))]and a,b),lambda:((I:=[[*_m(_i,_p(a,","))]for a in _o(z[9])])and"Day 9:",(a:=lambda a:(a[2]-a[0]+1)*(a[3]-a[1]+1))((b:=[_s([(min(b,d),min(c,e),max(b,d),max(c,e))for(b,c),(d,e)in f],key=a)[::-1]for f in(it.combinations(I,2),it.pairwise(I+I))])[0][0]),a(next(c for c in b[0]if all(any([c[0]>=f,c[1]>=g,c[2]<=d,c[3]<=e])for d,e,f,g in b[1])))),lambda:((J:=[*_o(z[10],"rb")])and"Day 10:",*_m(_u,zip(*[((a:=lambda b,c=0,d=2:999*(-1 in[*b])or f[d:]and min(a([b-(a in f[d-1])for a,b in _e(b,48)],c,d+1)+1,a(b,c,d+1))or 999*any(a%2 for a in b)or c*any(b)and 2*a([a//2 for a in b],1))((f:=[a[1:-1]for a in b.split()])[0]),a([*_m(_i,f[-1].split(b","))],1))for b in J]))),lambda:((K:=[*_o(z[11])])and"Day 11:",(a:=ft.cache(lambda b,c=3,d="out":b==d[:c]or _u(a(b,c+(d in"dac fft"),e[:3])for e in K if" "+d in e)))("you"),a("svr",1)),lambda:("Day 12:",_u(9*_u((a:=[*_m(_i,re.split(r"\D+",b.strip()))])[2:])<=a[0]*a[1]for b in[*_o(z[12])][30:]))))])(*map(__import__,("functools","itertools","math","re")),enumerate,int,map,open,str.split,sorted,sum)