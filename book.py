#!/usr/bin/python
# coding:utf-8


##########################
# Script pour générer
# 1) les pdf synthétiques
# 2) le site web


import sys
import codecs
from SimulateurCarriere import *
from AnalyseCarriere import *
from tools import *
import matplotlib.pyplot as plt
import os


def generation_donnees(modeles, generations, variation_age, dir): # génération des simulations et des pensions

    carrieres = []

    # public

    for (ide,p,age) in cas_public:

        c = CarrierePublic(modeles[0], age, 1980, ide, p)
        fic = dir+"grille_"+c.id
        
        # génération des grilles
        if force_generate_figures  or  not os.path.isfile(fic+".pdf"):
            
            AnalyseCarriere(c).plot_grille()
            print(fic)
            plt.savefig(fic+".pdf")
            plt.close('all')

        ages=range(age,age+variation_age) # pour avoir éventuellement la variabilité par rapport à l'âge de départ

        l_perso = [] # type de carrière
        for k in range(len(types_carrieres)):
            l_age = []
            for a in ages:
                l_gen = []
                for gn in generations:
                    an = gn + a  # année de début
                    l_mod = []
                    for j in range(len(modeles)):
                        
                        l_mod.append( CarrierePublic(modeles[j], a, an, ide, p, types_carrieres[k][0]) )
                        
                    l_gen.append(l_mod)
                l_age.append(l_gen)
            l_perso.append(l_age)
        carrieres.append(l_perso)

    # privé
    
    for (id, metier, age, profil, base) in cas_prive:

        ages=range(age,age+variation_age) # pour avoir éventuellement la variabilité par rapport à l'âge de départ

        l_perso = [] # type de carrière
        for k in range(len(types_carrieres)):
            l_age = []
            for a in ages:
                l_gen = []
                for gn in generations:

                    an = gn + a  # année de début

                    l_mod = []
                    for j in range(len(modeles)):
                        
                        l_mod.append( CarrierePrive(modeles[j], a, an, id, metier, profil, base, types_carrieres[k][0]) )
                        
                    l_gen.append(l_mod)
                l_age.append(l_gen)
            l_perso.append(l_age)
        carrieres.append(l_perso)

    return carrieres

        

def comparaison_modeles(f, deb, fin, modeles, avec_tableaux):     ### Génération de la comparaison des modèles

    fic="fig/comparaison_modeles.pdf"
    if force_generate_figures  or  not os.path.isfile("./tex/"+fic):
        fig=plt.figure(figsize=(16.5,11))
        AnalyseModele.plot_modeles( modeles, [deb,fin] )
        print(fic)
        plt.savefig("./tex/"+fic)
        plt.close('all')
    f.write("\n \\begin{center}\\includegraphics[width=1\\textwidth]{%s}\\end{center} \n\n"%(fic))
    f.write("\\newpage \n \n")  

    if avec_tableaux:
        for m in modeles:
            f.write(dec("{\\bf Description détaillée du modèle \emph{"+(m.nom)+"}} \n "))
            f.write("\\begin{center} \\begin{adjustbox}{max width=0.7\\textwidth} \n")
            AnalyseModele(m).affiche_modele(True,f,deb,fin)
            f.write("\\end{adjustbox} \\end{center} \\newpage \n")

            
