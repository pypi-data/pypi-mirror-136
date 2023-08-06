import numpy as np

def constant_integration(func,a,b,N):
    dx=(b-a)/N
    I=0
    for i in range (N):
        I+=func(a+i*dx)*dx
    return I

def trapezium_integration(func,a,b,N):
    dx=(b-a)/N
    I=0
    for i in range (1,N):
        I+=2*func(a+i*dx)
    I=(func(a) + I + func(b))*dx/2
    return I

def simpson_integration(func,a,b,N):
    dx=(b-a)/N
    I=0
    for i in range (1,N):
        if i%2 == 1:
            I+=4*func(a+i*dx)
        else:
            I+=2*func(a+i*dx)
    I=(func(a)+I+func(b))*dx/3
    return I

