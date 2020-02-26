#!/usr/bin/python
# coding:utf-8

import sys
import codecs
from SimulateurCarriere import *
from AnalyseCarriere import *
from tools import *
import matplotlib.pyplot as plt


####################################################
# Partie principale
####################################################


########################
# Modèles de projection

debut, fin = 1980, 2130

modeles = [ ModeleGouv(debut,fin,1.3,True), ModeleGouv(debut,fin,1.3,False) ] #, ModeleDestinie(debut,fin)]
mod_titres = [ 'Reproduction des simulations du gouvernement', 'Simulations corrigées (âge pivot glissant)', 'Simulations du modèle Destinie2' ]

##############
# Générations

generations = [1975,1980,1990,2003]

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
#               ("BIATSS",0.1,22),
               ("MCF",0.034,28),
               ("CR",0.034,28),
               ("PR",0.071,28), ("DR",0.071,28),
               ("Magistrat",0.547,22)  ]

# cas_public = [("Magistrat",0.52,22)]


# dans le privé

cas_prive = [ ("SMPT","Salarié privé au salaire moyen durant toute sa carrière",22)#,
#              ("SMIC","Salarié privé au SMIC",22,)
]


#############################################
# génération des simulations et des pensions

carrieres = []
variation_age=4

# public

for (ide,p,age) in cas_public:

    # génération de la grille
    
    fic="grille_%s.pdf"%(ide)
    c=CarrierePublic(modeles[0], age, 1980, ide, p)
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
            if an<=2030: # après c'est trop loin
                l_mod = []
                for j in range(len(modeles)):
                    l_mod.append( CarrierePublic(modeles[j], a, an, ide, p) )
                l_gen.append(l_mod)
        l_age.append(l_gen)
    carrieres.append(l_age)

        
# privé

for (id_metier,metier,age) in cas_prive:

    ages=range(age,age+variation_age) # pour avoir éventuellement la variabilité par rapport à l'âge de départ

    l_age = []
    for a in ages:
        l_gen = []
        for gn in generations:
            an = gn + a  # année de début
            if an<=2030: # après c'est trop loin
                l_mod = []
                for j in range(len(modeles)):
                    l_mod.append( CarrierePrive(modeles[j], a, an, id_metier, metier) )
                l_gen.append(l_mod)
        l_age.append(l_gen)
    carrieres.append(l_age)



    
###########################################
#### Génération du corps du fichier LateX

f = codecs.open("tex/corps.tex", "w", "utf-8")

### Génération de la comparaison des modèles

fig=plt.figure(figsize=(18,12))
AnalyseModele.plot_modeles( modeles, [1980,2090] )
fic="fig/comparaison_modeles.pdf"
print(fic)
plt.savefig("./tex/"+fic)
plt.close('all')
f.write("\n \\begin{center}\\includegraphics[width=1\\textwidth]{%s}\\end{center} \n\n"%(fic))
f.write("\\newpage \n \n")  


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

            fig = plt.figure(figsize=(16,6),dpi=72)

            # Affichage détaillé
            for j in [0]:#range(len(carrieres[i][a][g])): # modèles
                
                c = carrieres[i][a][g][j]
                #f.write(dec("\\paragraph{"+mod_titres[j]+" (carrière détaillée)}  \n \n"))
                ana = AnalyseCarriere(c)
                
                #f.write(dec("\\subparagraph{Evolution de la rémunération et des points retraites au cours de la carrière} \n \n"))
                f.write("{ \\scriptsize \\begin{center} \n")
                ana.affiche_carriere(True, f)
                f.write("\\end{center} } \n")
                f.write("\\newpage \n \n")

            # Affichage synthétique
            for j in range(len(carrieres[i][a][g])): # modèles

                c = carrieres[i][a][g][j]
                f.write(dec("\\paragraph{"+mod_titres[j]+"}  \n \n"))
                ana = AnalyseCarriere(c)
                
                #f.write(dec("\\paragraph{Différents départs à la retraite (pension, taux de remplacement), et ratios Revenu/SMIC pendant la retraite (à 70, 75, 80, 85, 90 ans)} \n\n"))
                f.write("{ \\scriptsize \\begin{center} \n")
                ana.affiche_pension_macron(True, f)
                f.write("\\end{center} } \n")
                    
                # Affichage des graphiques synthétiques
                fic = "fig/%s_%d_%d_%s_retraite.pdf"%(c.id_metier, c.annee_debut-c.age_debut, c.age_debut, str(c.m.trucage))
                print(fic)
                
                ax = fig.add_subplot(1,2,j+1)
                lc = [carrieres[i][a][h][j] for h in range(len(carrieres[i][a]))]
                AnalyseCarriere.plot_evolution_carriere_corr(ax, c.m.smic, g, lc, lc[-1].annee_debut + lc[-1].age_mort-lc[-1].age_debut, "Revenu/SMIC", dec(mod_titres[j]), 1, 1)

            plt.savefig("./tex/"+fic)
            plt.close('all')
            f.write("\n \\begin{center}\\includegraphics[width=1\\textwidth]{%s}\\end{center} \n\n"%(fic))
            f.write("\\newpage \n \n")                 
                

f.close()


