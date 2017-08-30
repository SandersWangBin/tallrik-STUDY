#!/usr/bin/python
import re
import sys
from Stack import Stack

SYMBOL_PARENLEFT = "("
SYMBOL_PARENRIGHT = ")"
SYMBOL_LOOP = "*"
SYMBOL_AND = ","
SYMBOL_OR = "|"
SYMBOL_NEXT = ";"
SYMBOL_VARLEFT = "<"
SYMBOL_VARRIGHT = ">"
SYMBOL_CONSLEFT = "["
SYMBOL_CONSRIGHT = "]"
SYMBOL_SPACE = " "

TYPE_OP   = "OP"
TYPE_VAR  = "VAR"
TYPE_CONS = "CONS"

class Loop:
    REG_SINGLE = '\[([0-9]*)\]'
    REG_RANGE  = '\[([0-9]*):([0-9]*)\]'

    LOOP_STATUS_LESS = '$LESS'
    LOOP_STATUS_IN   = '$IN'
    LOOP_STATUS_MAX  = '$MAX'
    LOOP_STATUS_MORE = '$MORE'

    FIRE_STATUS_TODO   = '$TODO'
    FIRE_STATUS_MUSTDO = '$MUSTDO'
    FIRE_STATUS_DOING  = '$DOING'
    FIRE_STATUS_DONE   = '$DONE'

    VALUE_MAX_INT = sys.maxint

    def __init__(self, loopStr='[1]'):
        self.loopStrList = list()
        self.loopStrList.append(loopStr)
        self.min ,self.max = self._parserLoopStr(loopStr)
        self.fireCount = 0
        self.loopStatus, self.fireStatus = self._updateStatus(self.fireCount)

    def _parserLoopStr(self, loopStr):
        min, max = 1, 1
        m = re.search(Loop.REG_SINGLE, loopStr)
        if m:
            value = m.group(1)
            if value.isdigit(): min, max = int(value), int(value)
            else: min, max = 1, 1
        else:
            m = re.search(Loop.REG_RANGE, loopStr)
            if m:
                value1, value2 = m.group(1), m.group(2)
                min = int(value1) if value1.isdigit() else 1
                max = int(value2) if value2.isdigit() else Loop.VALUE_MAX_INT
            else:
                min, max = 1, 1
        return min, max

    def _updateLoopStatus(self, count):
        if count > self.max: return Loop.LOOP_STATUS_MORE
        elif count == self.max: return Loop.LOOP_STATUS_MAX
        elif count >= self.min and count < self.max: return Loop.LOOP_STATUS_IN
        else: return Loop.LOOP_STATUS_LESS

    def _updateFireStatus(self, count):
        if count <= 0: return Loop.FIRE_STATUS_TODO
        else:
            if count >= self.max: return Loop.FIRE_STATUS_DONE
            elif count >= self.min and count < self.max: return Loop.FIRE_STATUS_DOING
            else: return Loop.FIRE_STATUS_MUSTDO

    def _updateStatus(self, count):
        loopStatus = self._updateLoopStatus(count)
        fireStatus = self._updateFireStatus(count)
        return loopStatus, fireStatus

    def _updateLoop(self):
        if count >= self.max:
            self.loops += 1
            self.loopIn = 0

    def fire(self):
        self.fireCount += 1
        self.loopStatus, self.fireStatus = self._updateStatus(self.fireCount)

    def _times(self, loopMin, loopMax):
        self.min = self.min * loopMin
        if self.max == Loop.VALUE_MAX_INT or loopMax == Loop.VALUE_MAX_INT:
            self.max = Loop.VALUE_MAX_INT
        else: self.max = self.max * loopMax

    def timesLoopStr(self, loopStr):
        self.loopStrList.append(loopStr)
        loopMin, loopMax = self._parserLoopStr(loopStr)
        self._times(loopMin, loopMax)
        self.loopStatus, self.fireStatus = self._updateStatus(self.fireCount)
        return self

    def times(self, loop):
        self._times(loop.min, loop.max)
        self.loopStatus, self.fireStatus = self._updateStatus(self.fireCount)
        return self

    def _plus(self, loopMin, loopMax):
        self.min = self.min + loopMin
        if self.max == Loop.VALUE_MAX_INT or loopMax == Loop.VALUE_MAX_INT:
            self.max = Loop.VALUE_MAX_INT
        else: self.max = self.max + loopMax

    def plus(self, loop):
        self._plus(loop.min, loop.max)
        self.loopStatus, self.fireStatus = self._updateStatus(self.fireCount)
        return self

    def avail(self):
        if self.fireStatus == Loop.FIRE_STATUS_DONE or self.loopStatus == Loop.LOOP_STATUS_MAX \
        or self.loopStatus == Loop.LOOP_STATUS_MORE:
            return False
        else: return True

    def reset(self):
        if len(self.loopStrList) > 0:
            self.min, self.max = self._parserLoopStr(self.loopStrList[0])
            for i in range(1, len(self.loopStrList)):
                loopMin, loopMax = self._parserLoopStr(self.loopStrList[i])
                self._times(loopMin, loopMax)
            self.loopStatus, self.fireStatus = self._updateStatus(self.fireCount)

    def restart(self):
        self.fireCount = 0
        self.loopStatus, self.fireStatus = self._updateStatus(self.fireCount)

    def startFire(self):
        if self.fireStatus == Loop.FIRE_STATUS_TODO: self.fireStatus = Loop.FIRE_STATUS_DOING

    def stopFire(self):
        if self.fireStatus == Loop.FIRE_STATUS_DOING and self.loopStatus != Loop.LOOP_STATUS_LESS:
            self.fireStatus = Loop.FIRE_STATUS_DONE
            return True
        else: return False

    def __str__(self):
        max = str(self.max) if self.max != Loop.VALUE_MAX_INT else '~'
        return '[' + str(self.min) + ':' + max + '] ' + \
        str(self.fireCount) + self.fireStatus + self.loopStatus

