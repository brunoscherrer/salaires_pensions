#!/usr/bin/python
# coding:utf-8

#################################################################################
### Simulateur micro de carrière (salaire et retraite à points), Partie Analyse
#################################################################################

# Remarque: convert doit être installé pour générer les gif

import sys
from tools import *
import matplotlib.pyplot as plt
import prettytable as pt
import SimulateurCarriere as sim
import math

class AnalyseCarriere:

    def __init__(self,c):
        
        self.c = c  

        
    def affiche_carriere(self, style="text", f=None): # flux: pour l'écriture dans un fichier (tex)

        c = self.c
        m = c.m   

        if style == "tex":

            pass

        else: # default style="text"

            x = pt.PrettyTable()
            
            print(c.nom_metier)
            x.field_names = [ "Annee","Age","Salaire ms","Pts","Ach.Pt","Vte.Pt" ]

            for i in range(sim.Carriere.age_max - c.age_debut + 1):
                an = c.annee_debut+i
                x.add_row( [ "%d"%an, "%d ans"%(c.age_debut+i),"%.2f"%(c.sal[i]/12/m.prix[ an - m.debut ]*m.prix[ c.m.annee_ref - m.debut]),"%.2f"%(c.nb_pts[i]),"%.2f"%(m.achat_pt[an - m.debut]),"%.2f"%(m.vente_pt[ an - m.debut]) ] )

            print(x)
            
            
    def affiche_pension_macron(self, style="text", f=None):

        c = self.c
        m = c.m   
        
        if style == "tex":

            #f.write("\\newpage \n\n")
            #f.write(dec("\\paragraph{Différents départs à la retraite (pension, taux de remplacement), et ratios Revenu/SMIC pendant la retraite (à 70, 75, 80, 85, 90 ans)} ~\\\\ \n\n"))
            f.write("{ \\scriptsize \\begin{center} \\begin{tabular}{|c|c||c|c||c|c||c||c|c|c|c|c|c|} \n")
            f.write("\\hline \n")
            f.write(dec("Retraite en & Âge & Âge Pivot &  décote/surcote & Retraite(\\euro{}cst) & Taux remplacement (\\%) & SMIC(\\euro{}cst) & Retraite/SMIC & Rev70/SMIC & Rev75/SMIC & Rev80/SMIC & Rev85/SMIC & Rev90/SMIC \\\\ \n"))
            f.write("\\hline \\hline \n")

            i=0
            for (a,d,p,t) in c.pension_macron:
                an = c.annee_debut+a-c.age_debut
                ap = int(m.age_pivot[ an - m.debut])
                
                l = [ str(an),
                      str(a),
                      "%d ans %d mois"%(ap, round((m.age_pivot[ an - m.debut]-ap)*12)),
                      "%.2f"%(d*100)+"\\%",
                      #"%.2f"%(p/12),
                      "%.2f"%(p/12/m.corr_prix_annee_ref[ an - m.debut]),
                      "%.2f"%(t*100),
                      "%.2f"%(m.smic[ an - m.debut ]/m.corr_prix_annee_ref[ an - m.debut]/12),
                      seuil(p/m.smic[ an - m.debut ], 1.0)       
                ]
                for j in range(sim.Carriere.age_mort+1 - a):
                    if a+j in [70,75,80,85,90]:
                        an = c.annee_debut+a-c.age_debut + j
                        p = c.revenus_retraite_macron[i][j]
                        l.append( seuil(p/m.smic[ an - m.debut ], 1.0) )
                
                f.write(tex_row(l))
                i=i+1
                        
                f.write("\\hline \n")
            f.write("\\end{tabular} \\end{center} } \n\n")

            fic = "fig/%s_%d_%d_%d_%s_retraite.pdf"%(c.id_metier, c.annee_debut-c.age_debut, c.age_debut, int(c.part_prime*100), str(c.m.trucage))
            print(fic)
            fig = plt.figure(figsize=(16,6),dpi=72)
            ax = fig.add_subplot(121)
            an=AnalyseCarriere(c)
            an.plot_evolution_carriere_corr(ax, c.m.prix, c.annee_debut, [c.annee_debut], "Euros constants (2019)", 12, 1)
            ax = fig.add_subplot(122)
            an.plot_evolution_carriere_corr(ax, c.m.smic, c.annee_debut, [c.annee_debut], "Ratio Revenu/SMIC", 1,1)
            plt.savefig("./tex/"+fic)

            f.write("\n \\begin{center}\\includegraphics[width=0.3\\textwidth]{%s}\\end{center} \n\n"%(fic))
            plt.close('all')
            
