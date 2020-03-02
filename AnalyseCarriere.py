#!/usr/bin/python
# -*- coding: utf-8 -*-

#################################################################################
### Simulateur micro de carrière (salaire et retraite à points), Partie Analyse
#################################################################################

# Remarque: convert doit être installé pour générer les gif

import sys
from tools import *
import matplotlib.pyplot as plt
import SimulateurCarriere as sim
import math



class AnalyseCarriere:

    def __init__(self,c):
        
        self.c = c  


    # affichage de tableaux

    def affiche_pension_macron(self, parts_enfant=0, tex=False, f=sys.stdout):
        
        c = self.c
        m = c.m

        eurcst="("+euroconst(c.m,tex)+")"
        l = [ [ "Retraite en", "Âge", "\\%(43ans)", "Âge pivot",  "Décote/Surcote", "Retraite "+eurcst, "Tx Rempl(\\%)", "SMIC "+eurcst, "Retraite/SMIC", "R70/SMIC", "R75/SMIC", "R80/SMIC", "R85/SMIC", "R90/SMIC" ] ]

        i=0
        for (a,d,p,t,r) in c.pension_macron[parts_enfant]:
            an = c.annee_debut+a-c.age_debut
            ap = int(m.age_pivot[ an - m.debut])
            x=[ str(an),
                str(a),
                "%.2f"%(r*100)+"\\%",
                "%d ans %d mois"%(ap, round((m.age_pivot[ an - m.debut]-ap)*12)),
                "%.2f"%(d*100)+"\\%",
                "%.2f"%(p/12/m.corr_prix_annee_ref[ an - m.debut]),
                "%.2f"%(t*100),
                "%.2f"%(m.smic[ an - m.debut ]/m.corr_prix_annee_ref[ an - m.debut]/12),
                seuil_tex(p/m.smic[ an - m.debut ], 1.0)       
            ]
            for j in range(sim.Carriere.age_mort+1 - a):
                if a+j in [70,75,80,85,90]:
                    an = c.annee_debut + a - c.age_debut + j
                    p = c.revenus_retraite_macron[parts_enfant][i][j]
                    x.append( seuil_tex(p/m.smic[ an - m.debut ], 1.0) )
            l.append(x)
            i=i+1

        print_table(l, f, tex, "{|c|c||c|c|c||c|c||c|c||c|c|c|c|c|}",[6, 8, 9, 10, 11, 12, 13])
                        

    def affiche_carriere(self, tex=False, f=sys.stdout):

        if self.c.public:
            self.affiche_carriere_public(tex, f)
        else:
            self.affiche_carriere_prive(tex, f)


    def affiche_carriere_public(self, tex=False, f=sys.stdout):

        c = self.c
        
        eurcst="("+euroconst(c.m,tex)+")"
        l = [ [ "Année", "Âge", "Quot(\\%)", "Ind Maj", "Pt Ind"+eurcst, "Rev HP"+eurcst, "Tx Primes","GIPA"+eurcst,"Revenu"+eurcst,"SMIC"+eurcst,"Rev/SMIC","Pts annuels","Cumul Pts","Achat Pt"+eurcst,"Serv. Pt"+eurcst ] ]
        
        for i in range(c.age_max - c.age_debut + 1):

            an = c.annee_debut+i
            m = c.m
            sal_cst = c.sal[i] / m.corr_prix_annee_ref[ an - m.debut]  

            l.append( [ str(an),
                        str(c.age_debut+i),
                        "%d"%(c.quot[i]*100),
                        "%.1f"%c.indm[i],
                        "%.2f"%(m.indfp[ an - m.debut ]/12/m.corr_prix_annee_ref[ an - m.debut]),
                        "%.2f"%(c.sal_hp[i]/12/m.corr_prix_annee_ref[ an - m.debut]),
                        "%.2f"%(c.prime[i]*100),
                        "%.2f"%(c.gipa[i]/12/m.corr_prix_annee_ref[ an - m.debut]),
                        "%.2f"%(sal_cst/12),
                        "%.2f"%(m.smic[ an - m.debut ]/m.corr_prix_annee_ref[ an - m.debut]/12),
                        "%.2f"%(c.sal[i] / m.smic[ an - m.debut ]),
                        "%.2f"%c.pts[i],
                        "%.2f"%c.cumul_pts[i],
                        "%.2f"%(m.achat_pt[ an - m.debut]/m.corr_prix_annee_ref[ an - m.debut]),
                        "%.2f"%(m.vente_pt[ an - m.debut]/m.corr_prix_annee_ref[ an - m.debut])
            ] )

        print_table(l, f, tex, "{|c|c||c|c|c|c|c|c|c||c|c||c|c|c|c|}",[10])
        

    def affiche_carriere_prive(self, tex=False, f=sys.stdout):

        c = self.c
        m = c.m   

        l=[]
            
        eurcst="("+euroconst(c.m,tex)+")"
        l.append( [ "Année","Âge", "Quot(\\%)", "Revenu "+eurcst,"SMIC "+eurcst,"Rev/SMIC","Cumul Pts","Achat Pt"+eurcst,"Serv. Pt"+eurcst ] )

        for i in range(1, sim.Carriere.age_max - c.age_debut + 1):
            an = c.annee_debut+i
            l.append([ "%d"%an,
                       "%d ans"%(c.age_debut+i),
                       "%d"%(c.quot[i]*100),
                       "%.2f"%(c.sal[i]/12/m.prix[ an - m.debut ]*m.prix[ c.m.annee_ref - m.debut]),
                       "%.2f"%(m.smic[ an - m.debut ]/m.corr_prix_annee_ref[ an - m.debut]/12),
                       "%.2f"%(c.sal[i] / m.smic[ an - m.debut ]),
                       "%.2f"%(c.cumul_pts[i]),"%.2f"%(m.achat_pt[an - m.debut]),
                       "%.2f"%(m.vente_pt[ an - m.debut]) ])

        print_table(l, f, tex, "{|c|c||c|c|c|c||c|c|c|}",[5])


    # affichage de graphiques
    
        
    def affiche_grille(self, tex=False, f=sys.stdout):

        c=self.c
        
        if not c.public:
            raise Exception("La fonction affiche_grille_tex() ne doit pas être appelée pour une carrière privée!")

        l = [ ["Indice majoré","Durée (années)"] ]
        g = sim.CarrierePublic.grilles[c.n_metier[0]][1]
        for i,d in g:
            if d!=100:
                l.append([ "%d"%i, "%.2f"%d ])
            else:
                l.append([ "%d"%i, "" ])
            
        print_table(l,f,tex,"{|c|c|}")

        

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


    def plot_points(self, ax, ls="-", label=""):

        c = self.c
        m = c.m

        plt.plot( range( c.annee_debut, c.annee_debut + sim.Carriere.age_max+1 - c.age_debut)  ,  [ c.pts[i] for i in range(len(c.sal)) ], linestyle=ls, label=label )
        plt.ylabel(dec("Nombre de points acquis"))

        
    def plot_carriere_corr(self, enfant, ax, corr, div=12, plot_retraite=0, couleur=(0.8,0.8,0.8), label="" ):

        c = self.c
        m = c.m
        
        # plot_retraite: 0:rien, 1:retraite macron, 2:retraite actuelle

        plt.plot( range( c.annee_debut, c.annee_debut + sim.Carriere.age_max+1 - c.age_debut)  ,  [ c.sal[i] / div / corr[c.annee_debut + i - m.debut] for i in range(len(c.sal)) ], color=couleur, label=label  )
        if plot_retraite==1:
            for i in range(0,len(c.pension_macron[enfant]),1):
                (age,_,pens,t,_) = c.pension_macron[enfant][i]
                lx = [ c.annee_debut + a - c.age_debut   for a in range(age, sim.Carriere.age_mort+1) ]  # années de retraite
                ly = [ c.revenus_retraite_macron[enfant][i][j] / div / corr[ lx[j] - m.debut ]   for j in range(sim.Carriere.age_mort+1 - age) ]  # revenus de retraite

                lx = [ lx[0] ] + lx
                ly = [ pens/t / div / corr[ lx[0] - m.debut ] ] + ly

                plt.plot( lx, ly, color=couleur, linestyle="dashed", label=dec("Retraites") )

                p1 = ax.transData.transform_point((lx[1], ly[1]))
                p2 = ax.transData.transform_point((lx[2], ly[2]))
                dy = (p2[1] - p1[1])
                dx = (p2[0] - p1[0])
                rotn = math.degrees(math.atan2(dy, dx))
                plt.text( p1[0]+1,p1[1]+1, dec( "%d ans, %.2f%%"%(age,t*100)), transform=None, rotation=rotn, fontsize=8)

    @classmethod
    def plot_evolution_carriere_corr(cls, enf, ax, corr, focus, carrieres, a2, labely, titre, div, plot_retraite=0):

        c = carrieres[0]
        m = c.m
        annee0 = c.annee_debut

        # Courbes du SMIC, du SMPT et de 85%MIC
        rg = range( annee0, a2 )
        plt.plot(rg, [m.smic[i-m.debut]/div/corr[i-m.debut] for i in rg], label="SMIC", color="red")
        plt.plot(rg, [m.smpt[i-m.debut]/div/corr[i-m.debut] for i in rg], label="Salaire moyen", color="blue")
        plt.plot(rg, [0.85*m.smic[i-m.debut]/div/corr[i-m.debut] for i in rg], label="85% SMIC", color="grey", linestyle=":")
        
        # Evolution de carrière en fonction de l'année de départ
        for i in range(len(carrieres)):
            if i!=focus:
                AnalyseCarriere(carrieres[i]).plot_carriere_corr(enf, ax, corr, div)
        AnalyseCarriere(carrieres[focus]).plot_carriere_corr(enf, ax, corr, div, plot_retraite, "green", labely)

        # legendes
        y1,y2 = ax.get_ylim()
        y = y1+(y2-y1)*0.98
        plt.text(m.annee_ref+2, y, dec("Projection "+m.nom), ha='left', va='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5), fontsize=8)
        if annee0 < m.annee_ref:
            plt.text(m.annee_ref-2, y, dec("Données réelles"), ha='right', va='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5), fontsize=8)
        
        plt.axvline(m.annee_ref, color="grey", linestyle="dashed")
        plt.title(titre)
            
        plt.ylabel(labely)
        plt.legend(loc="lower left")

    

class AnalyseModele():

    def __init__(self,m):

        self.m = m


    def affiche_modele(self, tex=False, f=sys.stdout, deb=2000, fin=2070):

        m = self.m
        
        eurcst="("+euroconst(m,tex)+")"

        l = [ [ "Année",
                "Indice Prix (réf=%d)"%(m.annee_ref),
                "Inflation (\\%)",
                "Croissance (\\%)",
                "SMIC"+eurcst,
                "Variation SMIC (\\%)",
                "SMPT"+eurcst,
                "Variation SMPT (\\%)",
                "Indice FP"+eurcst,
                "Variation Indice FP (\\%)",
                "Achat Pt"+eurcst,
                "Serv. Pt"+eurcst,
                "Variation Pt (\\%)",
                "Âge pivot"
        ] ]

        for a in range(deb,fin+1):
            i = a-m.debut
            l.append( [str(a),
                       "%.2f"%(m.corr_prix_annee_ref[i]),
                       "%.2f"%(m.inflation[i]),
                       "%.2f"%(m.croissance[i]),
                       "%.2f"%(m.smic[i]/12/m.corr_prix_annee_ref[i]),
                       "%.2f"%( ( (m.smic[i]/m.corr_prix_annee_ref[i])/(m.smic[i-1]/m.corr_prix_annee_ref[i-1])  -1.0 ) *100),
                       "%.2f"%(m.smpt[i]/12/m.corr_prix_annee_ref[i]),
                       "%.2f"%( ( (m.smpt[i]/m.corr_prix_annee_ref[i])/(m.smpt[i-1]/m.corr_prix_annee_ref[i-1])  -1.0 ) *100),
                       "%.2f"%(m.indfp[i]/12/m.corr_prix_annee_ref[i]),
                       "%.2f"%( ( (m.indfp[i]/m.corr_prix_annee_ref[i])/(m.indfp[i-1]/m.corr_prix_annee_ref[i-1])  -1.0 ) *100),
                       "%.2f"%(m.achat_pt[i]/m.corr_prix_annee_ref[i]),
                       "%.2f"%( (m.vente_pt[i]/m.corr_prix_annee_ref[i]) ),
                       "%.2f"%( ( (m.vente_pt[i]/m.corr_prix_annee_ref[i]) / (m.vente_pt[i-1]/m.corr_prix_annee_ref[i-1]) -1.0 ) *100),
                       "%.2f"%(m.age_pivot[i])
                       ] )
            if a==deb:
                l[-1][5]="-"
                l[-1][7]="-"
                l[-1][9]="-"
                l[-1][12]="-"

        print_table(l, f, tex, "{|c||c|c|c||c|c||c|c||c|c||c|c|c||c|}", [0])
            
    # affichage de graphiques
    
    def plot_modele(self, f, tit="", r=[], ls=1):

        m=self.m
        
        if r==[]:
            r=[m.debut, m.fin]
        r2 = [ r[0]-m.debut, r[1]+1-m.debut ]
        r  = range(r[0],r[1]+1)
        plt.plot(r,f[r2[0]:r2[1]], label=dec(m.nom), linestyle=ls)

        plt.axvline(m.annee_ref, color="grey", linestyle="dashed")
        plt.title(tit)


    @classmethod
    def plot_modeles(cls,lm,r):
        
        for i in range(9):
            eurcst=" ("+euroconst(lm[0],False)+")"
            label = [ "Indice Prix (réf=%d)"%(lm[0].annee_ref),
                      "Inflation (%)",
                      "Croissance (%)",
                      "SMIC"+eurcst,
                      "SMPT"+eurcst,
                      "Indice FP"+eurcst,
                      "Achat Pt"+eurcst,
                      "Serv. Pt"+eurcst,
                      "Âge pivot" ][i]
            
            ax=plt.subplot(3,3,i+1)
            k=0
            for m in lm:                
                
                n = m.fin-m.debut
                var = [ [ m.corr_prix_annee_ref[j] for j in range(n) ],
                        [ m.inflation[j] for j in range(n) ],
                        [ m.croissance[j] for j in range(n) ],
                        [ m.smic[j]/12/m.corr_prix_annee_ref[j] for j in range(n) ],
                        [ m.smpt[j]/12/m.corr_prix_annee_ref[j] for j in range(n) ],
                        [ m.indfp[j]/12/m.corr_prix_annee_ref[j] for j in range(n) ],
                        [ m.achat_pt[j]/m.corr_prix_annee_ref[j] for j in range(n) ],
                        [ m.vente_pt[j]/m.corr_prix_annee_ref[j] for j in range(n) ],
                        [ m.age_pivot[j] for j in range(n) ] ][i]
                a=AnalyseModele(m)
                a.plot_modele(var, dec(label), r, ['-','--',':'][k] )
                k=k+1
            #plt.legend(loc='upper right')
        handles, labels = ax.get_legend_handles_labels()
        plt.figlegend(handles, labels, borderaxespad=0.0, loc='upper center')
        #plt.tight_layout()
