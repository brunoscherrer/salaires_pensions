#!/usr/bin/python
# coding:utf-8

import sys
import codecs
from SimulateurCarriere import *
from AnalyseCarriere import *
from tools import *
import matplotlib.pyplot as plt


just_tex = True # pour simplement regénerer le tex

####################################################
# Partie principale
####################################################


version_courte = False 
#version_courte = True

if version_courte:
    variation_age=1
else:
    variation_age=3
    
########################
# Modèles de projection

debut, fin = 1980, 2120

modeles = [ ModeleGouv(debut,fin,1.3,True), ModeleGouv(debut,fin,1.3,False), ModeleDestinie(debut,fin)]

##############
# Générations

if version_courte:
    generations = [1975, 1980, 1990, 2003] # générations de l'étude d'impact
else:
    generations = range(1975,2006,1) # de 1975 à 2005

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
               ("MCF",0.034,25),
               ("CR",0.034,25),
               ("PR",0.071,25), ("DR",0.071,25),
               ("Magistrat",0.547,22)  ]


# dans le privé

cas_prive = [ ("SMPT","Salarié privé au salaire moyen durant toute sa carrière", 22, [1.0]*50, "SMPT"),
              ("SMIC","Salarié privé au SMIC durant toute sa carrière", 22, [1.0]*50, "SMIC"),
              ("Ascendant12","Salarié privé évoluant du SMIC à 2*SMIC", 22, [ 1.0 + i/43. for i in range(50) ],"SMIC"),
              ("Ascendant1525","Salarié privé évoluant de 1.5*SMIC à 2.5*SMIC", 22, [ 1.5 + i/43. for i in range(50) ],"SMIC"),
              ("Ascendant23","Salarié privé évoluant de 2*SMIC à 3*SMIC", 22, [ 2.0 + i/43. for i in range(50) ],"SMIC"),
              ("Ascendant34","Salarié privé évoluant du 3*SMIC à 4*SMIC", 22, [ 3.0 + i/43. for i in range(50) ],"SMIC"),
              ("Ascendant45","Salarié privé évoluant du 4*SMIC à 5*SMIC", 22, [ 4.0 + i/43. for i in range(50) ],"SMIC"),
              ("Riche","Salarié privé à 10*SMIC durant toute sa carrière", 22, [10.0]*50, "SMIC")
]


#############################################
# génération des simulations et des pensions

carrieres = []


# public

for (ide,p,age) in cas_public:

    # génération de la grille
    
    fic="grille_%s.pdf"%(ide)
    c=CarrierePublic(modeles[0], age, 1980, ide, p)
    if not just_tex:
        AnalyseCarriere(c).plot_grille()
        print fic
        plt.savefig("./tex/fig/"+fic)
        plt.close('all')
    
    ages=range(age,age+variation_age) # pour avoir éventuellement la variabilité par rapport à l'âge de départ
    
    l_age = []
    for a in ages:
        l_gen = []
        for gn in generations:
            an = gn + a  # année de début
            l_mod = []
            for j in range(len(modeles)):
                l_mod.append( CarrierePublic(modeles[j], a, an, ide, p) )
            l_gen.append(l_mod)
        l_age.append(l_gen)
    carrieres.append(l_age)

        
# privé

for (id_metier, metier, age, profil, base) in cas_prive:

    ages=range(age,age+variation_age) # pour avoir éventuellement la variabilité par rapport à l'âge de départ

    l_age = []
    for a in ages:
        l_gen = []
        for gn in generations:
            an = gn + a  # année de début
            l_mod = []
            for j in range(len(modeles)):
                l_mod.append( CarrierePrive(modeles[j], a, an, id_metier, metier, profil, base) )
            l_gen.append(l_mod)
        l_age.append(l_gen)
    carrieres.append(l_age)




###########################################################################################
    
###########################################
#### Génération du corps du fichier LateX

if version_courte:
    file="corps"
else:
    file="corps-long"
f = codecs.open("tex/"+file+".tex", "w", "utf-8")

    
### Génération de la comparaison des modèles

deb,fin=2000,2070

fic="fig/comparaison_modeles.pdf"
if not just_tex:
    fig=plt.figure(figsize=(18,12))
    AnalyseModele.plot_modeles( modeles, [deb,fin] )
    print(fic)
    plt.savefig("./tex/"+fic)
    plt.close('all')