#            f.write("\\newpage {\\tiny \n\n")
#            f.write(dec("\\begin{multicols}{3} \n"))
#            i=0
#            for (a,_,_,_) in c.pension_macron:
#                an = c.annee_debut+a-c.age_debut
#                f.write(dec("\\vbox{ \\paragraph{Hypothèse d'un départ à %d ans (en %d)} ~\\\\ \n\n"%(a, an)))
#                f.write("{\\small \\centering \\begin{tabular}{|*{6}{c|}} \n")
#                f.write("\\hline \n")
#                f.write(dec("Année & Age & Revenu(\euro{}cst) & SMIC(\euro{}cst) &Rev/SMIC \\\\ \n"))
#                f.write("\\hline \n")
#                for j in range(carriere.age_mort+1 - a):
#                    an = c.annee_debut+a-c.age_debut + j
#                    p = c.revenus_retraite_macron[i][j]
#                    l = [ str(an),
#                          str(a+j),
#                          #"%.2f"%(p/12),
#                          "%.2f"%(p/12/m.corr_prix_annee_ref[ an - m.debut]),
#                          "%.2f"%(m.smic[ an - m.debut ]/12/m.corr_prix_annee_ref[ an - m.debut]),
#                          "{\\bf %.2f}"%(p/m.smic[ an - m.debut ]) ]
#                    f.write(tex_row(l))
#                f.write("\\hline \n")
#                f.write("\\end{tabular}}} \n\n")
#                i=i+1
#            f.write(dec("\\end{multicols} }"))
#
#            f.write("\\newpage \n\n")
            
            
        else: # default style="text"
        
            x = pt.PrettyTable()
            print("Retraite Macron (Synthèse départs)")
            x.field_names = ["Année", "Age", "AgePivot", "+/-cote", "Brut ms", "Brut ms EC", "Tx rempl.", "%/SMIC" ]
            for (a,d,p,t) in c.pension_macron:
                an = c.annee_debut+a-c.age_debut
                ap = int(m.age_pivot[ an - m.debut])
                x.add_row( [ an, a, "%d ans %d mois"%(ap, round((m.age_pivot[ an - m.debut]-ap)*12)), "%.2f%%"%(d*100), "%.2f"%(p/12), "%.2f"%(p/12/m.corr_prix_annee_ref[ an - m.debut]), "%.2f"%(t*100), "%.2f"%(p/m.smic[ an - m.debut ]) ])
            print(x)

            print("Retraite Macron (détaillée selon départ)")
            i=0
            for (a,_,_,_) in c.pension_macron:
                an = c.annee_debut+a-c.age_debut
                print("Départ à %d ans (en %d)"%(a, an))
                x = pt.PrettyTable()
                x.field_names = ["Année", "Age", "Brut ms", "Brut ms EC", "%/SMIC" ]
                for j in range(carriere.age_mort+1 - a):
                    an = c.annee_debut+a-c.age_debut + j
                    p = c.revenus_retraite_macron[i][j]
                    x.add_row( [ an, a+j, "%.2f"%(p/12), "%.2f"%(p/12/m.corr_prix_annee_ref[ an - m.debut]), "%.2f"%(p/m.smic[ an - m.debut ]) ] ) 
                #####
                print(x)
                i=i+1
            

    def affiche_carriere(self, style="text", f=sys.stdout):

        if self.c.public:
            self.affiche_carriere_public(style, f)
        else:
            self.affiche_carriere_prive(style, f)


    def affiche_carriere_public(self, style="text", f=None):

        c = self.c
        
        if style == "tex":

            #f.write(dec("\\paragraph{Synthèse de la carrière} \n\n"))
            #f.write("\\newpage")
            #f.write(dec("\\begin{table}[htb]\\centering\\caption{Synthèse de la carrière} \n"))
            f.write("{\\scriptsize \\begin{center} \\begin{tabular}{|c|c||c|c|c|c|c|c||c|c||c|c|c||} \n")
            f.write("\\hline \n")
            f.write(dec("Année & Âge & Ind Maj & Pt Ind(\\euro{}cst) &  Hors-Primes(\\euro{}cst) & Tx Primes & GIPA(\\euro{}cst) & Brut(\\euro{}cst) & SMIC(\\euro{}cst) & Rev/SMIC & Cumul Pts & Achat Pt(\\euro{}cst) & Vente Pt(\\euro{}cst)  \\\\ \n"))
            f.write("\\hline \\hline\n")

            for i in range(carriere.age_max - c.age_debut + 1):
                an = c.annee_debut+i
                m = c.m
                sal_cst = c.sal[i] / m.corr_prix_annee_ref[ an - m.debut]  

                l = [ str(an),
                      str(c.age_debut+i),
                      "%.1f"%c.indm[i],
                      #"%.2f"%m.indfp[ an - m.debut ],
                      "%.2f"%(m.indfp[ an - m.debut ]/12/m.corr_prix_annee_ref[ an - m.debut]),
                      #"%.2f"%c.sal_hp[i],
                      "%.2f"%(c.sal_hp[i]/12/m.corr_prix_annee_ref[ an - m.debut]),
                      "%.2f"%(c.prime[i]*100),
                      "%.2f"%(c.gipa[i]/12/m.corr_prix_annee_ref[ an - m.debut]),
                      #"%.2f"%c.sal[i],
                      #"%.2f"%sal_cst,
                      "%.2f"%(sal_cst/12),
                      "%.2f"%(m.smic[ an - m.debut ]/m.corr_prix_annee_ref[ an - m.debut]/12),
                      "{\\bf %.2f}"%(c.sal[i] / m.smic[ an - m.debut ]),
                      "%.2f"%c.nb_pts[i],
                      "%.2f"%(m.achat_pt[ an - m.debut]/m.corr_prix_annee_ref[ an - m.debut]),
                      "%.2f"%(m.vente_pt[ an - m.debut]/m.corr_prix_annee_ref[ an - m.debut])
                      #"%.2f"%m.prix[ an - m.debut ]
                ]
                f.write(tex_row(l))
                f.write("\\hline \n")

            f.write("\\end{tabular} \\end{center} } \n\n")
            #f.write("\\end{table}")
            
        else: # default style="text"
        
            print(c.nom_metier," - an=annuel, ms=mensuel, HP=Hors Prime, EC=euros constants",c.m.annee_ref)

            x = pt.PrettyTable()

            x.field_names = ["Année", "Age", "Ind. Maj", "Val Ind an", "VInd ms", "BrutHP an", "BrutHP ms", "TxPrime", "GIPA ms", "Brut an", "Brut an EC", "Brut ms EC", "%/SMIC", "Tot Pts", "AchPt", "VtePt","Prix" ]

            
            for i in range(sim.Carriere.age_max - c.age_debut + 1):
                an = c.annee_debut+i
                m = c.m
                sal_cst = c.sal[i] / m.corr_prix_annee_ref[ an - m.debut]  #m.prix[ an - m.debut ]*m.prix[ ANNEE_REF - m.debut]

                x.add_row( [ an,
                             c.age_debut+i,
                             "%.1f"%c.indm[i],
                             "%.2f"%m.indfp[ an - m.debut ],
                             "%.2f"%(m.indfp[ an - m.debut ]/12),
                             "%.2f"%c.sal_hp[i],
                             "%.2f"%(c.sal_hp[i]/12),
                             "%.2f"%(c.prime[i]*100),
                             "%.2f"%(c.gipa[i]/12),
                             "%.2f"%c.sal[i],
                             "%.2f"%sal_cst,
                             "%.2f"%(sal_cst/12),
                             "%.2f"%(c.sal[i] / m.smic[ an - m.debut ]),
                             "%.2f"%c.nb_pts[i],
                             "%.2f"%m.achat_pt[ an - m.debut],
                             "%.2f"%m.vente_pt[ an - m.debut],
                             "%.2f"%m.prix[ an - m.debut ]
                ] )

            print(x)
            

    def affiche_carriere_prive(self,style="text",f=sys.stdout):

        print("Warning: affiche_carriere_prive pas implémenté!")
        pass


    def plot_grille(self):

        c=self.c
        
        if not c.public:
            raise Exception("La fonction plot_grille() ne doit pas être appelée pour une carrière privée!")
        
        g = sim.CarrierePublic.grilles[c.n_metier[0]][1]
        x,y = 0, g[0][0]
        lx, ly = [x], [y]
    
        for i in range(1,len(g)):
            dx = g[i-1][1]
            lx.append(x+dx)
            ly.append(y)
            x = x+dx
            y = g[i][0]
            lx.append(x)
            ly.append(y)
        lx.append(45)
        ly.append(y)
        
        plt.plot(lx,ly)
        plt.xlabel(dec("Ancienneté"))
        plt.ylabel(dec("Indice majoré"))
        plt.title(dec("Grille indiciaire ("+c.nom_metier)+")",fontsize=11)
        

    def affiche_grille_tex(self,f):

        c=self.c
        
        if not c.public:
            raise Exception("La fonction affiche_grille_tex() ne doit pas être appelée pour une carrière privée!")
        
        f.write("\\begin{tabular}{|c|c|} \n")
        f.write(dec("\\hline \n Indice majoré & Durée (années) \\\\ \\hline \\hline"))
        g = sim.CarrierePublic.grilles[c.n_metier[0]][1]
        for i,d in g:
            if d!=100:
                f.write("%d & %.2f "%(i,d))
            else:
                f.write("%d & "%(i))
            f.write("\\\\ \\hline")
        f.write("\\end{tabular} \n\n")

        
    def plot_grille_prime(self):

        c=self.c
        
        if not c.public:
            raise Exception("La fonction plot_grille_prime() ne doit pas être appelée pour une carrière privée!")
        
        plt.figure(figsize=(11,4))

        plt.subplot(1,2,1)
        self.plot_grille()
        
        plt.subplot(1,2,2)
        plt.plot( [c.prime[i]*100 for i in range(len(c.prime))] )
        plt.xlabel(dec("Ancienneté"))
        plt.ylabel(dec("Pourcentage du salaire brut"))
        plt.title(dec("Prime ("+c.nom_metier)+")",fontsize=11)


    def plot_carriere_corr(self, ax, corr, div=12, plot_retraite=0, couleur=(0.8,0.8,0.8), label="" ):

        c=self.c
        m=c.m
        
        # plot_retraite: 0:rien, 1:retraite macron, 2:retraite actuelle

        plt.plot( range( c.annee_debut, c.annee_debut + sim.Carriere.age_max+1 - c.age_debut)  ,  [ c.sal[i] / div / corr[c.annee_debut + i - m.debut] for i in range(len(c.sal)) ], color=couleur, label=label  )

        if plot_retraite==1:
            for i in range(0,len(c.pension_macron),2):
                (age,_,pens,t) = c.pension_macron[i]
                lx = [ c.annee_debut + a - c.age_debut   for a in range(age, sim.Carriere.age_mort+1) ]  # années de retraite
                ly = [ c.revenus_retraite_macron[i][j] / div / corr[ lx[j] - m.debut ]   for j in range(sim.Carriere.age_mort+1 - age) ]  # revenus de retraite

                lx = [ lx[0] ] + lx
                ly = [ pens/t / div / corr[ lx[0] - m.debut ] ] + ly

                plt.plot( lx, ly, color=couleur, linestyle="dashed", label=dec("Retraites") )

                p1 = ax.transData.transform_point((lx[1], ly[1]))
                p2 = ax.transData.transform_point((lx[-1], ly[-1]))
                dy = (p2[1] - p1[1])
                dx = (p2[0] - p1[0])
                rotn = math.degrees(math.atan2(dy, dx))
                plt.text( p1[0]+1,p1[1]+1, dec( "%d ans, %.2f%%"%(age,t*100)), transform=None, rotation=rotn, fontsize=8)

    @classmethod
    def plot_evolution_carriere_corr(cls, ax, corr, focus, carrieres, a2, labely, div, plot_retraite=0, posproj=0.95):
        
        m=carrieres[0].m
        annee0 = carrieres[0].annee_debut

        # Courbes du SMIC et du SMPT
        rg = range( annee0, a2 )
        plt.plot(rg, [m.smic[i-m.debut]/div/corr[i-m.debut] for i in rg], label="SMIC", color="red")
        plt.plot(rg, [m.smpt[i-m.debut]/div/corr[i-m.debut] for i in rg], label="Salaire moyen", color="blue")
            
        # Evolution de carrière en fonction de l'année de départ
        for i in range(len(carrieres)):
            if i!=focus:
                AnalyseCarriere(carrieres[i]).plot_carriere_corr(ax, corr, div)
        AnalyseCarriere(carrieres[focus]).plot_carriere_corr(ax, corr, div, plot_retraite, "green", labely)

        # legendes
        y1,y2 = ax.get_ylim()
        y = y1+(y2-y1)*0.98
        plt.text(m.annee_ref+2, y, dec("Projection "+m.nom), ha='left', va='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5), fontsize=8)
        if annee0 < m.annee_ref:
            plt.text(m.annee_ref-2, y, dec("Données réelles"), ha='right', va='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5), fontsize=8)
        
        plt.axvline(m.annee_ref, color="grey", linestyle="dashed")
        plt.title( dec(carrieres[focus].nom_metier+" débutant en %d"%carrieres[focus].annee_debut) )
        
        plt.ylabel(labely)
        plt.legend(loc="upper right")

    

class AnalyseModele():

    def __init__(self,m):

        self.m = m
        
    
    def plot_modele(self, f=sys.stdout, tit="", r=[]):

        m=self.m
        
        if r==[]:
            r=[m.debut, m.fin]
        r2 = [ r[0]-m.debut, r[1]+1-m.debut ]
        r  = range(r[0],r[1]+1)
        plt.plot(r,f[r2[0]:r2[1]], label=dec(m.nom))

        plt.axvline(m.annee_ref, color="grey", linestyle="dashed")
        plt.title(tit)


    @classmethod
    def plot_modeles(cls,lm,r):

        for i in range(6):
            label = ["Prix (Inflation intégrée)","SMIC annuel","SMPT annuel","Valeur du point d'indice de la Fonction Publique","Valeur d'achat du point Macron","Valeur de vente du point Macron"][i]
            plt.subplot(3,2,i+1)
            for m in lm:
                var = [m.prix, m.smic, m.smpt, m.indfp, m.achat_pt, m.vente_pt][i]
                a=AnalyseModele(m)
                a.plot_modele(var, dec(label),r)
            plt.legend(loc='upper right')
        plt.tight_layout()
