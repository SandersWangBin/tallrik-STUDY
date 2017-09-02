#!/usr/bin/python

import sys

sys.path.append('../src/')
from Events import Events

e = Events()
e.register('../userDesign/hello.py:printHello')
e.register('../userDesign/hello.py:Hello#0', 456)
e.register('../userDesign/hello.py:Hello#0.printText')

print e

e.fire('../userDesign/hello.py:printHello')
e.fire('../userDesign/hello.py:Hello#0.printText', 123, 'ok')

from Tree import *
from Parser import *
def fireNodes(exp, nodes, expects, printFlag=False):
    rpn = genRpnList(exp)
    #if printFlag: print rpn
    mt = MergedTree(rpn)
    if printFlag:
        mt.printTreeUpDown()
        mt.printWishList()
        mt.printCandiList()

    i = 0
    result = True
    for n in nodes.split(' '):
        if len(n) > 0:
            if printFlag:
                print '==== ', n, ' ===='
            mt.fire(n)
            if printFlag:
                mt.printWishList()
                mt.printCandiList()
            wishList = mt.wishList.keys()
            wishList = sorted(wishList)
            if wishList != expects[i]:
                result = False
                if printFlag:
                    print '!!!!!!!!!!!!!!!!! WRONG !!!!!!!!!!'
                    print 'wishList', wishList
                    print 'expects', str(i), expects[i]
                    mt.printTreeUpDown()
            i += 1
    if printFlag:
        print
        print
    return result

def verifyList(vList):
    trueResult = 0
    for v in vList:
        num, exp, nodes, expects = v
        result = fireNodes(exp, nodes, expects)
        print num, '('+str(result)+') =>', exp
        trueResult += 1 if result else 0
    print '='*32
    print 'Successful:', str(trueResult), '/', str(len(vList))
    print 'Fail      :', str(len(vList)-trueResult), '/', str(len(vList))
    print
    print

vList = [('#0000', '<a>; ( (<b>,<c>,<d>*[0:]) | (<e> ; <f>*[2]) )', '<a> <c> <d> <b>', [['<b>','<c>','<d>','<e>'], ['<b>','<d>'], ['<b>','<d>'], []]), \
('#0001', '<a>; ( (<b>,<c>,<d>*[0:]) | (<e> ; <f>*[2]) )', '<a> <e> <f> <f>',[['<b>','<c>','<d>','<e>'], ['<f>'], ['<f>'], []]), \
('#0002', '<a>*[0:]; <b>*[0:]', '<a> <b>',[['<a>','<b>'], ['<b>']]), \
('#0003', '<a>*[0:]; <b>*[0:]', '<b>',[['<b>']]), \
('#0004', '(<a>*[0:], <b>*[0:])*[0:2]; <c>', '<b> <a> <a> <b> <a> <c>',[['<a>','<b>','<c>'],['<a>','<c>'], ['<a>','<c>'], ['<a>','<b>','<c>'], ['<a>','<c>'], []]), \
('#0005', '(<a>*[0:1], <b>*[0:])*[0:2]; <c>', '<b> <a> <a> <b> <b> <c>',[['<a>','<b>','<c>'], ['<a>','<b>','<c>'], ['<b>','<c>'],['<b>','<c>'],['<b>','<c>'],[]]), \
('#0006', '(<a>*[0:], <b>*[0:])*[0:2]; <c>', '<b> <a> <b> <c>',[['<a>','<b>','<c>'], ['<a>','<c>'], ['<a>','<b>','<c>'], []]), \
('#0007', '<d>; ((<a>*[0:], <b>*[0:])*[0:2], <c>)*[1:3]; <e>', '<d> <c> <c> <e>',[['<a>','<b>','<c>'], ['<a>','<b>','<e>'], ['<a>','<b>','<e>'], []]), \
('#0008', '<d>; ((<a>*[0:]| <b>*[0:])*[0:2]| <c>)*[1:3]; <e>', '<d> <c> <a> <a> <b> <e>',[['<a>','<b>','<c>'], ['<a>','<b>','<c>','<e>'], ['<a>','<e>'], ['<a>','<e>'], ['<b>','<e>'], []]), \
('#0009', '<d>; ((<a>*[0:]; <b>*[0:])*[0:2]; <c>)*[1:2]; <e>', '<d> <c> <a> <a> <b> <c>',[['<a>','<b>','<c>'],['<a>','<b>','<c>','<e>'], ['<a>','<b>','<c>'], ['<a>','<b>','<c>'], ['<b>','<c>'], ['<e>']]), \
('#0010', '(<a>; <b>), (<c>; <d>)', '<c> <d> <a> <b>',[['<d>'], ['<a>'], ['<b>'], []]), \
('#0011', '(<a>*[3:7], <b>*[2:4])*[1:1]; <c>', '<a> <a> <a> <b> <b> <b> <c>',[['<a>'], ['<a>'], ['<a>', '<b>'], ['<b>'], ['<b>', '<c>'], ['<b>', '<c>'], []]), \
('#0012', '(<a>*[3:7], <b>*[2:4])*[1:3], <c>', '<a> <a> <a> <b> <b> <c>',[['<a>'], ['<a>'], ['<a>', '<b>'], ['<b>'], ['<b>', '<c>'], []]), \
('#0013', '(<a>*[3:7], <b>*[2:4])*[0:3], <c>', '<a> <a> <a> <b> <b> <c>',[['<a>'], ['<a>'], ['<a>', '<b>'], ['<b>'], ['<b>', '<c>'],[]]), \
('#0014', '(<a>*[3:7], <b>*[2:4])*[0:3], <c>', '<c>',[['<a>', '<b>']]), \
('#0015', '(<a>*[0:], <b>)*[2:4]; <c>', '<b> <b> <c>',[['<a>'],['<a>', '<c>'], []]), \
('#0016', '<a>*[0:3], <b>*[0:2]; <c>', '<c>', [[]]), \
('#0017', '<a>*[0:3]; <b>*[0:2],<c>; <d>*[0:2], <e>, (<f>*[0:3], <g>*[0:1]; <h>)*[0:2]', '<a> <c> <h> <h>',[['<a>', '<b>', '<c>'], ['<b>', '<d>', '<e>', '<f>', '<g>', '<h>'], ['<d>', '<e>', '<f>', '<g>', '<h>'], ['<d>', '<e>']]), \
('#0018', '<a>*[0:3]; <b>*[0:2],<c>; <d>*[0:2], <e>, (<f>*[0:3], <g>*[0:1]; <h>)*[0:2]', '<a> <c> <h> <e>',[['<a>', '<b>', '<c>'], ['<b>', '<d>', '<e>', '<f>', '<g>', '<h>'], ['<d>', '<e>', '<f>', '<g>', '<h>'], ['<d>']]), \
('#0019', '<a>*[0:3]; <b>*[0:2],<c>; <d>*[0:2], <e>, (<f>*[0:3], <g>*[0:1]; <h>)*[2:3]', '<a> <c> <h> <f> <g> <h> <e> <d> <d>',[['<a>', '<b>', '<c>'], ['<b>', '<d>', '<e>', '<f>', '<g>', '<h>'], ['<f>', '<g>', '<h>'], ['<f>', '<g>', '<h>'], ['<h>'], ['<d>', '<e>', '<f>', '<g>', '<h>'], ['<d>'], ['<d>'], []]), \
('#0020', '<a>*[0:2], <b>*[1,3]|(<c>*[0:1],<d>*[2:3];<e>)*[0:1], <f>*[0:1]; <g>', '<d> <d> <c> <e> <g>',[['<d>'], ['<c>', '<d>', '<e>'], ['<e>'], ['<f>', '<g>'], []]), \
]

