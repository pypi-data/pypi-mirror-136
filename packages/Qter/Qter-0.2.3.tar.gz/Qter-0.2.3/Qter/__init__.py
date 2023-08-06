import cmath as cmath
import numpy as np
from numpy import kron as kron
import math as math
from math import pi as pi
import random
import matplotlib.pyplot as plt

p=cmath.sqrt(-1)
a= cmath.exp(-(p*pi)/4)
k=1/np.sqrt(2)
v= cmath.exp((p*pi)/2)
I = [[1,0],[0,1]]
X = [[0,1],[1,0]]
Y = [[0,-p],[p,0]]
Z = [[1,0],[0,-1]]
H = [[k,k],[k,-k]]
T = [[1,0],[0,a]]
S = [[1, 0], [0, v]]
CX=[[1, 0, 0, 0],[0, 1, 0, 0],[0, 0, 0, 1],[0, 0, 1, 0]]

SW = [[1, 0, 0, 0],[0, 0, 1, 0],[0, 1, 0, 0],[0, 0, 0, 1]]

def run(cir, n, count=8192, error=False, Transpiler=True, err=0 ):

    if (Transpiler == True):
        def search(list, value):
            for i in range(len(list)):
                if list[i] == value:
                    return True
            return False
        tr=0
        for i in range(len(cir)):
            if ((cir[i][1])==list):
                tr+=1
        if (tr==0):
            Transpiler = False

        if (Transpiler == True):
            k=[]
            for i in range(len(cir)):
                if(type(cir[i][1])==list):
                    for j in range(2):
                        if(search(k,cir[i][1][j])==False):
                            k.append(cir[i][1][j])
            qubito=[]
            for j in range(len(k)):
                qubito.append(k[j])
            for i in range(len(qubit)):
                if(search(qubito, i)==False):
                    qubito.append(i)
            qubit=[]
            for i in range(n):
                qubit.append(i)
            qubit1q=[]
            qubit2q=[]
            for i in range(len(qubit)):
                if(i<len(k)):
                    qubit2q.append(i)
                else:
                    qubit1q.append(i)
            seq=[]
            circom=[]
            def permutations(start, end=[]):
                if len(start) == 0:
                    seq.append(end)
                    circom.append([])
                else:
                    for i in range(len(start)):
                        permutations(start[:i] + start[i+1:], end + start[i:i+1])
            permutations(qubit2q)
            for i in range(len(seq)):
                for j in range(len(qubit1q)):
                    seq[i].append(qubit1q[j])

            for i in range(len(seq)):
                for t in range(len(cir)):
                    if(type(cir[t][1])==int):
                        circom[i].append([cir[t][0], seq[i][qubito.index(cir[t][1])]])
                    if(type(cir[t][1])==list):
                        circom[i].append([cir[t][0], [seq[i][qubito.index(cir[t][1][0])], seq[i][qubito.index(cir[t][1][1])]]])

            for i in range(len(circom)):
                cost = 0
                mincostindex=[]
                mincost= np.sqrt(((circom[0][4][1][0]) - (circom[0][4][1][1]))**2)*100
                for j in range(len(circom[0])):
                    if (type(circom[i][j][1])==list):
                        cost = cost + np.sqrt(((circom[i][j][1][0]) - (circom[i][j][1][1]))**2)
                if(cost<mincost):
                    mincost=cost
                    mincostindex.append(i)
                    cir = circom[mincostindex[len(mincostindex)-1]]
    def He():
        c = random.uniform(-err, err)
        E =  np.array([[c, -c], [-c, -c]])
        He =np.add(H,E)
        return(He)

    def Xe():
        c1 = random.uniform(-err, err)
        c2 = random.uniform(-err, err)
        E =  np.array([[c1, -c2], [c2, -c1]])
        Xe =np.add(X,E)
        return(Xe)

    def Ye():
        c1 = random.uniform(-err, err)
        c2 = random.uniform(-err, err)
        E =  np.array([[c1, c2], [c2, -c1]])
        Ye =np.add(Y,E)
        return(Ye)

    def Ze():
        c1 = random.uniform(-err, err)
        E =  np.array([[0, c1], [c1, 0]])
        Ze =np.add(Z,E)
        return(Ze)

    def CXe():
        c1 = random.uniform(-err, err)
        c2 = random.uniform(-err, err)
        c3 = random.uniform(-err, err)
        c4 = random.uniform(-err, err)
        c5 = random.uniform(-err, err)
        c6 = random.uniform(-err, err)    
        E =  np.array([[0, 0, c1, c1], [0, 0, c2, c2], [c3, c4, c5, c6], [c3, c4, c6, c5]])
        CXe =np.add(CX,E)
        return(CXe)

    def SWe():
        c1 = random.uniform(-err, err)
        c2 = random.uniform(-err, err)
        c3 = random.uniform(-err, err)
        c4 = random.uniform(-err, err)
        c5 = random.uniform(-err, err)
        c6 = random.uniform(-err, err)    
        E =  np.array([[0, c1, c1, 0], [c2, c3, c4, c5], [c2, c4, c3, c5], [0, c6, c6, 0]])
        SWe =np.add(SW,E)
        return(SWe)
    ec=[]
    if (error == True):
        for i in range(len(cir)):
            if(cir[i][0]==H):
                ec.append([He(),cir[i][1]])
            if(cir[i][0]==X):
                ec.append([Xe(),cir[i][1]])
            if(cir[i][0]==Y):
                ec.append([Ye(),cir[i][1]])
            if(cir[i][0]==Z):
                ec.append([Ze(),cir[i][1]])
            if(cir[i][0]==CX):
                ec.append([CXe(),cir[i][1]])
            if(cir[i][0]==SW):
                ec.append([SWe(),cir[i][1]])
        cir = ec
    
    gate=[]
    
    for i in range(n):
        gate.append([])
    for i in range(len(cir)):
        if(type(cir[i][1])==int):
            gate[cir[i][1]].append(cir[i][0])

        elif(type(cir[i][1])==list):
            if((cir[i][1][1]-cir[i][1][0])==1):
                if(len(gate[cir[i][1][0]])==(len(gate[(cir[i][1][0]+1)]))):
                    gate[cir[i][1][0]].append(cir[i][0])
                    gate[cir[i][1][0]+1].append('Ta')
                elif(len(gate[cir[i][1][0]])>(len(gate[(cir[i][1][0]+1)]))):
                    for j in range(len(gate[cir[i][1][0]])-(len(gate[(cir[i][1][0])+1]))):
                        gate[cir[i][1][0]+1].append(I)
                    gate[cir[i][1][0]].append(cir[i][0])
                    gate[cir[i][1][0]+1].append('Ta')
                elif(len(gate[cir[i][1][0]])<(len(gate[(cir[i][1][0]+1)]))):
                    for j in range(len(gate[cir[i][1][0]+1])-(len(gate[(cir[i][1][0])]))):
                        gate[cir[i][1][0]].append(I)
                    gate[cir[i][1][0]].append(cir[i][0])
                    gate[cir[i][1][0]+1].append('Ta')

            elif((cir[i][1][1]-cir[i][1][0])>1):

                for m in range((cir[i][1][1]-cir[i][1][0])-1):
                    if(len(gate[cir[i][1][1]-m])==len(gate[cir[i][1][1]-m-1])):
                        gate[cir[i][1][1]-m-1].append(SW)
                        gate[cir[i][1][1]-m].append('Ta')
                    elif(len(gate[cir[i][1][1]-m])>len(gate[cir[i][1][1]-m-1])):
                        for j in range(len(gate[cir[i][1][1]-m])-len(gate[cir[i][1][1]-m-1])):
                            gate[cir[i][1][1]-m-1].append(I)
                        gate[cir[i][1][1]-m-1].append(SW)
                        gate[cir[i][1][1]-m].append('Ta')
                    elif(len(gate[cir[i][1][1]-m])<len(gate[cir[i][1][1]-m-1])):
                        for j in range(len(gate[cir[i][1][1]-m-1])-len(gate[cir[i][1][1]-m])):
                            gate[cir[i][1][1]-m].append(I)
                        gate[cir[i][1][1]-m-1].append(SW)
                        gate[cir[i][1][1]-m].append('Ta')
                if(len(gate[cir[i][1][0]])==(len(gate[(cir[i][1][0]+1)]))):
                    gate[cir[i][1][0]].append(cir[i][0])
                    gate[cir[i][1][0]+1].append('Ta')
                elif(len(gate[cir[i][1][0]])>(len(gate[(cir[i][1][0]+1)]))):
                    for j in range(len(gate[cir[i][1][0]])-(len(gate[(cir[i][1][0])+1]))):
                        gate[cir[i][1][0]+1].append(I)
                    gate[cir[i][1][0]].append(cir[i][0])
                    gate[cir[i][1][0]+1].append('Ta')
                elif(len(gate[cir[i][1][0]])<(len(gate[(cir[i][1][0]+1)]))):
                    for j in range(len(gate[cir[i][1][0]+1])-(len(gate[(cir[i][1][0])]))):
                        gate[cir[i][1][0]].append(I)
                    gate[cir[i][1][0]].append(cir[i][0])
                    gate[cir[i][1][0]+1].append('Ta')
                for t in range(cir[i][1][1]-cir[i][1][0]):
                    for p in range(2*t-1):
                        gate[cir[i][1][0]+t+1].append(I)
                for t in range(cir[i][1][1]-cir[i][1][0]-1):    
                    gate[cir[i][1][0]+t+1].append(SW)
                    gate[cir[i][1][0]+t+2].append('Ta')


            elif((cir[i][1][1]-cir[i][1][0])<1):
                for m in range((cir[i][1][0]-cir[i][1][1])):
                    if(len(gate[cir[i][1][1]+m])==len(gate[cir[i][1][1]+m+1])):
                        gate[cir[i][1][1]+m].append(SW)
                        gate[cir[i][1][1]+m+1].append('Ta')
                    elif(len(gate[cir[i][1][1]+m])>len(gate[cir[i][1][1]+m+1])):
                        for j in range(len(gate[cir[i][1][1]+m])-len(gate[cir[i][1][1]+m+1])):
                            gate[cir[i][1][1]+m+1].append(I)
                        gate[cir[i][1][1]+m].append(SW)
                        gate[cir[i][1][1]+m+1].append('Ta')
                    elif(len(gate[cir[i][1][1]+m])<len(gate[cir[i][1][1]+m+1])):
                        for j in range(len(gate[cir[i][1][1]+m+1])-len(gate[cir[i][1][1]+m])):
                            gate[cir[i][1][1]+m].append(I)
                        gate[cir[i][1][1]+m].append(SW)
                        gate[cir[i][1][1]+m+1].append('Ta')
                gate[cir[i][1][0]-1].append(cir[i][0])
                gate[cir[i][1][0]].append('Ta')
                gate[cir[i][1][0]-1].append(SW)
                gate[cir[i][1][0]].append('Ta')

                for t in range(cir[i][1][0]-cir[i][1][1]):
                    for p in range(2*t+1):
                        if(t!=0):
                            gate[cir[i][1][0]-t-1].append(I)
                for t in range(cir[i][1][0]-cir[i][1][1]-1):    
                    gate[cir[i][1][0]-t-2].append(SW)
                    gate[cir[i][1][0]-t-1].append('Ta')
    v=0
    for i in range(len(gate)):
        if(v<len(gate[i])):
            v= len(gate[i])

    for k in range(len(gate)):
        if(len(gate[k])<v):
            for j in range(v-len(gate[k])):
                gate[k].append(I)
    if(Transpiler == False):
        inst=[]
        k=[1, 0]
        c=kron(k,k)
        for i in range(n-2):
            c=kron(c,k)
        inst.append(c)
        t1=[]
        
        for j in range(len(gate[0])):
            

            v=gate[0][j]

            for i in range(n-1):
                if(gate[i+1][j]=='Ta'):
                    pass
                elif(len(gate[i+1][j])==2):
                    v=kron(v, gate[i+1][j])
                    pass
                elif(len(gate[i+1][j])==4):
                    v=kron(v,gate[i+1][j])
            t1.append(v)
            

        f=np.matmul(inst,t1[0])
        for i in range(len(gate[0])-1):
            f=np.matmul(f,t1[i+1])

    if(Transpiler == True): 
        qu=[qubit2q]

        for i in range(len(qubit1q)):
            qu.append(qubit1q[i])
        instt=[]
        k=[1, 0]
        for i in range(len(qu)):
            if i==0:
                c=kron(k,k)
                for j in range(len(qubit2q)-2):
                    c=kron(c,k)
                instt.append(c)
            else:
                instt.append(k)
        tt1=[]
        for j in range(len(gate[0])):

            if j!=0:
                tt1.append(v)
                pass
            v=gate[0][j]

            for i in range(len(qubit2q)-1):
                if(gate[i+1][j]=='Ta'):
                    pass
                elif(len(gate[i+1][j])==2):
                    v=kron(v, gate[i+1][j])
                    pass
                elif(len(gate[i+1][j])==4):
                    v=kron(v,gate[i+1][j])
        ft=[]
        for i in range(len(tt1)):
            ft.append([])
        for i in range(len(qu)):
            if(i==0):
                ft[0].append([np.matmul(instt[i],tt1[0])])
            else:
                ft[0].append([np.matmul(instt[i], gate[len(qu[0])+i-1][0])])
        for i in range(len(qubit1q)+1):
            for j in range(len(gate[0])-2):
                    if(i==0):
                       ft[j+1].append(np.matmul(ft[j][i],tt1[j+1]))
                    else:
                       ft[j+1].append(np.matmul(ft[j][i],gate[len(qu[0])+i-1][j+1]))
        for i in range(len(ft[len(tt1)-1])-1):
            if(i==0):
                v= kron(ft[len(tt1)-1][i],ft[len(tt1)-1][i+1])
            else:
                v= kron(v,ft[len(tt1)-1][i+1])
        f=v
    fist=[]
    for i in range(len(f[0])):
        if(f[0][i]==1):
            fist.append(i)
            pass
        else:

            fist.append([i, f[0][i]])

    final=[]
    for i in range(len(fist)):
        k= bin(fist[i][0])[2:]
        final.append(k)


    final=[]
    finalc=[]
    for i in range(len(fist)):
        k = [int(x) for x in bin(fist[i][0])[2:]]
        while(len(k)<n):
            k.insert(0,0)
        final.append(k)
        finalc.append(fist[i][1])

    if (Transpiler == True):
        qut = seq[mincostindex[len(mincostindex)-1]]
        finalt=[]
        for i in range(len(final)):
            finalt.append([])
            for j in range(len(final[0])):
                finalt[i].append(final[i][qubito.index(qut[j])])
        final=finalt
        finalct=[]
        for i in range(len(finalc)):
            finalct.append(finalc[final.index(finalt[i])])
        finalc=finalct
    fi=[]
    for i in range(len(final)):

        for j in range(len(final[0])):
            if (j==0):
                v=str(final[i][0])
                pass
            else:
                v=v+str(final[i][j])
        fi.append(v)
    fst=[]
    for i in range(len(fi)):
        if(finalc[i]!=0):
            fst.append([finalc[i],fi[i]])

    fst
    prob=[]
    for i in range (len(fst)):
        v=fst[i][0]
        k=(abs(v))**2
        prob.append([k,fst[i][1]])
    coun=[]
    for i in range(len(prob)):
        coun.append([int(prob[i][0]*count), prob[i][1]])
    return prob, coun