def resume_carriere(carrieres, g, z, modeles, lc, avec_tableaux, fic, dir, f=sys.stdout):  ### fonction qui affiche le résumé pour une carrière (g=numero de génération, z=enfants)

    c = carrieres[0]
    generate_figures =  force_generate_figures  or  not os.path.isfile(dir+"fig/"+fic+".pdf")
    
    if generate_figures:
        fig = plt.figure(figsize=(8*(len(modeles)+1),6),dpi=72)
        print(fic)

    # Affichage synthétique

    for j in range(len(modeles)): # modèles

        c = carrieres[j]

        f.write(dec("{\\bf \\noindent Retraites possibles et ratios Revenu/SMIC à 70, 75, 80, 85, 90 ans dans le modèle \\emph{"+modeles[j].nom+"}}  \n \n"))
        ana = AnalyseCarriere(c)

        f.write("\\begin{adjustbox}{max width=\\textwidth} \n")
        ana.affiche_pension_macron(z, True, f)
        f.write("\\end{adjustbox} \n \n \\vspace{0.1cm} \n")

        if generate_figures:
            # Affichage des graphiques synthétiques    
            ax = fig.add_subplot(1,len(modeles)+1,j+1)
            AnalyseCarriere.plot_evolution_carriere_corr(z, ax, c.m.smic, g, lc[j], lc[j][-1].annee_debut + lc[j][-1].age_mort-lc[j][-1].age_debut, "Revenu/SMIC", dec(modeles[j].nom), 1, 1)
            # Affichage du nombre de points
            ax = fig.add_subplot(1,len(modeles)+1,len(modeles)+1)
            ana.plot_points(ax, ["-.","--","-"][j], dec(modeles[j].nom))
            plt.legend(loc="upper left")
            plt.title(dec("Points retraite acquis par année"))

    if generate_figures:
        #fig.tight_layout() ### pour l'instant marche pas
        plt.savefig(dir+"fig/"+fic+".pdf")
        plt.close('all')

    f.write("\n {\\hspace{-2.2cm}\\includegraphics[width=1.1\\textwidth]{fig/%s}} \n\n"%(fic))     
    
    f.write("\\newpage \n \n")
                        
    if avec_tableaux:
    # Affichage détaillé
        for j in range(len(modeles)): # modèles
            
            c = carrieres[j]
            f.write(dec("{\\bf \\noindent Détails des revenus et points dans le modèle \emph{"+modeles[j].nom+"}}  \n \n"))
            ana = AnalyseCarriere(c)

            f.write("\\begin{center} \\begin{adjustbox}{max height=0.45\\textheight} \n")
            ana.affiche_carriere(True, f)
            f.write("\\end{adjustbox} \\end{center} \n")

            f.write("\\newpage \n\n")
    

####################################################
# Partie principale
####################################################


def genere_tex(file, generations, avec_tableaux):

    # Modèles de projection
    debut, fin = 1980, 2120
    modeles = [ ModeleGouv(debut,fin,1.3,True), ModeleGouv(debut,fin,1.3,False), ModeleDestinie(debut,fin)]

    variation_age=1
        
    #### Génération des données
        
    carrieres = generation_donnees(modeles, generations, variation_age, "tex/fig/")
                                
    f = codecs.open("tex/"+file+".tex", "w", "utf-8")   # création du fichier

    print("Génération du fichier: "+file+".tex")

    ### modèles
    
    comparaison_modeles(f, 1995, 2070, modeles, avec_tableaux)

    ### Génération des synthèses des simulations
    
    for i in range(len(carrieres)): # types de métiers

        c = carrieres[i][0][0][0][0]
        nom = c.nom_metier
        f.write(dec("\\chapter{"+nom+"} \n\n"))
        context = nom
        
        if c.public:
            fic="grille_"+c.id
            print(nom)
            f.write("\\begin{minipage}{0.55\\linewidth}\\includegraphics[width=0.7\\textwidth]{fig/"+fic+".pdf}\\end{minipage} \n")
            f.write("\\begin{minipage}{0.3\\linewidth} \n \\begin{center} \n\n")
            AnalyseCarriere(c).affiche_grille(True, f)
            f.write("\\end{center} \n \\end{minipage} \n\n")
        
        ### Type de carrières
        k = 0 # uniquement temps plein sans enfant
        
        z = types_carrieres[k][1]
        c = carrieres[i][k][0][0][0]
        txt = "Début de carrière à %d ans"%(c.age_debut) + " / " + c.perso #"Enfants: "+str(Carriere.parts_enfant[z][0])+" ("+Carriere.parts_enfant[z][1]+")"
        #f.write(dec("\\section{"+txt+"} \n\n"))
        #print(txt)
        f.write("~\\\\ \n \n \\noindent {\\bf "+dec(txt)+"} \n\n")

        f.write(dec("\n \\etocsetnexttocdepth{2} \\etocsettocstyle{\\subsubsection*{Date de naissance (et année de début de carrière)}}{} \n \\localtableofcontents \n\n"))
        f.write(dec("~\\\\ \n \n \\hyperlink{page.2}{\\noindent Retourner à la liste des métiers}\n\n \\newpage \n\n"))

        for g in range(len(generations)): # générations

            c = carrieres[i][k][0][g][0]
            fic = "%s_%d_%d_%d"%(c.id_carriere, c.age_debut, c.annee_debut - c.age_debut, z)
            txt2 = "Génération %d (début en %d)"%(c.annee_debut-c.age_debut, c.annee_debut)
            f.write(dec("\\section{"+txt2+"\\label{"+fic+"}} \n \n"))
            f.write("{\\bf \\noindent "+dec(context+" / "+txt)+"}  ~ \n\n ~\\\\" )

            z = types_carrieres[k][1]                
            resume_carriere(carrieres[i][k][0][g], g, z, modeles, [ [ carrieres[i][k][0][h][j] for h in range(len(generations)) ] for j in range(len(modeles)) ], avec_tableaux, fic, "tex/", f)
                
    f.close() # on ferme le fichier


