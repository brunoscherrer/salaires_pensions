#!/usr/bin/python
# coding:utf-8

import sys
import codecs
from SimulateurCarriere import *
from AnalyseCarriere import *
from tools import *
import matplotlib.pyplot as plt

global m, cas  # pour l'instant, un peu goret

dir_images = "./tex/fig/"


####################################################
# Partie principale
####################################################



# Modèles de projection

debut, fin = 1980, 2130
m1 = ModeleGouv(debut,fin,1.3,True)
m2 = ModeleGouv(debut,fin,1.3,False)

# Carrières considérées: id, prime(2019), age de début

cas = [ ("Infirmier",0.299, 22), ("AideSoignant",0.242, 22), ("TechHosp",0.27, 22), ("AdjTech", 0.18, 22), ("Redacteur",0.281, 22), ("SecretaireAdmin",0.27, 22), ("ATSEM",0.16, 22), ("ProfEcoles",0.081, 22), ("ProfCertifie",0.096, 22), ("ProfAgrege",0.09, 22), ("BIATSS",0.1,22),
        ("MCF",0.034,28), ("CR",0.034,28), ("PR",0.071,28), ("DR",0.071,28),
        ("Magistrat",0.52,22)  ]
#cas = [ ("Infirmier",0.299, 22) ]
#cas = [("CR",0.034,28)]
#cas = [("ProfEcoles",0.081, 22)]
cas = [("Magistrat",0.52,22)]

generations = range(1970,2011,1)  # année de début de carrière
generations = [1975,1980,1990,2003]

f = codecs.open("tex/corps.tex", "w", "utf-8")

for (ide,p,age) in cas:

    ages = range(age, age+4)
    ages = [age]
    
    i,j = CarrierePublic.numero_metier_public(ide)
    nom = CarrierePublic.grilles[i][0][j][1]

    print nom
    
    f.write(dec("\\chapter{%s} \n\n"%nom))
    
    fic="grille_%s_%d.pdf"%( ide, int(p*100) )
    c=CarrierePublic(m1, age, 1980, ide, p)
    AnalyseCarriere(c).plot_grille()
    print fic
    plt.savefig("./tex/fig/"+fic)
    plt.close('all')

    f.write("\\begin{minipage}{0.55\\linewidth}\\includegraphics[width=0.7\\textwidth]{%s}\\end{minipage} \n"%("fig/"+fic))
    f.write("\\begin{minipage}{0.3\\linewidth} \n \\begin{center} \n\n")
    AnalyseCarriere(c).affiche_grille(True, f)
    f.write("\\end{center} \n \\end{minipage} \n\n")
    
    f.write(dec("\n \\addto{\\captionsenglish}{ \\renewcommand{\\mtctitle}{}} \\setcounter{minitocdepth}{2} \n \\minitoc \\newpage \n\n"))

    for a in ages:

        f.write(dec("\\section{Début de carrière à %d ans} \n\n"%(a)))

        #f.write(" \n \\setcounter{minitocdepth}{2} \minitoc \\newpage \n\n")
        
        for gn in generations:

            an = gn + a

            if an<=2030: # après c'est trop loin

                f.write(dec("\\subsection{Génération %d (début en %d)} \n\n"%(gn, an)))
                
                for m,titre in [ (m1,"Simulations du gouvernement (avec trucage de l'âge pivot et de la valeur du point)"), (m2,"Simulations du gouvernement (avec trucage de l'âge pivot mais pas de la valeur du point)") ]:

                    f.write(dec("\\paragraph{"+titre+"}  ~\\\\ \n \n"))
                    
                    c = CarrierePublic(m, a, an, ide, p)
                    ana = AnalyseCarriere(c)
                
                    f.write(dec("\\subparagraph{Evolution de la rémunération et des points retraites au cours de la carrière} \n \n"))
                    f.write("{ \\scriptsize \\begin{center} \n")
                    ana.affiche_carriere(True, f)
                    f.write("\\end{center} } \n")
                    
                    # Affichage de la pension
                    f.write("\\newpage \n \n")
                    f.write(dec("\\paragraph{Différents départs à la retraite (pension, taux de remplacement), et ratios Revenu/SMIC pendant la retraite (à 70, 75, 80, 85, 90 ans)} \n\n"))
                    f.write("{ \\scriptsize \\begin{center} \n")
                    ana.affiche_pension_macron(True, f)
                    f.write("\\end{center} } \n")
                    
                    # Affichage des graphiques synthétiques
                    fic = "fig/%s_%d_%d_%d_%s_retraite.pdf"%(c.id_metier, c.annee_debut-c.age_debut, c.age_debut, int(c.part_prime*100), str(c.m.trucage))
                    print(fic)
                    fig = plt.figure(figsize=(16,6),dpi=72)
                    ax = fig.add_subplot(121)
                    AnalyseCarriere.plot_evolution_carriere_corr(ax, c.m.prix, 0, [c], c.annee_debut+c.age_mort-c.age_debut, "Revenu \texteuro "+str(c.m.annee_ref), 12, 1)
                    ax = fig.add_subplot(122)
                    AnalyseCarriere.plot_evolution_carriere_corr(ax, c.m.smic, 0, [c], c.annee_debut+c.age_mort-c.age_debut, "Revenu/SMIC", 1,1)
                    plt.savefig("./tex/"+fic)
                    plt.close('all')
                    f.write("\n \\begin{center}\\includegraphics[width=1.0\\textwidth]{%s}\\end{center} \n\n"%(fic))
                    f.write("\\newpage \n \n")                 
                

f.close()