verifyList(vList)

'''
print '=>', fireNodes('<a>; ( (<b>,<c>,<d>*[0:]) | (<e> ; <f>*[2]) )', '<a> <c> <d> <b>', 
[['<b>','<c>','<d>','<e>'], ['<b>','<d>'], ['<b>','<d>'], []])
print '=>', fireNodes('<a>; ( (<b>,<c>,<d>*[0:]) | (<e> ; <f>*[2]) )', '<a> <e> <f> <f>',
[['<b>','<c>','<d>','<e>'], ['<f>'], ['<f>'], []])
print '=>', fireNodes('<a>*[0:]; <b>*[0:]', '<a> <b>',
[['<a>','<b>'], ['<b>']])
print '=>', fireNodes('<a>*[0:]; <b>*[0:]', '<b>',
[['<b>']])

print '=>', fireNodes('(<a>*[0:], <b>*[0:])*[0:2]; <c>', '<b> <a> <a> <b> <a> <c>',
[['<a>','<b>','<c>'],['<a>','<c>'], ['<a>','<c>'], ['<a>','<b>','<c>'], ['<a>','<c>'], []])

print '=>', fireNodes('(<a>*[0:1], <b>*[0:])*[0:2]; <c>', '<b> <a> <a> <b> <b> <c>',
[['<a>','<b>','<c>'], ['<a>','<b>','<c>'], ['<b>','<c>'],['<b>','<c>'],['<b>','<c>'],[]])

print '=>', fireNodes('(<a>*[0:], <b>*[0:])*[0:2]; <c>', '<b> <a> <b> <c>',
[['<a>','<b>','<c>'], ['<a>','<c>'], ['<a>','<b>','<c>'], []])

print '=>', fireNodes('<d>; ((<a>*[0:], <b>*[0:])*[0:2], <c>)*[1:3]; <e>', '<d> <c> <c> <e>',
[['<a>','<b>','<c>'], ['<a>','<b>','<e>'], ['<a>','<b>','<e>'], []])

print '=>', fireNodes('<d>; ((<a>*[0:]| <b>*[0:])*[0:2]| <c>)*[1:3]; <e>', '<d> <c> <a> <a> <b> <e>',
[['<a>','<b>','<c>'], ['<a>','<b>','<c>','<e>'], ['<a>','<e>'], ['<a>','<e>'], ['<b>','<e>'], []])

print '=>', fireNodes('<d>; ((<a>*[0:]; <b>*[0:])*[0:2]; <c>)*[1:2]; <e>', '<d> <c> <a> <a> <b> <c>',
[['<a>','<b>','<c>'],['<a>','<b>','<c>','<e>'], ['<a>','<b>','<c>'], ['<a>','<b>','<c>'], ['<b>','<c>'], ['<e>']])

print '=>', fireNodes('(<a>; <b>), (<c>; <d>)', '<c> <d> <a> <b>',
[['<d>'], ['<a>'], ['<b>'], []])

print '=>', fireNodes('(<a>*[3:7], <b>*[2:4])*[1:1]; <c>', '<a> <a> <a> <b> <b> <b> <c>',
[['<a>'], ['<a>'], ['<a>', '<b>'], ['<b>'], ['<b>', '<c>'], ['<b>', '<c>'], []])

print '=>', fireNodes('(<a>*[3:7], <b>*[2:4])*[1:3], <c>', '<a> <a> <a> <b> <b> <c>',
[['<a>'], ['<a>'], ['<a>', '<b>'], ['<b>'], ['<b>', '<c>'], []])

print '=>', fireNodes('(<a>*[3:7], <b>*[2:4])*[0:3], <c>', '<a> <a> <a> <b> <b> <c>',
[['<a>'], ['<a>'], ['<a>', '<b>'], ['<b>'], ['<b>', '<c>'],[]])

print '=>', fireNodes('(<a>*[3:7], <b>*[2:4])*[0:3], <c>', '<c>',
[['<a>', '<b>']])

print '=>', fireNodes('(<a>*[0:], <b>)*[2:4]; <c>', '<b> <b> <c>',
[['<a>'],['<a>', '<c>'], []])

print '=>', fireNodes('<a>*[0:3], <b>*[0:2]; <c>', '<c>', [[]])

print '=>', fireNodes('<a>*[0:3]; <b>*[0:2],<c>; <d>*[0:2], <e>, (<f>*[0:3], <g>*[0:1]; <h>)*[0:2]', '<a> <c> <h> <h>',
[['<a>', '<b>', '<c>'], ['<b>', '<d>', '<e>', '<f>', '<g>', '<h>'], ['<d>', '<e>', '<f>', '<g>', '<h>'], ['<d>', '<e>']])

print '=>', fireNodes('<a>*[0:3]; <b>*[0:2],<c>; <d>*[0:2], <e>, (<f>*[0:3], <g>*[0:1]; <h>)*[0:2]', '<a> <c> <h> <e>',
[['<a>', '<b>', '<c>'], ['<b>', '<d>', '<e>', '<f>', '<g>', '<h>'], ['<d>', '<e>', '<f>', '<g>', '<h>'], ['<d>']])

print '=>', fireNodes('<a>*[0:3]; <b>*[0:2],<c>; <d>*[0:2], <e>, (<f>*[0:3], <g>*[0:1]; <h>)*[2:3]', '<a> <c> <h> <f> <g> <h> <e> <d> <d>',
[['<a>', '<b>', '<c>'], ['<b>', '<d>', '<e>', '<f>', '<g>', '<h>'], ['<f>', '<g>', '<h>'], ['<f>', '<g>', '<h>'], ['<h>'], ['<d>', '<e>', '<f>', '<g>', '<h>'], ['<d>'], ['<d>'], []])
'''


print fireNodes('<a>*[0:2], <b>*[1,3]|(<c>*[0:1],<d>*[2:3];<e>)*[0:1], <f>*[0:1]; <g>', '<d> <d> <c> <e> <g>',
[['<d>'], ['<c>', '<d>', '<e>'], ['<e>'], ['<f>', '<g>'], []], True)

'''
def verifyLoop(loopStr, loopStr2, fires=1):
    from Tree import Loop
    l = Loop(loopStr)
    print loopStr, str(l)
    print ' * ', loopStr2, 
    print '=>', str(l.timesLoopStr(loopStr2))
    print 'fire: ' + str(fires) + ' ', 
    for f in range(fires): l.fire()
    print l

verifyLoop('[]', '[]')
verifyLoop('[5]', '[2]')
verifyLoop('[3:5]', '[1:4]')
verifyLoop('[:5]', '[:2]')
verifyLoop('[3:]', '[4:]')
verifyLoop('[:]', '[:]')
verifyLoop('[0:5]', '[2]')
verifyLoop('[0:5]', '[0:]')

#print
#printTreeDownUp(root)
'''