##################################################
# Génération de la page web

def print_contexte(f, contexte, style="md"): 

    if style == "md":
        f.write(dec("*Votre sélection :* [(recommencer)](#top)\n\n"))
        for x in contexte:
            f.write("- " + dec(x)+"\n")
        f.write("\n")
    elif style == "tex":
        f.write("\\noindent ")
        for x in contexte:
            f.write(dec(x)+"\\\\\n")

    
def genere_html(generations, avec_tableaux):

    # Modèles de projection

    debut, fin = 1980, 2120
    modeles = [ ModeleGouv(debut,fin,1.3,True), ModeleGouv(debut,fin,1.3,False), ModeleDestinie(debut,fin)]

    variation_age=5
        
    #### Génération des données
    
    carrieres = generation_donnees(modeles, generations, variation_age, "web/fig/")

    file="./web/index.md"
    f = codecs.open(file, "w", "utf-8")   # création du fichier
    
    print("Génération du fichier: "+file)

    f.write("<!doctype html>\n<html lang=\"fr\"><head><meta charset=\"UTF-8\">\n\n")
    
    #f.write("<script type=\"text/javascript\" src=\"https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.0/MathJax.js?config=TeX-AMS_CHTML\"></script>\n\n") # pour les équations 

    ### Génération des synthèses des simulations 

    f.write(dec("### Quelle trajectoire professionnelle ? <a name=\"top\"></a> \n\n"))
    for i in range(len(carrieres)): # types de métiers
        c = carrieres[i][0][0][0][0]
        link="%d"%i
        f.write("- ["+dec(c.nom_metier+"](#"+link+") \n"))
    f.write("<br>"*50+"\n")
    
    for i in range(len(carrieres)): 
        c = carrieres[i][0][0][0][0]
        context = [ c.nom_metier ]
        link="%d"%i
        f.write("***\n<a name=\""+link+"\"></a>")
        print_contexte(f, context, "md")

        print(context)
        sys.stdout.flush()
        
        f.write(dec("### Quel type de carrière ? \n\n"))
        for k in range(len(types_carrieres)):
            z = types_carrieres[k][1]
            c = carrieres[i][k][0][0][0]
            link="%d_%d"%(i,k)
            txt = c.perso_md +" / Enfants: " + str(Carriere.parts_enfant[z][0]) + " (" + Carriere.parts_enfant[z][1] + ")"
            f.write( "- [" + dec(txt) + "](#"+link+") \n")
        f.write("<br>"*50+"\n")
                
        ### Type de carrières

        for k in range(len(types_carrieres)):
            
            z = types_carrieres[k][1]
            c = carrieres[i][k][0][0][0]
            link = "%d_%d"%(i,k)
            txt = c.perso_md +" / Enfants: " + str(Carriere.parts_enfant[z][0]) + " (" + Carriere.parts_enfant[z][1] + ")"
            context.append( txt )
            f.write("***\n<a name=\""+link+"\"></a>")
            print_contexte(f, context, "md")

            ages = range(c.age_debut, c.age_debut + variation_age) # pour avoir éventuellement la variabilité par rapport à l'âge de départ

            f.write(dec("### Quel âge de début de carrière ? \n\n"))
            for a in range(len(ages)):
                c = carrieres[i][k][a][0][0]
                link = "%d_%d_%d"%(i,k,a)
                txt = "Début de carrière à %d ans"%c.age_debut
                f.write( "- ["+ dec(txt) + "](#"+link+") \n")
            f.write("<br>"*50+"\n")
            
            ### Ages possible de début
            
            for a in range(len(ages)):

                c = carrieres[i][k][a][0][0]
                link="%d_%d_%d"%(i,k,a)
                txt = "Début de carrière à %d ans"%c.age_debut
                context.append( txt )
                f.write("***\n<a name=\""+link+"\"></a> ")
                print_contexte(f, context, "md")
                
                f.write(dec("### Quelle année de naissance (année de début de carrière) ? \n\n"))
                for g in range(len(generations)):
                    
                    c = carrieres[i][k][a][g][0]
                    link = "%d_%d_%d_%d"%(i,k,a,g)
                    txt = "Génération %d (début en %d)"%(c.annee_debut-c.age_debut, c.annee_debut)
                    f.write( "- [" + dec(txt) + "](#" + link + ") \n")
                    
                f.write("<br>"*50+"\n")

                for g in range(len(generations)):
                    
                ### création du fichier tex personnalisé

                    c = carrieres[i][k][a][g][0]
                    link = "%d_%d_%d_%d"%(i,k,a,g)
                    txt = "Génération %d (début en %d)"%(c.annee_debut-c.age_debut, c.annee_debut)
                    context.append( txt )
                    fic = c.id_carriere+"_%d_%d_%d"%(c.age_debut, c.annee_debut-c.age_debut, z)
                    f.write("***\n<a name=\""+link+"\"></a>")
                    print_contexte(f, context, "md")
                    f.write(dec("[Téléchargez la simulation](" + fic + ".pdf)\n"))
                    f.write("<br>"*50+"\n")
                    

                    if force_generate_figures  or  not os.path.isfile("web/"+fic+".pdf"):
                    
                        f2 = codecs.open("web/"+fic+".tex", "w", "utf-8")   # création du fichier

                        f2.write("\\documentclass[a4paper,10pt]{report}\n\n")
                        f2.write("\\input{preambule}\n\n")
                        f2.write("\\begin{document}\n\n")

                        nom = c.nom_metier
                        f2.write(dec("\\chapter*{"+nom+"} \n\n"))

                        if c.public:
                            fic2="grille_"+c.id
                            f2.write("\\begin{minipage}{0.55\\linewidth}\\includegraphics[width=0.7\\textwidth]{fig/"+fic2+".pdf}\\end{minipage} \n")
                            f2.write("\\begin{minipage}{0.3\\linewidth} \n \\begin{center} \n\n")
                            AnalyseCarriere(c).affiche_grille(True, f2)
                            f2.write("\\end{center} \n \\end{minipage} \n\n")

                        context2 = context[:]
                        context2[0] = c.perso
                        context2[1] = "Enfants: " + str(Carriere.parts_enfant[z][0]) + " (" + Carriere.parts_enfant[z][1] + ")"
                        f2.write("\n~\\\\\n\n")
                        print_contexte(f2, context2, "tex")
                        f2.write("\n\n")


                        f2.write("\n~\\\\\n\n")
                        f2.write(dec("\\emph{Ce document présente des simulations de pension dans un système de retraite à points pur (sans transition avec le système actuel). Les pages suivantes contiennent 3 simulations, correspondant chacune à un modèle macro-économique:\n"))
                        f2.write("\\begin{itemize}\n")
                        f2.write(dec("\\item le modèle utilisé par le gouvernement (avec âge pivot bloqué à 65 ans) ;\n"))
                        f2.write(dec("\\item le modèle utilisé par le gouvernement corrigé (avec âge pivot glissant) ;\n"))
                        f2.write(dec("\\item le modèle Destinie2 (avec âge pivot glissant), qui prévoit une indexation du public sur le salaire moyen.\n"))
                        f2.write("\\end{itemize}\n")
                        f2.write(dec("La page suivante donne une synthèse des simulations. Les 3 pages qui suivent contiennent des tableaux détaillés pour chacune des 3 simulations.}\n\n"))

                        f2.write("\\newpage\n\n")

                        resume_carriere(carrieres[i][k][a][g], 0, z, modeles, [ [ carrieres[i][k][a][g][j] ] for j in range(len(modeles)) ], avec_tableaux, fic, "web/", f2)

                        f2.write("\\end{document}\n")
                        f2.close() # on ferme le fichier tex

                        os.chdir("web/") # on se met dans le bon répertoire
                        for repete in range(2):
                            shell_command("pdflatex "+fic+".tex")
                        shell_command("rm " + fic + ".aux " + fic + ".out " + fic + ".log " + fic + ".tex " + "fig/" + fic + ".pdf")
                        os.chdir("..")
                        
                    context = context[0:3]
                context = context[0:2]
            context = context[0:1]
                
    f.write("</html>")
            
    f.close() # on ferme le fichier web

    os.chdir("web/")
    shell_command("markdown index.md > index.html")
    os.chdir("..")
    


