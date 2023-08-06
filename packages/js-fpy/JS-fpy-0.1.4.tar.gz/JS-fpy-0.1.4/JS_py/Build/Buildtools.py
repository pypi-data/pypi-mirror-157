from JS_py.Build.Parser import parseline
from alive_progress import alive_bar
import logging
import os
from pyparsing import ParseResults
def build(path):
    pa = os.path.dirname(path)+'/'+os.path.basename(path)+'.build/'
    handler = logging.FileHandler(pa+"build.log")
    handler2 = logging.FileHandler(pa+"parse.log")
    blogger = logging.getLogger("build")
    blogger.setLevel(logging.INFO)
    blogger.addHandler(handler)
    plogger = logging.getLogger("Parser")
    plogger.setLevel(logging.INFO)
    plogger.addHandler(handler2)
    with open(path, 'r') as p:
        r = p.readlines()
        r.append("#Made using JS-fpy / JS-py. Debug Version\n ")
    r[len(r)-2] = r[len(r)-2] +"\n"
    indent = [0, 0]
    lastI = indent
    def indentWrapper(obj):
        
        dent = indent[0:]
        if type(obj[0]) != ParseResults:

            indent[1] = 0
            indent[0] = 0
            return [obj, dent]
        else:
            
            indentt = 0
            jj = obj
            
            while type(jj) == ParseResults:
                indentt += 1
                if len(jj) < 2:
                    jj = jj[0]
                else:
                    jj = jj[0:]
            indentt += 1

            if indent[0] < indentt:
                indent[1] += 1
            if indent[0] > indentt:
                indent[1] = indent[1] - 1
            indent[0] = indentt
            
            jj.insert(0, "".join([" " for x in range(indentt)]))
            return [jj, dent]
                
    index = 1
    with alive_bar(len(r)) as bar:
        for l in r:
            

         
            p = parseline(l,plogger,indent)
            
            p= indentWrapper(p)
            lastI = p[1]
            p = p[0]
          
            
            p = ''.join(p)
            blogger.info("Indent: "+str(indent)+ " Last indent: " + str(lastI))
             
            if lastI[1] > indent[1]:
                
                p = "};"+p
            
            blogger.info('Parsed Line '+str(index))
            
            with open(pa+'/cache/line-'+str(index)+'.ch', 'w') as w:
                w.write(l)
                w.write('//\\ Line '+str(index)+'\n')
                w.write(p.split("\n")[0]+' ')
            index += 1
            bar()
        
def finalize(path, args, name):
    handler = logging.FileHandler(path+"build.log")
    blogger = logging.getLogger("Finalize")
    blogger.setLevel(logging.INFO)
    blogger.addHandler(handler)
    build = []
    debug = []
    for filename in os.listdir(path+"cache/"):
        f = os.path.join(path+"cache/", filename)
        with open(f, 'r') as c:
            r = c.readlines()
            build.append(r[2])
            debug.append(r[1])
            debug.append(r[2])
        blogger.info("Appended: " + r[2])
    n = name[:-2]+'.js'
    if '-o' in args[3:]:
        with open('debug.'+n,'w') as d:
            d.write('\n'.join(debug))
    else:
        with open(path+'debug.'+n,'w') as d:
            d.write('\n'.join(debug))
    blogger.info("Wrote debug file")
    with open(n, 'w') as f:
        f.write('\n'.join(build))
    blogger.info("Wrote js file")