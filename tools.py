#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import prettytable as pt


def euroconst(m, tex=False):
    if tex:
        return "\\euro{} "+str(m.annee_ref)
    else:
        return "Euro"+str(m.annee_ref)

def shell_command(com,verbose=True):
    if verbose:
        print(com)
    os.system(com)


# pour le codage utf8

def dec(s):
    return s.decode("utf-8")


# Pour afficher des tableaux (en texte et latex)

def seuil_tex(x,s):
    if x<s:
        return "{\color{red} %.2f}"%x
    else:
        return "%.2f"%x


def tex_row(l, colemph=[]):
    s = ""
    for i in range(len(l)):
        if i in colemph:
            s += " {\\bf "+dec(l[i])+"}"
        else:
            s += " "+dec(l[i])
        if i<len(l)-1:
            s += " & " 
    return s+" \\\\ \n"


def print_table(l, f=sys.stdout, tex=False, texparams="", colemph=[]): # fonction pour afficher soit des prettytable, soit du code en latex

    if tex:

        f.write("\\begin{tabular}[htb]"+texparams+" \n")
        f.write("\\hline \n")
        f.write(tex_row(l[0])) #,range(len(l[0]))))
        f.write("\\hline \hline \n")

        for i in range(1,len(l)):
            f.write(tex_row(l[i],colemph))
            f.write("\\hline \n")

        f.write("\\hline \n")
        f.write("\\end{tabular} \n")
        
    else:

        x = pt.PrettyTable()

        x.field_names = l[0]

        for i in range(1,len(l)):
            x.add_row(l[i])

        f.write(x.get_string())
