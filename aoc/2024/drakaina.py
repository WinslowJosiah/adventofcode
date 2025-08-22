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
|  12 |  Y  |  Y  |
|  13 |  Y  |  Y  |
|  14 |  Y  |  Y  |
|  15 |  Y  |  Y  |
|  16 |  Y  |  Y  |
|  17 |  Y  |  Y  |
|  18 |  Y  |  Y  |
|  19 |  Y  |  Y  |
|  20 |  Y  |  Y  |
|  21 |  Y  |  Y  |
|  22 |  Y  |  Y  |
|  23 |  Y  |  Y  |
|  24 |  Y  |  Y  |
|  25 |  Y  | N/A |
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
    6: r"day06/example.txt",  # slow-ish on real input
    7: r"day07/input.txt",
    8: r"day08/input.txt",
    9: r"day09/input.txt",
    10: r"day10/input.txt",
    11: r"day11/input.txt",
    12: r"day12/input.txt",
    13: r"day13/input.txt",
    14: r"day14/example.txt",  # slow-ish on real input
    15: r"day15/example1.txt",  # slow-ish on real input
    16: r"day16/input.txt",
    17: r"day17/input.txt",
    18: r"day18/input.txt",
    19: r"day19/input.txt",
    20: r"day20/example.txt",  # slow-ish on real input
    21: r"day21/input.txt",
    22: r"day22/example2.txt",  # slow-ish on real input
    23: r"day23/input.txt",
    24: r"day24/input.txt",
    25: r"day25/input.txt",
}

