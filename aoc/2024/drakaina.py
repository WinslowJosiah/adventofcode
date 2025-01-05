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
|  17 |  N  |  N  |
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
    # 17: r"day17/input.txt",
}

# THE DRAKAINA
(lambda z:print(*(lambda A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y:["Day 1:",sum(abs(int(a)-int(b))for a,b in zip(*map(sorted,A))),sum(int(a)*A[1].count(a)for a in A[0]),"\nDay 2:",sum(map(c:=lambda a:any(all(1<=b-a<=3 for a,b in zip(b,b[1:]))for b in(a,a[::-1])),B)),sum(any(c(a[:b]+a[b+1:])for b in range(len(a)))for a in B),"\nDay 3:",*[sum(int(a)*int(b)for a,b in z("re").findall(r"mul\((\d+),(\d+)\)",c))for c in(C,z("re").sub(r"(?s)don't\(\).*?(do\(\)|$)","",C))],[a:=len(D[0])-2,"\nDay 4:"][1],sum(len(z("re").findall("(?s)(?="+f".{{{a}}}".join(b)+")","".join(D)))for a in(0,a,a+1,a+2)for b in("XMAS","SAMX")),sum(len(z("re").findall(f"(?s)(?=%s.%s.{{{a}}}A.{{{a}}}%s.%s)"%tuple(b),"".join(D)))for b in("MMSS","SSMM","MSMS","SMSM")),(a:={tuple(a.split("|"))for a in E[0].split()})and"\nDay 5:",*[sum(int(sorted(c,key=lambda d:len([e for e in c if(d,e)in a]))[len(c)//2])for b in E[1].split()if(c:=b.split(","))and d==any(a>={d}for d in z("itertools").combinations(c[::-1],2)))for d in(0,1)],(a:=min(a for a in F if"^"==F[a]))and"\nDay 6:",len(b:=(c:=lambda d:(e:=a,f:=-1j,g:=set(),[(g.add((e,f)),(f:=f*1j)if"#"==d.get(e+f)else(e:=e+f))for _ in z("itertools").takewhile(lambda _:e in d and(e,f)not in g,F)])and({g[0]for g in g},(e,f)in g))(F)[0]),sum(c(F|{b:"#"})[1]for b in b),"\nDay 7:",*[sum(b[0]for b in G if(a:=lambda b,c,d,e:c==b[d]if d==1 else e and str(c).endswith(str(b[d]))and a(b,int("0"+str(c)[:-len(str(b[d]))]),d-1,e)or 0==c%b[d]and a(b,c//b[d],d-1,e)or c>b[d]and a(b,c-b[d],d-1,e))(b,b[0],len(b)-1,c))for c in(0,1)],"\nDay 8:",*[len({f for e in H[0]for(a,b),(c,d)in z("itertools").permutations(e,2)for g in range(h,2 if h else max(max(H[1])))if(f:=(a+(a-c)*g,b+(b-d)*g))in H[1]})for h in(1,0)],(a:=[b:=0]+[(b:=b+c)for c in I],b:=[d*(c&1)for c,d in enumerate(I)],c:={},d:=I[:],e:=len(d)-1)and"\nDay 9:",sum((f&1==0 or(e:=next((e for e in range(e,f,-2)if d[e]),f),d.__setitem__(e,d[e]-1)))and[f,e][f&1]//2*(a[f]+g)*(f<e)for f,g in enumerate(d[1:],1)for g in range(g)),sum((f:=next((f for f in range(c.get(I[g],0),g)if b[f]>=I[g]),g),b.__setitem__(f,b[f]-I[g]),c:=c|{I[g]:f},a.__setitem__(f,a[f]+I[g]))and(g//2*((2*a[f]-I[g]-1)*I[g]//2))for g in range(len(I)-1,-1,-2)),(a:=[(b:=lambda c,d,e:e+([]if d!=int(J.get(c,-1))else[c]if d>=9 else b(c+1,(d:=d+1),e)+b(c-1,d,e)+b(c+1j,d,e)+b(c-1j,d,e)))and b(c,0,[])for c in J])and"\nDay 10:",*[sum(map(len,a))for a in(map(set,a),a)],"\nDay 11:",*[sum(z("functools").reduce(lambda a,_:(b:=z("collections").Counter())or[b.update({d:a[c]})for c in a if(f:=str(c),g:=len(f)//2)for d in([1]if c==0 else[c*2024]if 1&len(f)else[int(f[:g]),int(f[g:])])]and b,range(e),K).values())for e in(25,75)],(a:=[],b:=set(),[(c:=set(),d:={f},[g==L.get(e:=d.pop(),0)and(b.add(e),c:=c|{e},d:=d|{e+f for f in(1,-1,1j,-1j)}-b)for _ in z("itertools").takewhile(lambda _:d,L)],a:=a+[c])for f,g in L.items()if not{f}&b])and"\nDay 12:",sum(len(b)*sum(not{d+c}&b for c in(1,-1,1j,-1j)for d in b)for b in a),sum(len(b)*sum(not(f:={e+c,e+d})&b or f<=b and not{e+d+c}&b for c in(1j,-1j)for d in(1,-1)for e in b)for b in a),"\nDay 13:",sum((a:=lambda b,c,d,e,f,g:0 if(i:=divmod(f-b*(h:=divmod(e*f-d*g,b*e-c*d))[0],d))[1]or h[1]else int(3*h[0]+i[0]))(*b)for b in M),sum(a(*(b[:4]+[b[4]+1e13,b[5]+1e13]))for b in M),(a:=max(a[0]for a,_ in N)+1,b:=max(b[1]for b,_ in N)+1,c:=[z("math").prod(({0:0,1:0,2:0,3:0}|z("collections").Counter(i//(b//2+1)*2+h//(a//2+1)for(d,e),(f,g)in N if(h:=(d+f*j)%a)!=a//2 and(i:=(e+g*j)%b)!=b//2)).values())for j in range(max(101,a*b+1))])and"\nDay 14:",c[100],min(range(a*b+1),key=c.__getitem__),"\nDay 15:",*[(a:=x(f.split()),b:=min(b for b in a if"@"==a[b]),[(c:=[1,-1,1j,-1j,0]["><v^".find(f)],d:=a.copy(),(e:=lambda a:(f:=d[b:=a+c])=="#"or f in"[]"and e(b+92-ord(f))or f in"O[]"and e(b)or d.update({a:d[b],b:d[a]}))(b)or(a:=d,b:=b+c))for f in O[1]])and sum((a[b]in"O[")*int(b.real+b.imag*100)for b in a)for f in(O[0],O[0].translate({35:"##",46:"..",79:"[]",64:"@."}))],(a:=(b:=min(a for a in P if"S"==P[a])).real,b:=b.imag,c:=(d:=min(c for c in P if"E"==P[c])).real,d:=d.imag,e:={},f:=[(0,1,0,a,b)],g:={},[(f:=[])if(c,d)==(h:=z("heapq").heappop(f))[3:]else[(i:=h[0]+k)<(j:=e.get(l,i+1))and(e.__setitem__(l,i),z("heapq").heappush(f,(i,*l)),g.__setitem__(l,{h[1:]}))or i!=j or g[l].add(h[1:])for k,l in[(1,(*h[1:3],h[1]+h[3],h[2]+h[4])),(1000,(h[2],-h[1],*h[3:])),(1000,(-h[2],h[1],*h[3:]))][P[h[1]+h[3]+(h[2]+h[4])*1j]=="#":]]for _ in z("itertools").takewhile(lambda _:f,[*P]*2)])and"\nDay 16:",h[0],len((c:=lambda d:{d[2:]}.union(*[c(p)for p in g[d]if(a,b)!=d[2:]]))(h[1:]))])([*zip(*map(str.split,open(y[1]).readlines()))],[[*map(int,a)]for a in map(str.split,open(y[2]).readlines())],open(y[3]).read(),open(y[4]).readlines(),open(y[5]).read().split("\n\n"),(x:=lambda a:{b*1j+d:e for b,c in enumerate(a)for d,e in enumerate(c.strip())})(open(y[6])),[[*map(int,a.replace(":","").split())]for a in open(y[7]).readlines()],(a:={},b:=set())and[(f!="."and a.setdefault(f,set()).add((c,e)),b.add((c,e)))for c,d in enumerate(open(y[8]).readlines())for e,f in enumerate(d.strip())]and(a.values(),b),list(map(int,open(y[9]).read().strip())),x(open(y[10])),z("collections").Counter(map(int,open(y[11]).read().split())),x(open(y[12])),[[*z("itertools").chain.from_iterable(map(int,c.groups())for b in a.split("\n")if(c:=z("re").search(r"(\d+).+?(\d+)",b)))]for a in open(y[13]).read().split("\n\n")],[[[*map(int,a)]for a in z("re").findall(r"(-?\d+),(-?\d+)",b)]for b in open(y[14]).readlines()],open(y[15]).read().split("\n\n"),x(open(y[16])),None,None,None,None,None,None,None,None,None)))(__import__)