#############
## Carrières

# dans le public

cas_public = [ ("Infirmier",0.299, 22),
               ("AideSoignant",0.242, 22),
               ("TechHosp",0.27, 22),
               ("AdjTech", 0.223, 22),
               ("Redacteur",0.281, 22),
               ("SecretaireAdmin",0.403, 22),
               ("ATSEM",0.16, 22),
               ("ProfEcoles",0.081, 22),
               ("ProfCertifie",0.096, 22),
               ("ProfAgrege",0.096, 22),
               ("BIATSS",0.1,22),
               ("MCF",0.034,23),
               ("CR",0.034,23),
               ("PR",0.071,23), ("DR",0.071,25),
               ("Magistrat",0.547,22)  ]


# dans le privé

cas_prive = [ ("SMPT","Salarié privé au salaire moyen durant toute sa carrière", 22, [1.0]*50, "SMPT"),
              ("SMIC","Salarié privé au SMIC durant toute sa carrière", 22, [1.0]*50, "SMIC"),
              ("Ascendant12","Salarié privé évoluant du SMIC à 2*SMIC", 22, [ 1.0 + i/43. for i in range(50) ],"SMIC"),
              ("Ascendant1525","Salarié privé évoluant de 1.5*SMIC à 2.5*SMIC", 22, [ 1.5 + i/43. for i in range(50) ],"SMIC"),
              ("Ascendant23","Salarié privé évoluant de 2*SMIC à 3*SMIC", 22, [ 2.0 + i/43. for i in range(50) ],"SMIC"),
              ("Ascendant34","Salarié privé évoluant du 3*SMIC à 4*SMIC", 22, [ 3.0 + i/43. for i in range(50) ],"SMIC"),
              ("Ascendant45","Salarié privé évoluant du 3*SMIC à 4*SMIC", 22, [ 4.0 + i/43. for i in range(50) ],"SMIC"),
              ("10SMIC","Salarié privé à 10*SMIC durant toute sa carrière", 22, [10.0]*50, "SMIC")
]