f.write("\n \\begin{center}\\includegraphics[width=1\\textwidth]{%s}\\end{center} \n\n"%(fic))
f.write("\\newpage \n \n")  

for m in modeles:
    f.write(dec("\paragraph{Description détaillée du modèle \emph{"+(m.nom)+"}} \n \n "))
    f.write("{ \\tiny \\begin{center} \n")
    AnalyseModele(m).affiche_modele(True,f,deb,fin)
    f.write("\\end{center} } \n\\newpage \n \n") 
    
    
### Génération des simulations


for i in range(len(carrieres)): # metiers

    c = carrieres[i][0][0][0]
    nom = c.nom_metier
    print nom
    f.write(dec("\\chapter{%s} \n\n"%nom))
    fic="grille_%s.pdf"%(c.id_metier)
    
    if c.public:
        f.write("\\begin{minipage}{0.55\\linewidth}\\includegraphics[width=0.7\\textwidth]{%s}\\end{minipage} \n"%("fig/"+fic))
        f.write("\\begin{minipage}{0.3\\linewidth} \n \\begin{center} \n\n")
        AnalyseCarriere(c).affiche_grille(True, f)
        f.write("\\end{center} \n \\end{minipage} \n\n")
    
    f.write(dec("\n \\addto{\\captionsenglish}{ \\renewcommand{\\mtctitle}{}} \\setcounter{minitocdepth}{2} \n \\minitoc \\newpage \n\n"))
    
    for a in range(len(carrieres[i])): # age de début

        c = carrieres[i][a][0][0]
        f.write(dec("\\section{Début de carrière à %d ans} \n\n"%(c.age_debut)))
        
        for g in range(len(carrieres[i][a])): # générations

            c = carrieres[i][a][g][0]
            f.write(dec("\\subsection{Génération %d (début en %d)} \n\n"%(c.annee_debut-c.age_debut, c.annee_debut)))

            if not just_tex:
                fig = plt.figure(figsize=(8*len(modeles),6),dpi=72)

            # Affichage synthétique
            for j in range(len(carrieres[i][a][g])): # modèles

                c = carrieres[i][a][g][j]
                f.write(dec("\\paragraph{Retraites possibles et ratios Revenu/SMIC à 70, 75, 80, 85, 90 ans avec le modèle \\emph{"+modeles[j].nom+"}}  \n \n"))
                ana = AnalyseCarriere(c)
                
                #f.write(dec("\\paragraph{Différents départs à la retraite (pension, taux de remplacement), et ratios Revenu/SMIC pendant la retraite (à 70, 75, 80, 85, 90 ans)} \n\n"))
                f.write("{ \\scriptsize \\begin{center} \n")
                ana.affiche_pension_macron(True, f)
                f.write("\\end{center} } \n")

                fic = "fig/%s_%d_%d_%s_retraite.pdf"%(c.id_metier, c.annee_debut-c.age_debut, c.age_debut, c.m.id_modele)
                if not just_tex:
                    # Affichage des graphiques synthétiques
                    print(fic)
                    ax = fig.add_subplot(1,len(modeles),j+1)
                    lc = [carrieres[i][a][h][j] for h in range(len(carrieres[i][a]))]
                    AnalyseCarriere.plot_evolution_carriere_corr(ax, c.m.smic, g, lc, lc[-1].annee_debut + lc[-1].age_mort-lc[-1].age_debut, "Revenu/SMIC", dec(modeles[j].nom), 1, 1)

            if not just_tex:
                plt.savefig("./tex/"+fic)
                plt.close('all')
            f.write("\n \\begin{center}\\includegraphics[width=0.9\\textwidth]{%s}\\end{center} \\label{%s} \n\n"%(fic,fic))
            f.write("\\newpage \n \n")                 

            # Affichage détaillé
            for j in range(len(carrieres[i][a][g])): # modèles
                
                c = carrieres[i][a][g][j]
                f.write(dec("\\paragraph{Revenus et points pour le modèle \emph{"+modeles[j].nom+"}} \n \n"))
                ana = AnalyseCarriere(c)
                
                #f.write(dec("\\subparagraph{Evolution de la rémunération et des points retraites au cours de la carrière} \n \n"))
                f.write("{ \\scriptsize \\begin{center} \n")
                ana.affiche_carriere(True, f)
                f.write("\\end{center} } \n")
                f.write("\\newpage \n \n")
            

f.close()


