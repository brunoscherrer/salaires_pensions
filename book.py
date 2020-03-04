#!/usr/bin/python
# coding:utf-8

import sys
import codecs
from SimulateurCarriere import *
from AnalyseCarriere import *
from tools import *
import matplotlib.pyplot as plt


def generation_donnees(modeles, generations, variation_age): # génération des simulations et des pensions

    carrieres = []

    # public

    for (ide,p,age) in cas_public:

        # génération de la grille
        if not just_tex:
            c=CarrierePublic(modeles[0], age, 1980, ide, p)
            fic="grille_"+c.id_metier
            AnalyseCarriere(c).plot_grille()
            print(fic)
            plt.savefig("./tex/fig/"+fic+".pdf")
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
    
    for (id_metier, metier, age, profil, base) in cas_prive:

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
                        
                        l_mod.append( CarrierePrive(modeles[j], a, an, id_metier, metier, profil, base, types_carrieres[k][0]) )
                        
                    l_gen.append(l_mod)
                l_age.append(l_gen)
            l_perso.append(l_age)
        carrieres.append(l_perso)

    return carrieres

        

def comparaison_modeles(f, deb, fin, modeles, avec_tableaux):     ### Génération de la comparaison des modèles

    fic="fig/comparaison_modeles.pdf"
    if not just_tex:
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

            
def resume_carriere(carrieres, g, z, modeles, generations, avec_tableaux, fic, f=sys.stdout):  ### fonction qui affiche le résumé pour une carrière (g=numero de génération, z=enfants)

    c = carrieres[g][0]
    
    if not just_tex:
        fig = plt.figure(figsize=(8*(len(modeles)+1),6),dpi=72)
        print(fic)

    # Affichage synthétique
    for j in range(len(modeles)): # modèles

        c = carrieres[g][j]

        f.write(dec("{\\bf \\noindent Retraites possibles et ratios Revenu/SMIC à 70, 75, 80, 85, 90 ans dans le modèle \\emph{"+modeles[j].nom+"}}  \n \n"))
        ana = AnalyseCarriere(c)

        f.write("\\begin{adjustbox}{max width=\\textwidth} \n")
        ana.affiche_pension_macron(z, True, f)
        f.write("\\end{adjustbox} \n \n \\vspace{0.1cm} \n")

        if not just_tex:
            # Affichage des graphiques synthétiques    
            ax = fig.add_subplot(1,len(modeles)+1,j+1)
            lc = [ carrieres[h][j] for h in range(len(generations)) ]  # rajoute contexte temporel
            AnalyseCarriere.plot_evolution_carriere_corr(z, ax, c.m.smic, g, lc, lc[-1].annee_debut + lc[-1].age_mort-lc[-1].age_debut, "Revenu/SMIC", dec(modeles[j].nom), 1, 1)
            # Affichage du nombre de points
            ax = fig.add_subplot(1,len(modeles)+1,len(modeles)+1)
            ana.plot_points(ax, ["-.","--","-"][j], dec(modeles[j].nom))
            plt.legend(loc="upper left")
            plt.title(dec("Points retraite acquis par année"))

    if not just_tex:
        #fig.tight_layout() ### pour l'instant marche pas
        plt.savefig("./tex/fig/"+fic+".pdf")
        plt.close('all')

    f.write("\n {\\hspace{-2.2cm}\\includegraphics[width=1.1\\textwidth]{fig/%s}} \n\n"%(fic))     
    
    f.write("\\newpage \n \n")
                        
    if avec_tableaux:
    # Affichage détaillé
        for j in range(len(modeles)): # modèles
            
            c = carrieres[g][j]
            f.write(dec("{\\bf \\noindent Détails des revenus et points dans le modèle \emph{"+modeles[j].nom+"}}  \n \n"))
            ana = AnalyseCarriere(c)

            f.write("\\begin{center} \\begin{adjustbox}{max height=0.45\\textheight} \n")
            ana.affiche_carriere(True, f)
            f.write("\\end{adjustbox} \\end{center} \n")

            f.write("\\newpage \n\n")
    

####################################################
# Partie principale
####################################################