def draw(cir, n):
    def cir_str (x):
        v = "U "
        if (x == H):
            v= "H--"
        if x == X:
            v= "X--"
        if x == I:
            v= "I--"
        if x == Y:
            v= "Y--"
        if x == Z:
            v= "Z--"
        if x == T:
            v= "T--"
        if x == S:
            v= "S--"
        if x == CX:
            v= "CX-"
        if x == SW:
            v= "SW-"
    
        return v
    
    dr=[]
    for i in range(n):
        dr.append([])
    for i in range(len(cir)):
        if (type(cir[i][1])==int):
            dr[cir[i][1]].append(cir_str(cir[i][0]))
        if (type(cir[i][1])==list):
            if (cir[i][1][0]<cir[i][1][1]):
                v=0
                for k in range(cir[i][1][1]-cir[i][1][0]+1):
                    
                    if (len(dr[cir[i][1][0]+k])>v):
                        v=len(dr[cir[i][1][0]+k])
                for c in range(cir[i][1][1]-cir[i][1][0]+1):
                    for t in range(v-len(dr[cir[i][1][0]+c])):
                        dr[cir[i][1][0]+c].append("---")
                dr[cir[i][1][0]].append("-@-")
                dr[cir[i][1][1]].append(cir_str(cir[i][0]))
                for c in range(cir[i][1][1]-cir[i][1][0]-1):
                    dr[cir[i][1][0]+c+1].append("-|-")
            if (cir[i][1][0]>cir[i][1][1]):
                v=0
                for k in range(cir[i][1][0]-cir[i][1][1]+1):
                    
                    if (len(dr[cir[i][1][1]+k])>v):
                        v=len(dr[cir[i][1][1]+k])
                for c in range(cir[i][1][0]-cir[i][1][1]+1):
                    for t in range(v-len(dr[cir[i][1][1]+c])):
                        dr[cir[i][1][1]+c].append("---")
                dr[cir[i][1][0]].append("-@-")
                dr[cir[i][1][1]].append(cir_str(cir[i][0]))
                for c in range(cir[i][1][0]-cir[i][1][1]-1):
                    dr[cir[i][1][1]+c+1].append("-|-")
                
    k=0
    for i in range (len(dr)):
        
        if(len(dr[i])>k):
            k=len(dr[i])
            
    for i in range (len(dr)):
        for j in range(k-len(dr[i])):
            dr[i].append("---")
    for i in range (len(dr)):
        print('q',i,">---", end = "")
        for j in range (len(dr[i])):
            print(dr[i][j],"---", end ="")
        print("\n")
    return
def plot(x,y=[10,15]):
    yax=[]
    xax=[]
    for i in range(len(x)):
        yax.append(x[i][1])
        xax.append(x[i][0])
    plt.xticks(rotation='vertical')
    plt.rcParams["figure.figsize"] = (y[0], y[1])
    plt.bar(yax,xax)