from .layout import *

class InvalidLayoutCombinationError(Exception):
    def __init__(self, firstLayout, secondLayout) -> None:
        self.message = f"{firstLayout} and {secondLayout} is not a valid layout or a valid layout combination."
        super().__init__(self.message)

def qwkm(message):
    messageList = [x for x in message]
    ans = []
    i = 0
    while i < len(messageList):
        if messageList[i] == ',':
            if messageList[i-1] in qwerty:
                ans.append(kedmanee[qwerty.index(messageList[i])])
            elif messageList[i-1] in kedmanee:
                ans.append(qwerty[kedmanee.index(messageList[i])])
            else:
                ans.append(kedmanee[qwerty.index(messageList[i])])
        elif messageList[i] == '.':
            if messageList[i-1] in kedmanee:
                ans.append(qwerty[kedmanee.index(messageList[i])])
            elif messageList[i-1] in qwerty:
                ans.append(kedmanee[qwerty.index(messageList[i])])
            else:
                ans.append(kedmanee[qwerty.index(messageList[i])])
        elif messageList[i] == '-':
            if messageList[i-1] == ' ' and messageList[i+1] == ' ':
                ans.append(qwerty[kedmanee.index(messageList[i])])
            elif messageList[i-1] in kedmanee:
                ans.append(qwerty[kedmanee.index(messageList[i])])
            elif messageList[i-1] in qwerty:
                ans.append(kedmanee[qwerty.index(messageList[i])])
            else:
                ans.append(qwerty[kedmanee.index(messageList[i])])
        elif messageList[i] in kedmanee:
            ans.append(qwerty[kedmanee.index(messageList[i])])
        elif messageList[i] in qwerty:
            ans.append(kedmanee[qwerty.index(messageList[i])])
        elif messageList[i] == ' ':
            ans.append(' ')
        else:
            ans.append(messageList[i])
        i += 1
    answer = ''.join(ans)
    return answer

def qwmn(message):
    messageList = [x for x in message]
    ans = []
    i = 0
    while i < len(messageList):
        if messageList[i] == '-':
            ans.append(messageList[i])
        elif messageList[i] in manoonchai:
            ans.append(qwerty[manoonchai.index(messageList[i])])
        elif messageList[i] in qwerty:
            ans.append(manoonchai[qwerty.index(messageList[i])])
        elif messageList[i] == ' ':
            ans.append(' ')
        else:
            ans.append(messageList[i])
        i += 1
    answer = ''.join(ans)
    return answer

def dvkm(message):
    messageList = [x for x in message]
    ans = []
    i = 0
    while i < len(messageList):
        if messageList[i] == '/':
            if messageList[i-1] == " " and messageList[i+1] == " ":
                ans.append(dvorak[kedmanee.index(messageList[i])])
            elif messageList[i-1] in kedmanee:
                ans.append(dvorak[kedmanee.index(messageList[i])])
            elif messageList[i-1] in dvorak:
                ans.append(kedmanee[dvorak.index(messageList[i])])
            else:
                ans.append(dvorak[kedmanee.index(messageList[i])])
        elif messageList[i] == ',':
            if messageList[i-1] in dvorak:
                ans.append(kedmanee[dvorak.index(messageList[i])])
            elif messageList[i-1] in kedmanee:
                ans.append(dvorak[kedmanee.index(messageList[i])])
            else:
                ans.append(kedmanee[dvorak.index(messageList[i])])
        elif messageList[i] == '.':
            if messageList[i-1] in kedmanee:
                ans.append(dvorak[kedmanee.index(messageList[i])])
            elif messageList[i-1] in dvorak:
                ans.append(kedmanee[dvorak.index(messageList[i])])
            else:
                ans.append(kedmanee[dvorak.index(messageList[i])])
        elif messageList[i] == '-':
            if messageList[i-1] == ' ' and messageList[i+1] == ' ':
                ans.append(dvorak[kedmanee.index(messageList[i])])
            elif messageList[i-1] in kedmanee:
                ans.append(dvorak[kedmanee.index(messageList[i])])
            elif messageList[i-1] in dvorak:
                ans.append(kedmanee[dvorak.index(messageList[i])])
            else:
                ans.append(dvorak[kedmanee.index(messageList[i])])
        elif messageList[i] in kedmanee:
            ans.append(dvorak[kedmanee.index(messageList[i])])
        elif messageList[i] in dvorak:
            ans.append(kedmanee[qwerty.index(messageList[i])])
        elif messageList[i] == ' ':
            ans.append(' ')
        else:
            ans.append(messageList[i])
        i += 1
    answer = ''.join(ans)
    return answer

def dvmn(message):
    messageList = [x for x in message]
    ans = []
    i = 0
    while i < len(messageList):
        if messageList[i] == '-':
            ans.append(messageList[i])
        elif messageList[i] in manoonchai:
            ans.append(dvorak[manoonchai.index(messageList[i])])
        elif messageList[i] in dvorak:
            ans.append(manoonchai[dvorak.index(messageList[i])])
        elif messageList[i] == ' ':
            ans.append(' ')
        else:
            ans.append(messageList[i])
        i += 1
    answer = ''.join(ans)
    return answer

def convert(EngLayout, ThaLayout, Message):
    if ThaLayout == 'Kedmanee':
        if EngLayout == 'QWERTY':
            return qwkm(Message)
        elif EngLayout == 'Dvorak':
            return dvkm(Message)
        else: InvalidLayoutCombinationError(ThaLayout, EngLayout)
    elif ThaLayout == 'Manoonchai':
        if EngLayout == 'QWERTY':
            return qwmn(Message)
        elif EngLayout == 'Dvorak':
            return dvmn(Message)
        else: InvalidLayoutCombinationError(ThaLayout, EngLayout)
    else: InvalidLayoutCombinationError(ThaLayout, EngLayout)