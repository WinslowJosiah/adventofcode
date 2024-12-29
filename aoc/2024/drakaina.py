# type: ignore
"""
The Drakaina: a Python one-liner that solves Advent of Code 2024.
https://adventofcode.com/2024

Written by Josiah Winslow
https://github.com/WinslowJosiah

Inspired by Sav Bell's programs "The Beast" and "The Basilisk"!
https://github.com/savbell/advent-of-code-one-liners

Thanks to u/azzal07 for providing a faster Day 9 solution!
https://reddit.com/u/azzal07

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
|  12 |  N  |  N  |
"""

# NOTE Make sure your input files exist at these locations. (Also, this
# part technically makes this program not a "one-liner", but the input
# file locations could easily be hardcoded.)
y = {
    1: r"day01/input.txt",
    2: r"day02/input.txt",
    3: r"day03/input.txt",
    4: r"day04/input.txt",
    5: r"day05/input.txt",
    6: r"day06/example.txt",  # slow on real input
    7: r"day07/input.txt",
    8: r"day08/input.txt",
    9: r"day09/input.txt",
    10: r"day10/input.txt",
    11: r"day11/input.txt",
    # 12: r"day12/input.txt",
}

# THE DRAKAINA
(lambda z:print(*(lambda A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y:["Day 1:",sum(abs(int(a)-int(b))for a,b in zip(*map(sorted,A))),sum(int(a)*A[1].count(a)for a in A[0]),"\nDay 2:",sum(map(c:=lambda a:any(all(1<=b-a<=3 for a,b in zip(b,b[1:]))for b in(a,a[::-1])),B)),sum(any(c(a[:b]+a[b+1:])for b in range(len(a)))for a in B),"\nDay 3:",*[sum(int(a)*int(b)for a,b in z("re").findall(r"mul\((\d+),(\d+)\)",c))for c in(C,z("re").sub(r"(?s)don't\(\).*?(do\(\)|$)","",C))],[a:=len(D[0])-2,"\nDay 4:"][1],sum(len(z("re").findall("(?s)(?="+f".{{{a}}}".join(b)+")","".join(D)))for a in(0,a,a+1,a+2)for b in("XMAS","SAMX")),sum(len(z("re").findall(f"(?s)(?=%s.%s.{{{a}}}A.{{{a}}}%s.%s)"%tuple(b),"".join(D)))for b in ("MMSS","SSMM","MSMS","SMSM")),(a:={tuple(a.split("|"))for a in E[0].split()})and"\nDay 5:",*[sum(int(sorted(c,key=lambda d:len([e for e in c if(d,e)in a]))[len(c)//2])for b in E[1].split()if(c:=b.split(","))and d==int(any(d in a for d in z("itertools").combinations(c[::-1], 2))))for d in(0,1)],(a:=min(b for b in F if"^"==F[b]))and"\nDay 6:",(b:=lambda c:(d:=a,e:=-1,f:=set(),z("collections").deque(((f:=f|{(d,e)},(e:=e*-1j)if c.get(d+e)=="#"else(d:=d+e))for _ in z("itertools").takewhile(lambda _:d in c and(d,e)not in f,z("itertools").count())),maxlen=0))and({f[0]for f in f},(d,e)in f))and len(g:=b(F)[0]),sum(b(F|{g:"#"})[1]for g in g),(a:=lambda b,c,d,e:c==b[d]if d==1 else e and str(c).endswith(str(b[d]))and a(b,int("0"+str(c)[:-len(str(b[d]))]),d-1,e)or 0==c%b[d]and a(b,c//b[d],d-1,e)or c>b[d]and a(b,c-b[d],d-1,e))and"\nDay 7:",*[sum(b[0]for b in G if a(b,b[0],len(b)-1,c))for c in(0,1)],"\nDay 8:",*[len({f for e in H[0]for(a,b),(c,d)in z("itertools").permutations(e,2)for g in range(h,2 if h else max(max(H[1])))if(f:=(a+(a-c)*g,b+(b-d)*g))in H[1]})for h in(1,0)],(a:=[b:=0]+[(b:=b+c)for c in I],b:=[d*(c&1)for c,d in enumerate(I)],c:={},d:=I[:],e:=len(d)-1)and"\nDay 9:",sum((f&1==0 or(e:=next((e for e in range(e,f,-2)if d[e]),f),d.__setitem__(e,d[e]-1)))and[f,e][f&1]//2*(a[f]+g)*(f<e)for f,g in enumerate(d[1:],1)for g in range(g)),sum((f:=next((f for f in range(c.get(I[g],0),g)if b[f]>=I[g]),g),b.__setitem__(f,b[f]-I[g]),c:=c|{I[g]:f},a.__setitem__(f,a[f]+I[g]))and(g//2*((2*a[f]-I[g]-1)*I[g]//2))for g in range(len(I)-1,-1,-2)),(a:=[(b:=lambda c,d,e:e+([]if d!=J.get(c,b)else[c]if d>=9 else b(c+1,(d:=d+1),e)+b(c-1,d,e)+b(c+1j,d,e)+b(c-1j,d,e)))and b(c,0,[])for c in J])and"\nDay 10:",*[sum(map(len,a))for a in (map(set,a),a)],"\nDay 11:",*[sum(z("functools").reduce(lambda a,_:(b:=z("collections").Counter())or[b.update({d:a[c]})for c in a for d in([1]if c==0 else[c*2024]if 1&len(str(c))else[int(str(c)[:len(str(c))//2]),int(str(c)[len(str(c))//2:])])]and b,range(e),K).values())for e in(25,75)]])([*zip(*map(str.split,open(y[1]).readlines()))],[[*map(int,a)]for a in map(str.split,open(y[2]).readlines())],open(y[3]).read(),open(y[4]).readlines(),open(y[5]).read().split("\n\n"),{a+c*1j:d for a,b in enumerate(open(y[6]))for c,d in enumerate(b.strip())},[[*map(int,a.replace(":","").split())]for a in open(y[7]).readlines()],(a:={},b:=set())and[(f!="."and a.setdefault(f,set()).add((c,e)),b.add((c,e)))for c,d in enumerate(open(y[8]).readlines())for e,f in enumerate(d.strip())]and(a.values(),b),list(map(int,open(y[9]).read().strip())),{a+c*1j:int(d)for a,b in enumerate(open(y[10]))for c,d in enumerate(b.strip())},z("collections").Counter(map(int,open(y[11]).read().split())),None,None,None,None,None,None,None,None,None,None,None,None,None,None)))(__import__)