### Pour générer les images pour quelques profils seulement
#cas_public = [ ("Infirmier", 0.299, 22) ] #("ATSEM", 0.299, 22) ]
#cas_prive = [ ("SMPT","Salarié privé au salaire moyen durant toute sa carrière", 22, [1.0]*50, "SMPT") ]



# types de carrières (quotité, numero du nombre d'enfants)

types_carrieres = [ ([1.0],                       0),  # temps plein, pas d'enfant
                   # ([1.0],                       1),  # temps plein, pas d'enfant
                   # ([1.0],                       2),  # temps plein, pas d'enfant
                   # ([0.5],                       1),  # mi-temps, 2 enfants
                    ([0.5],                       2),  # mi-temps, 2 enfants
                   # ([1.0, (30, 0.6), (40, 1.)],  1),  # temps plein, puis à 60% entre 30 et 40 ans, 2 enfants
                    ([1.0, (30, 0.6), (40, 1.)],  2)   # temps plein, puis à 60% entre 30 et 40 ans, 2 enfants
]

force_generate_figures = False

def tex():
    genere_tex("corps", [1975, 1980, 1990, 2003], False)
    genere_tex("corps2", [1975, 1980, 1990, 2003], True)
    os.chdir("tex/") # on se met dans le bon répertoire
    for fic in ["book", "book2"]:
        for repete in range(2):
            shell_command("pdflatex " + fic + ".tex")
        shell_command("rm " + fic + ".aux " + fic + ".out " + fic + ".log ")
    os.chdir("..")


def html():
    genere_html( range(1975, 2006,5), True)


tex()
html()
