# -*- coding: utf-8 -*-
"""
Created on Mon Jan 31 00:45:40 2022

@author: Jefferson
"""

def primo(n):
        
    M=0
    for i in range(2,n+1):
        
        for k in range(2,i):
            if i % k == 0:
                M+=1
        
        if M==0:
            print(i)
        else:
            M=0
        
            
primo(11)

