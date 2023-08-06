from pyparsing import *
from pyparsing import *
import string
import logging
def ident(t, n, v):
    
    return v[0:]
def evalVar(t, n, v):
    m = t.split(' ')
    
    if m[len(m)-1].startswith('<$:'):
        
        v = m[len(m)-1].replace('<$:','').replace('$>','').replace('\n','')
        m.insert(0, v)
        
        del m[len(m)-1]
        m.append('\n')
        
    else:
        m.insert(0,'var')
    

    return ' '.join(m)
def evalIf(t, n, v):
    
    mid = v[1]
    mid = mid[1:]
    mid = "(" +mid+ ")"
    end = "{\n"
    e = "if "+ mid +" "+ end
    
    return "if "+ mid +" "+ end
all = identbodychars+printables+' '+'\t'+'\n'
nall = all.replace('#','').replace(' ','').replace(')','').replace('(','')
deadline = StringStart()+ZeroOrMore(White()) + StringEnd()
comment = Char('#').setParseAction(replaceWith('//')) + ZeroOrMore(Word(all))
ifblock = (Keyword("if") + OneOrMore(Word(all.replace(':',''))) + Char(":")).setParseAction(evalIf)
ifblock.leaveWhitespace()
indent = Forward()
block = ifblock
keycall = Word("print")
keycall.setParseAction(replaceWith('console.log'))
tuple = Char('(') + Optional(delimitedList(Word(nall), delim=',')) + Char(')')
call = (keycall | Word(alphanums+'_')) + tuple.leaveWhitespace()
call.leaveWhitespace()
set = (Word(alphanums+'_') + ' ' + Keyword('=') +' ' + Word(all.replace('#',''))).setParseAction(evalVar)
set.leaveWhitespace()
activeline = (set | call)
activeline.leaveWhitespace()
comment.leave_whitespace()
cactiveline = activeline + ZeroOrMore(White()) + comment
cactiveline.leaveWhitespace()
deadline.leaveWhitespace()
indent <<= (indentedBlock((cactiveline | activeline | block | deadline | indent), [1])).setParseAction(ident)
indent.leaveWhitespace()
line = comment  | cactiveline |activeline| block | deadline | indent
class BuildError(Exception):
    pass
def parseline(l, pa, block):
    
    
    try:
        
        ll = line.parse_string(l)
        
        pa.info(f'String "{l}" parsed to {ll}'.encode())
        error = False
    except ParseException as o:
        error = True
        orr = o
    if error:
        raise BuildError(orr)
    return ll