def genere(file, generations, avec_tableaux):

    # Modèles de projection
    debut, fin = 1980, 2120
    modeles = [ ModeleGouv(debut,fin,1.3,True), ModeleGouv(debut,fin,1.3,False), ModeleDestinie(debut,fin)]

    variation_age=4
        
    #### Génération des données
        
    carrieres = generation_donnees(modeles, generations, variation_age)
                                
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
            fic="grille_"+c.id_metier
            print(nom)
            f.write("\\begin{minipage}{0.55\\linewidth}\\includegraphics[width=0.7\\textwidth]{fig/"+fic+".pdf}\\end{minipage} \n")
            f.write("\\begin{minipage}{0.3\\linewidth} \n \\begin{center} \n\n")
            AnalyseCarriere(c).affiche_grille(True, f)
            f.write("\\end{center} \n \\end{minipage} \n\n")
        
        ### Type de carrières
        k = 0
        
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
            fic = "%s_%d_%d_%d"%(c.id_metier, c.annee_debut-c.age_debut, c.age_debut, z)
            txt2 = "Génération %d (début en %d)"%(c.annee_debut-c.age_debut, c.annee_debut)
            f.write(dec("\\section{"+txt2+"\\label{"+fic+"}} \n \n"))
            f.write("{\\bf \\noindent "+dec(context+" / "+txt)+"}  ~ \n\n ~\\\\" )

            z = types_carrieres[k][1]                
            resume_carriere(carrieres[i][k][0], g, z, modeles, generations, avec_tableaux, fic, f)
                
    f.close() # on ferme le fichier




   
def genere_detail(file, generations, avec_tableaux):

    # Modèles de projection
    debut, fin = 1980, 2120
    modeles = [ ModeleGouv(debut,fin,1.3,True), ModeleGouv(debut,fin,1.3,False), ModeleDestinie(debut,fin)]

    variation_age=1
        
    #### Génération des données
        
    carrieres = generation_donnees(modeles, generations, variation_age)
                                
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
            fic="grille_"+c.id_metier
            print(nom)
            f.write("\\begin{minipage}{0.55\\linewidth}\\includegraphics[width=0.7\\textwidth]{fig/"+fic+".pdf}\\end{minipage} \n")
            f.write("\\begin{minipage}{0.3\\linewidth} \n \\begin{center} \n\n")
            AnalyseCarriere(c).affiche_grille(True, f)
            f.write("\\end{center} \n \\end{minipage} \n\n")
        
        ### Type de carrières
        k = 0
        
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
            fic = "%s_%d_%d_%d"%(c.id_metier, c.annee_debut-c.age_debut, c.age_debut, z)
            txt2 = "Génération %d (début en %d)"%(c.annee_debut-c.age_debut, c.annee_debut)
            f.write(dec("\\section{"+txt2+"\\label{"+fic+"}} \n \n"))
            f.write("{\\bf \\noindent "+dec(context+" / "+txt)+"}  ~ \n\n ~\\\\" )

            z = types_carrieres[k][1]                
            resume_carriere(carrieres[i][k][0], g, z, modeles, generations, avec_tableaux, fic, f)
                
    f.close() # on ferme le fichier

 


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
#cas_public = []
#cas_prive = [ ("SMPT","Salarié privé au salaire moyen durant toute sa carrière", 22, [1.0]*50, "SMPT"),              ("SMIC","Salarié privé au SMIC durant toute sa carrière", 22, [1.0]*50, "SMIC") ]



# types de carrières (quotité, numero du nombre d'enfants)

types_carrieres = [ ([1.0],                       0),  # temps plein, pas d'enfant
                    ([1.0, (30, 0.6), (40, 1.)],  2),  # temps plein, puis à 60% entre 30 et 40 ans, 2 enfants
                    ([0.5],                       2)   # mi-temps, 2 enfants
]


just_tex = True
genere("corps", [1975, 1980, 1990, 2003], False)
#just_tex = False
genere("corps2", [1975, 1980, 1990, 2003], True)

exit(1)

genere("detail")
just_tex = False
genere(False,False)