class TNode:
    def __init__(self, type, item):
        self.type = type
        self.item = item
        self.childRank = 0
        self.loop = Loop('[]')
        self.avail = True   # count for loop
        self.enable = True  # disable when one of or branches is fired
        self.parent = None
        self.children = list()

    def __str__(self):
        result = self.type + ': ' + self.item + ' (' + str(self.childRank) + ')'
        result += 'loop: ' + str(self.loop) + ' avail: ' + str(self.avail) + ' enable: ' + str(self.enable)
        if self.parent != None: result += ' ^: ' + self.parent.item
        if len(self.children) > 0: result += ' v: ' + ' '.join([e.item for e in self.children])
        return result

class MergedTree:
    def __init__(self, rpnList):
        self.root = self._genBinTree(rpnList)
        self.mergeLoopTreeDownUp()
        self.mergeSameOpTreeDownUp()
        self.wishList = {}
        self.candiList = {}
        self._generateWishList()

    def _genTNode(self, element):
        return TNode(element[0], element[1])

    def _genBinTree(self, rpnList):
        rpnStack = Stack()
        for e in rpnList:
            type, item = e
            if type == TYPE_CONS or type == TYPE_VAR:
                rpnStack.push(self._genTNode(e))
            elif type == TYPE_OP:
                node = self._genTNode(e)
                r = rpnStack.pop()
                r.parent = node
                r.childRank = 1
                l = rpnStack.pop()
                l.parent = node
                node.children.append(l)
                node.children.append(r)
                rpnStack.push(node)
        return rpnStack.pop()

    def _handleTreeUpDown(self, node, _handleNode):
        _handleNode(node)
        for child in node.children: self._handleTreeUpDown(child, _handleNode)
    
    def _handleTreeDownUp(self, node, _handleNode):
        for child in node.children: self._handleTreeDownUp(child, _handleNode)
        _handleNode(node)
    
    def _printNode(self, node):
        if node != None: print str(node)
    
    def printTreeUpDown(self):
        self._handleTreeUpDown(self.root, self._printNode)
    
    def printTreeDownUp(self):
        self._handleTreeDownUp(self.root, self._printNode)

    def _mergeLoopNode(self, node):
        if node.type == TYPE_OP and node.item == SYMBOL_LOOP:
            node.children[0].loop.timesLoopStr(node.children[1].item)
            node.parent.children[node.childRank] = node.children[0]
            node.children[0].parent = node.parent
            node.children[1].parent = None
            for rank in range(0,len(node.parent.children)):
                node.parent.children[rank].childRank = rank
            node.parent = None
            del node.children
    
    def mergeLoopTreeDownUp(self):
        self._handleTreeDownUp(self.root, self._mergeLoopNode)
    
    def _mergeSameOpNode(self, node):
        if node.type == TYPE_OP and node.parent != None:
            if node.item == node.parent.item:
                if node.childRank == 0:
                    node.parent.children = node.children + node.parent.children[1:]
                else:
                    node.parent.children = node.parent.children[:node.childRank] + \
                    node.children + node.parent.children[node.childRank+1:]
                for child in node.children: child.parent = node.parent
                for rank in range(0,len(node.parent.children)):
                    node.parent.children[rank].childRank = rank
                node.parent = None
                del node.children
    
    def mergeSameOpTreeDownUp(self):
        self._handleTreeDownUp(self.root, self._mergeSameOpNode)


    # merge next list (wish list and candi list)
    def _genAvailList(self, node):
        availList = list()
        nextOne = False
        if node.type == TYPE_OP and node.avail and node.enable:
            for child in node.children:
                if child.avail and child.enable:
                    availList.append(child)
                    if child.loop.loopStatus == Loop.LOOP_STATUS_LESS:
                        nextOne = False
                    else: nextOne = True
                    if node.item == SYMBOL_NEXT and not nextOne: break
        return availList

    def _handleAvailTreeUpDown(self, node, _handleNode):
        _handleNode(node)
        #print node.item, ': ',
        #for child in _genAvailList(node): print child.item,
        #print
        for child in self._genAvailList(node): self._handleAvailTreeUpDown(child, _handleNode)

    def _genCandiList(self, node):
        availList = list()
        if node.type == TYPE_OP:
            for child in node.children:
                if child.avail and child.enable:
                    availList.append(child)
                    if child.loop.loopStatus == Loop.LOOP_STATUS_LESS:
                        nextOne = False
                    else: nextOne = True
                    if node.item == SYMBOL_NEXT and not nextOne: break
        return availList


    def _addWishList(self, node):
        if node.type == TYPE_VAR: self.wishList[node.item] = node

    def _generateWishList(self):
        self.wishList.clear()
        self._handleAvailTreeUpDown(self.root, self._addWishList)

    def _addCandiList(self, node):
        if node.type == TYPE_VAR: self.candiList[node.item] = node

    def _cleanupCandiList(self):
        pass


    def _generateCandiList(self, node):
        self.candiList.clear()
        self._handleTreeUpDown(node, self._addCandiList)


    def printWishList(self):
        print 'wish list:',
        for child in self.wishList.keys(): print child,
        print

    def printCandiList(self):
        print 'candi list:', 
        for child in self.candiList.keys(): print child,
        print


    # fire wish
    def _handleSingleTreeDownUp(self, node, _handleNode):
        _handleNode(node)
        if node.parent != None: self._handleSingleTreeDownUp(node.parent, _handleNode)

    def _handleBrother(self, node):
        if node.parent != None:
            if node.parent.type == TYPE_OP and node.parent.item == SYMBOL_OR:
                for child in node.parent.children:
                    if child.childRank != node.childRank: child.enable = False
            elif node.parent.type == TYPE_OP and node.parent.item == SYMBOL_AND:
                for child in node.parent.children:
                    if child.childRank != node.childRank:
                        if child.loop.stopFire():
                            child.enable = False
                            child.avail = child.loop.avail()
            elif node.parent.type == TYPE_OP and node.parent.item == SYMBOL_NEXT:
                for i in range(0, node.childRank):
                    node.parent.children[i].enable = False
                    node.parent.children[i].loop.stopFire()

    def _handleChildren(self, node):
        if node.item == SYMBOL_AND and len(node.children) > 0:
            doneList = [child for child in node.children if child.loop.fireStatus == Loop.FIRE_STATUS_DONE]
            allDone = (len(doneList) == len(node.children))
            inList = [child for child in node.children if child.loop.loopStatus == Loop.LOOP_STATUS_IN \
                      and child.loop.fireStatus != Loop.FIRE_STATUS_DONE]
            almostDone = (len(inList) + len(doneList) == len(node.children))
            return allDone, almostDone
        ############ catch or / next case to fire
        else: return False, False

    def _restartNode(self, node):
        node.loop.restart()
        node.avail = node.loop.avail()
        node.enable = True

    def _restartTreeUpDown(self, node):
        self._handleTreeUpDown(node, self._restartNode)


    def _fireWish(self, node):
        if node.type != TYPE_OP:
            node.loop.fire()
            node.avail = node.loop.avail()
        else:
            allDone, almostDone = self._handleChildren(node)
            if allDone:
                node.loop.fire() # count + 1
                # node.children (all) restart to 0
                if node.loop.loopStatus == Loop.LOOP_STATUS_LESS \
                or node.loop.loopStatus == Loop.LOOP_STATUS_IN:
                    for child in node.children: self._restartTreeUpDown(child)
            elif almostDone:
                print '!!!! almost done'
                # startFire
                # if node.loop.loopStatus:
                # -> less or in: candiList
                node.loop.startFire()
                if (node.loop.loopStatus == Loop.LOOP_STATUS_LESS \
                or node.loop.loopStatus == Loop.LOOP_STATUS_IN) \
                and node.loop.fireCount < node.loop.max - 1:
                    print '!!!! generate candi list'
                    self._generateCandiList(node)
            else:
                # startFire
                node.loop.startFire()
                
            node.avail = node.loop.avail()
            if node.avail: pass ########################### how to count one time is done???
            else: node.loop.startFire()
        self._handleBrother(node)

    # fire candi
    # node.parent: alldone or almostdone, restart counter
    def _restartForCandi(self): pass

    # fire itself. upDown fire parent
    # calculate the alldone and almostDone, generate candiList
    # fire wish???
    def _fireCandi(self): pass


    # fire
    def fire(self, statement):
        if self.wishList.get(statement, None) != None:
            self.candiList.clear()
            self._handleSingleTreeDownUp(self.wishList[statement], self._fireWish)
            self._generateWishList()
            return
        else:
            if self.candiList.get(statement, None) != None:
                self.candiList.clear()
                self._handleSingleTreeDownUp(self.candiList[statement], self._restartForCandi)
                self._handleSingleTreeDownUp(self.candiList[statement], self._fireCandi)
                self._generateWishList()