# THE DRAKAINA
(lambda z:print(*(lambda A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y:["Day 1:",sum(abs(int(a)-int(b))for a,b in zip(*map(sorted,A))),sum(int(a)*A[1].count(a)for a in A[0]),"\nDay 2:",sum(map(c:=lambda a:any(all(1<=b-a<=3 for a,b in zip(b,b[1:]))for b in(a,a[::-1])),B)),sum(any(c(a[:b]+a[b+1:])for b in range(len(a)))for a in B),"\nDay 3:",*[sum(int(a)*int(b)for a,b in z("re").findall(r"mul\((\d+),(\d+)\)",c))for c in(C,z("re").sub(r"(?s)don't\(\).*?(do\(\)|$)","",C))],(a:=len(D[0])-2,)and"\nDay 4:",sum(len(z("re").findall("(?s)(?="+f".{{{a}}}".join(b)+")","".join(D)))for a in(0,a,a+1,a+2)for b in("XMAS","SAMX")),sum(len(z("re").findall(f"(?s)(?=%s.%s.{{{a}}}A.{{{a}}}%s.%s)"%tuple(b),"".join(D)))for b in("MMSS","SSMM","MSMS","SMSM")),(a:={tuple(a.split("|"))for a in E[0].split()})and"\nDay 5:",*[sum(int(sorted(c,key=lambda d:len([e for e in c if(d,e)in a]))[len(c)//2])for b in E[1].split()if(c:=b.split(","))and d==any(a>={d}for d in z("itertools").combinations(c[::-1],2)))for d in(0,1)],(a:=min(a for a in F if"^"==F[a]))and"\nDay 6:",len(b:=(c:=lambda d:(e:=a,f:=-1j,g:=set(),[(g.add((e,f)),(f:=f*1j)if"#"==d.get(e+f)else(e:=e+f))for _ in z("itertools").takewhile(lambda _:e in d and(e,f)not in g,F)])and({g[0]for g in g},(e,f)in g))(F)[0]),sum(c(F|{b:"#"})[1]for b in b),"\nDay 7:",*[sum(b[0]for b in G if(a:=lambda b,c,d,e:c==b[d]if d==1 else e and str(c).endswith(str(b[d]))and a(b,int("0"+str(c)[:-len(str(b[d]))]),d-1,e)or 0==c%b[d]and a(b,c//b[d],d-1,e)or c>b[d]and a(b,c-b[d],d-1,e))(b,b[0],len(b)-1,c))for c in(0,1)],"\nDay 8:",*[len({f for e in H[0]for(a,b),(c,d)in z("itertools").permutations(e,2)for g in range(h,2 if h else max(max(H[1])))if(f:=(a+(a-c)*g,b+(b-d)*g))in H[1]})for h in(1,0)],(a:=[b:=0]+[(b:=b+c)for c in I],b:=[d*(c&1)for c,d in enumerate(I)],c:={},d:=I[:],e:=len(d)-1)and"\nDay 9:",sum((f&1==0 or(e:=next((e for e in range(e,f,-2)if d[e]),f),d.__setitem__(e,d[e]-1)))and[f,e][f&1]//2*(a[f]+g)*(f<e)for f,g in enumerate(d[1:],1)for g in range(g)),sum((f:=next((f for f in range(c.get(I[g],0),g)if b[f]>=I[g]),g),b.__setitem__(f,b[f]-I[g]),c:=c|{I[g]:f},a.__setitem__(f,a[f]+I[g]))and(g//2*((2*a[f]-I[g]-1)*I[g]//2))for g in range(len(I)-1,-1,-2)),(a:=[(b:=lambda c,d,e:e+([]if d!=int(J.get(c,-1))else[c]if d>=9 else b(c+1,(d:=d+1),e)+b(c-1,d,e)+b(c+1j,d,e)+b(c-1j,d,e)))and b(c,0,[])for c in J])and"\nDay 10:",*[sum(map(len,a))for a in(map(set,a),a)],"\nDay 11:",*[sum(z("functools").reduce(lambda a,_:(b:=z("collections").Counter())or[b.update({d:a[c]})for c in a if(f:=str(c),g:=len(f)//2)for d in([1]if c==0 else[c*2024]if 1&len(f)else[int(f[:g]),int(f[g:])])]and b,range(e),K).values())for e in(25,75)],(a:=[],b:=set(),[(c:=set(),d:={f},[g==L.get(e:=d.pop(),0)and(b.add(e),c:=c|{e},d:=d|{e+f for f in(1,-1,1j,-1j)}-b)for _ in z("itertools").takewhile(lambda _:d,L)],a:=a+[c])for f,g in L.items()if not{f}&b])and"\nDay 12:",sum(len(b)*sum(not{d+c}&b for c in(1,-1,1j,-1j)for d in b)for b in a),sum(len(b)*sum(not(f:={e+c,e+d})&b or f<=b and not{e+d+c}&b for c in(1j,-1j)for d in(1,-1)for e in b)for b in a),"\nDay 13:",sum((a:=lambda b,c,d,e,f,g:0 if(i:=divmod(f-b*(h:=divmod(e*f-d*g,b*e-c*d))[0],d))[1]or h[1]else int(3*h[0]+i[0]))(*b)for b in M),sum(a(*(b[:4]+[b[4]+1e13,b[5]+1e13]))for b in M),(a:=max(a[0]for a,_ in N)+1,b:=max(b[1]for b,_ in N)+1,c:=[z("math").prod(({0:0,1:0,2:0,3:0}|z("collections").Counter(i//(b//2+1)*2+h//(a//2+1)for(d,e),(f,g)in N if(h:=(d+f*j)%a)!=a//2 and(i:=(e+g*j)%b)!=b//2)).values())for j in range(max(101,a*b+1))])and"\nDay 14:",c[100],min(range(a*b+1),key=c.__getitem__),"\nDay 15:",*[(a:=x(f.split()),b:=min(b for b in a if"@"==a[b]),[(c:=[1,-1,1j,-1j,0]["><v^".find(f)],d:={**a},(e:=lambda a:(f:=d[b:=a+c])=="#"or f in"[]"and e(b+92-ord(f))or f in"O[]"and e(b)or d.update({a:d[b],b:d[a]}))(b)or(a:=d,b:=b+c))for f in O[1]])and sum((a[b]in"O[")*int(b.real+b.imag*100)for b in a)for f in(O[0],O[0].translate({35:"##",46:"..",79:"[]",64:"@."}))],(a:=(b:=min(a for a in P if"S"==P[a])).real,b:=b.imag,c:=(d:=min(c for c in P if"E"==P[c])).real,d:=d.imag,e:={},f:=[(0,1,0,a,b)],g:={},[(f:=[])if(c,d)==(h:=z("heapq").heappop(f))[3:]else[(i:=h[0]+k)<(j:=e.get(l,i+1))and(e.__setitem__(l,i),z("heapq").heappush(f,(i,*l)),g.__setitem__(l,{h[1:]}))or i!=j or g[l].add(h[1:])for k,l in[(1,(*h[1:3],h[1]+h[3],h[2]+h[4])),(1000,(h[2],-h[1],*h[3:])),(1000,(-h[2],h[1],*h[3:]))][P[h[1]+h[3]+(h[2]+h[4])*1j]=="#":]]for _ in z("itertools").takewhile(lambda _:f,[*P]*2)])and"\nDay 16:",h[0],len((c:=lambda d:{d[2:]}.union(*[c(p)for p in g[d]if(a,b)!=d[2:]]))(h[1:])),(a:=lambda b:filter(lambda c:c is not None,[(d:=lambda e:[0,1,2,3,*b][e],e:=Q[1][b[3]][1],[lambda:b.__setitem__(0,b[0]>>d(e)),lambda:b.__setitem__(1,b[1]^e),lambda:b.__setitem__(1,d(e)&7),lambda:b[0]and b.__setitem__(3,e-1),lambda:b.__setitem__(1,b[1]^b[2]),lambda:d(e)&7,lambda:b.__setitem__(1,b[0]>>d(e)),lambda:b.__setitem__(2,b[0]>>d(e))][Q[1][b[3]][0]](),b.__setitem__(3,b[3]+1))[2]for _ in z("itertools").takewhile(lambda _:b[3]<len(Q[1]),z("itertools").count(0))]))and"\nDay 17:",",".join(map(str,a([*Q[0],0]))),(b:=[*z("itertools").chain(*Q[1])],c:=next(b for b in Q[1]if b[0]==0)[1],d:={b:next(a([b,*Q[0][1:],0]))for b in range(1<<7+c)},e:=lambda f,g:[i for h in range(1<<c)if d[f>>c*g|h<<7]==b[g]for i in e(f|h<<7+c*g,g+1)]if g<len(b)else[f])and min([h for f,g in d.items()if g==b[0]for h in e(f,1)],default=0),(a:=complex(max(a.real for a in R),max(a.imag for a in R)),b:=lambda c:(c:=set(R[:c]),d:=[(0,0)],[c.add(g)or d.append((e+1,g))for e,f in z("itertools").takewhile(lambda g:g[1]!=a,d)for g in(f+1,f-1,f+1j,f-1j)if 0<=g.real<=a.real and 0<=g.imag<=a.imag and not{g}&c])and next((c[0]for c in d if c[1]==a),float("inf")))and"\nDay 18:",b(1024),(c:=R[z("bisect").bisect_left(range(len(R)),float("inf"),key=b)-1])and",".join(map(str,map(int,(c.real,c.imag)))),"\nDay 19:",*[sum(map(d,map(a:=z("functools").cache(lambda b:b==""or sum(a(b[len(c):])for c in S[0]if b[:len(c)]==c)),S[1])))for d in(bool,int)],(a:={next(a for a in T if"S"==T[a]):0},b:=[*a],[(a.__setitem__(d,a[c]+1),b.append(d))for c in b for d in(c+1,c-1,c+1j,c-1j)if T.get(d,"#")!="#"and d not in a],c:=lambda d:sum(99<a.get(g+e+f*1j,0)-a[g]-abs(e)-abs(f)for e in range(-d,d+1)for f in range(abs(e)-d,d-abs(e)+1)for g in a))and"\nDay 20:",c(2),c(20),(a:=z("functools").cache(lambda b,c:(d:=[divmod("789456123.0A<v>".find(e),3)for e in "A"+b+"A"])and c<1 or sum(a(("<"*(f-h)+"v0"[g<e]*abs(g-e)+">"*(h-f))[::0<(f|g^3)*(h|e^3)or-1],c-1)for(e,f),(g,h)in zip(d,d[1:]))))and"\nDay 21:",*[sum(int(b[:3])*a(b[:3],c)for b in U)for c in(4,27)],(a:=lambda b:(b:=b^(b<<6)&16777215,b:=b^(b>>5)&16777215)and b^(b<<11)&16777215)and"\nDay 22:",sum(z("functools").reduce(lambda b,_:a(b),range(2000),b)for b in V),(b:=z("collections").Counter(),[(c:={},d:=[e],[d.append(a(d[-1]))for _ in range(2000)],d:=[*map(lambda e:e%10,d)],[c.setdefault(tuple(f-e for e,f in zip(d[e:e+5],d[e+1:e+5])),d[e+4])for e in range(len(d)-4)],b.update(c))for e in V])and max(b.values()),"\nDay 23:",len(set(frozenset([a,c,d])for a,b in W.items()for c,d in z("itertools").combinations(b,2)if{c}<=W[d]and"t"==a[0])),(a:=[],b:=lambda c,d,e:[(b(c|{f},d&W[f],e&W[f]),d.remove(f),e.add(f))for f in set(d)]if d|e else a.append(c),b(set(),set(W),set()))and",".join(sorted(max(a,key=len))),(a:=X[0]|{b:lambda b=b,c=c:getattr(a[c[1]](),f"__{c[0].lower()}__")(a[c[2]]())for b,c in X[1].items()})and"\nDay 24:",int("".join(str(c())for b,c in sorted(a.items())if"z"==b[0])[::-1],2),",".join(sorted(b for b,(c,*d)in X[1].items()if(e:=any(f=="OR"for e,(f,*g)in X[1].items()if b in(e,*g)),)and[b[0]=="z"or not(e or"x00"in d),b[0]!="z"and all(c!=f[0]for c in"xy"for f in d)or e][c=="XOR"])),"\nDay 25:",sum(all(a+b<8 for a,b in zip(c,d))for c in Y[0]for d in Y[1])])([*zip(*map(str.split,open(y[1]).readlines()))],[[*map(int,a)]for a in map(str.split,open(y[2]).readlines())],open(y[3]).read(),open(y[4]).readlines(),open(y[5]).read().split("\n\n"),(x:=lambda a:{b*1j+d:e for b,c in enumerate(a)for d,e in enumerate(c.strip())})(open(y[6])),[[*map(int,a.replace(":","").split())]for a in open(y[7]).readlines()],(a:={},b:=set())and[(f!="."and a.setdefault(f,set()).add((c,e)),b.add((c,e)))for c,d in enumerate(open(y[8]).readlines())for e,f in enumerate(d.strip())]and(a.values(),b),[*map(int,open(y[9]).read().strip())],x(open(y[10])),z("collections").Counter(map(int,open(y[11]).read().split())),x(open(y[12])),[[*z("itertools").chain.from_iterable(map(int,b.groups())for a in c.split("\n")if(b:=z("re").search(r"(\d+).+?(\d+)",a)))]for c in open(y[13]).read().split("\n\n")],[[[*map(int,a)]for a in z("re").findall(r"(-?\d+),(-?\d+)",b)]for b in open(y[14]).readlines()],open(y[15]).read().split("\n\n"),x(open(y[16])),(a:=open(y[17]).read().splitlines(),b:=[*map(lambda c:c.split(": ")[1],(*a[:3],a[-1]))])and([*map(int,b[:3])],[*zip(*[iter(map(int,b[3].split(",")))]*2)]),[complex(*map(int,a.split(",")))for a in open(y[18]).readlines()],(a:=open(y[19]).read().splitlines(),)and(a[0].split(", "),a[2:]),x(open(y[20])),[*open(y[21])],[*map(int,open(y[22]).read().splitlines())],(a:=z("collections").defaultdict(set),[(c:=b.split("-"),a[c[0]].add(c[1]),a[c[1]].add(c[0]))for b in open(y[23]).read().splitlines()])and a,(a:=[[a.replace(":", "").split()for a in b.split("\n")]for b in open(y[24]).read().split("\n\n")],)and({b:lambda c=c:int(c)for b,c in a[0]},{e:(c,b,d)for b,c,d,_,e in a[1]}),(a:=[],b:=[],[(a,b)[set(d[0])=={"#"}].append([c.count("#")for c in zip(*d.split())])for d in open(y[25]).read().split("\n\n")])and(a,b))))(__import__)
