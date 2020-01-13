#!/usr/bin/python
# coding:utf-8

from pylab import *
import os


def shell_command(com):
    print com
    os.system(com)


ANNEE_REF = 2019 # année courante


def dec(s):
    return s.decode("utf-8")

### Simulateur micro des pensions (ancien et nouveau système)


# fonction pour charger les données à partir du modèle Destinie2 (1,3% croissance)

def charge_donnees(deb,fin): # debut et fin compris

    with open("./destinie2_1.3.csv","r") as f:

        n=fin+1-deb
        prix,smic,indfp,smpt = [0.0]*n, [0.0]*n, [0.0]*n, [0.0]*n
        
        f.readline() # on vire la première ligne

        while True:
            l = f.readline()
            if not l:
                break
            l = l.split("|")
            a = int( l[1] ) # annee
            if a > fin:
                break
            if a >= deb: # si l'année est bien dans la plage
                b = a-deb
                prix[b] = float( l[2].replace(',', '.') ) 
                smic[b] = float( l[4].replace(',', '.') )
                smpt[b] = float( l[6].replace(',', '.') )
                indfp[b] = float( l[5].replace(',', '.') )
                
    return prix,smic,smpt,indfp



###################################################################        
# classes pour décrire le contexte macro passé et futur

class modele_abs(object):  
    
    def __init__(self, debut, debut_proj, fin):

        self.age_legal = 62
        self.age_pivot = 65
        
        self.debut = debut
        self.debut_proj = debut_proj
        self.fin = fin

        # initialisation
        n = fin+1-debut
        self.prix = [0.0]*n
        self.smic = [0.0]*n
        self.smpt = [0.0]*n
        self.indfp = [0.0]*n
        
        # charge l'historique des données passées (entre debut et debut_proj)
        n = debut_proj+1-debut
        self.prix[0:n], self.smic[0:n], self.smpt[0:n], self.indfp[0:n] = charge_donnees(self.debut, self.debut_proj)

        
    def post_init(self):

        a=2022
        
        # calcul du point par rapport au valeurs 2020 (indexation sur inflation+smpt)
        n = self.fin+1-self.debut
        self.achat_pt = [0.0]*n
        self.vente_pt = [0.0]*n
        self.corr_part_prime = [0.0]*n
        self.corr_prix_annee_ref = [0.0]*n
        
        for i in xrange(self.debut,self.fin+1):

            tmp = self.smpt[i-self.debut] / self.smpt[a-self.debut] # indexation du point sur le salaire moyen
            self.achat_pt[i-self.debut] = 10.0 / 0.9 / 0.2812 * tmp  
            self.vente_pt[i-self.debut] = 0.55 * tmp

            self.corr_part_prime[i-self.debut] = 0.0023*(i-ANNEE_REF)        
            self.corr_prix_annee_ref[i-self.debut] = self.prix[ i - self.debut ] / self.prix[ ANNEE_REF-self.debut ]
            
# classe pour décrire le contexte macro envisagé par le gouvernement

class modele_gouv(modele_abs):
    
    def __init__(self, deb, fin, croissance=1.3):

        self.nom="Gouvernement"
        inflation=1.0175
        present=ANNEE_REF
        super(modele_gouv,self).__init__(deb,present,fin)

        n = present-deb
        prix, smic, smpt, indfp = self.prix[n],self.smic[n],self.smpt[n],self.indfp[n]
        for i in xrange(present+1,fin+1):
            prix *= inflation
            smic *= (inflation+croissance/100.)
            smpt *= (inflation+croissance/100.)
            indfp *= inflation
            n = i-deb
            self.prix[n],self.smic[n],self.smpt[n],self.indfp[n] = prix, smic, smpt, indfp

        self.post_init()

            
# classe pour décrire le contexte macro envisagé par le modèle Destinie2

class modele_destinie(modele_abs):

    def __init__(self, deb, fin):

        self.nom="Destinie2"
        present=2018
        super(modele_destinie,self).__init__(deb,present,fin)

        i,j = present+1-deb, fin+1-deb
        self.prix[i:j], self.smic[i:j], self.smpt[i:j], self.indfp[i:j] = charge_donnees(present+1, fin)

        self.post_init()


#########################################################
# classes pour décrire une carrière (salaire et pension)


class carriere(object):

    age_max = 70
    
    def __init__(self, age_debut, annee_debut, nom_metier="Travailleur, Travailleuse"):

        self.age_debut = age_debut
        self.annee_debut = annee_debut
        self.pension = []
        self.nb_pts = [0.0]*(carriere.age_max+1-age_debut)
        self.nom_metier = nom_metier

        
    def calcule_retraite_macron(self,m):

        pension = []    
        nb_pts = []   
    
        pts = 0      
        for i in range(carriere.age_max - self.age_debut + 1):

            an = self.annee_debut + i
            
            # calcul des points
            pts += self.sal[i] / m.achat_pt[ an - m.debut ] 
            nb_pts.append ( pts )
            
            # calcul de la pension (si possible)
            age = self.age_debut + i
            if age  >=  m.age_legal:
                d = .05*(age - m.age_pivot)
                p = (1.0+d) * pts * m.vente_pt[ an - m.debut ]
                pension.append( (age, d, p, p/self.sal[i]) ) 

        self.pension = pension
        self.nb_pts = nb_pts
        

    def affiche_carriere(self,m):

        print "Annee   Age    Sal.cour Sal.cst   Pts    Ach.Pt  Vte.Pt"

        for i in xrange(carriere.age_max - self.age_debut + 1):
            an = self.annee_debut+i
            print "%d: %d ans   %.2f  %.2f   %.2f   %.2f  %.2f"%( an, self.age_debut+i, self.sal[i]/12, self.sal[i]/12/m.prix[ an - m.debut ]*m.prix[ ANNEE_REF - m.debut], self.nb_pts[i], m.achat_pt[an - m.debut], m.vente_pt[ an - m.debut] )

            
    def affiche_pension(self):

        for (a,d,p,t) in self.pension:
            print "Départ en %d (%d ans): sur/decote:%.2f  pension:%.2f => Tx remp brut:%.1f"%(self.annee_debut+a-self.age_debut,a,d,p/12,t*100)
            
    def affiche(self,m):
        self.affiche_carriere(m)
        self.affiche_pension()
        

        
# carrière dans le privé


class carriere_prive(carriere):
    
    def __init__(self, m, age_debut, annee_debut, nom_metier, coefs=[]):

        if coefs == []:
            coefs=[1.0]*(carriere.age_max+1-age_debut)
        
        super(carriere_smpt,self).__init__(age_debut, annee_debut, nom_m)
        self.sal = [ coefs[i] * m.smpt[ i + annee_debut - m.debut ] for i in xrange(carriere.age_max+1-age_debut) ]

        

        
        
# carrière dans le public

class carriere_public(carriere):

    grilles = [
        ( [("ATSEM2","ATSEM 2ème classe"),("AdjAdm2","Adjoint Administratif 2ème classe")], [ (329,1), (330,2), (333,2), (336, 2), (345,2), (351,2), (364,2), (380,2), (390,3), (402,3), (411,4), (418, 100) ] ),
        ( [("ATSEM1","ATSEM 1ère classe"),("AdjAdm1","Adjoint Administratif 1ère classe")], [ (350,1), (358,1), (368,2), (380,2), (393,2), (403,2), (415,3), (430,3), (450,3), (466,100) ] ),
        ( [("MCF","Maître de Conférences")], [ (474,1), (531,2+10./12), (584,2+10./12), (643,2+10./12), (693,2+10./12), (739,3.5), (769,2+10./12), (803,2+10./12), (830,100) ] ),
        ( [("CR","Chargé de Recherche Classe Normale")], [ (474,1), (510,2), (560,2+3./12), (600,2.5), (643,2.5), (693,2.5), (693,2.5), (739,3), (769,3), (803,2+9./12), (830,100) ] ),
        ( [("MCFHC","Maître de Conférences Hors Classe")], [(678,1), (716,1), (754,1), (796,1), (830,5), (880,100) ] ),
        ( [("PR2","Professeur d'Université 2ème classe")], [(667,1), (705,1), (743,1), (785,1), (830,3), (880,100) ] ),
        ( [("PR1","Professeur d'Université 1ère classe")], [(830,3), (967,1), (1008,1), (1062,1), (1119,1), (1143,1), (1168,100) ] ),
        ( [("ProfEcoles","Professeur des écoles (grille 2021)")], [(390,1), (441,1), (448,2), (461,2), (476,2.5), (492,3), (519,3), (557,3.5), (590,4), (629,4), (673,100) ] ), 
        ( [("ProfAgrege","Professeur agrégé (grille 2021)")], [(450,1), (498,1), (513,2), (542,2), (579,2.5), (618,3), (710,3.5), (757,4), (800, 4), (830,100) ] )   
    ]

    def __init__(self, m, age_debut, annee_debut, id_metier, part_prime=0.0):
        super(carriere_public,self).__init__(age_debut, annee_debut)

        n_metier=0
        while(True):
            if id_metier == carriere_public.grilles[n_metier][0][0][0]:
                break
            n_metier += 1

        self.nom_metier = carriere_public.grilles[n_metier][0][0][1]
            
        self.metier, grille = carriere_public.grilles[n_metier]
        self.part_prime=part_prime
        
        self.sal,self.sal_hp,self.prime = [],[],[]

        echelon, t = 0, grille[0][1]  # echelon, duree restante avant le prochain changement

        for i in xrange(carriere.age_max+1 - age_debut):
            
            annee = annee_debut+i 

            if t <= 1: # changement de echelon dans l'année (ou à la fin)
                sal_hp = (t * grille[echelon][0] + (1-t) * grille[echelon+1][0]) * m.indfp[annee-m.debut] 
                echelon += 1
                t = grille[echelon+1][1]-(1-t)
            else:
                sal_hp = grille[echelon][0] * m.indfp[annee-m.debut] 
                t -= 1
        
            prime = max( 0, part_prime + m.corr_part_prime[annee-m.debut] )
            
            sal = (sal_hp*(1+prime))
            if sal<m.smic[annee-m.debut]:
                sal = m.smic[annee-m.debut] 
            self.sal.append( sal )
            self.sal_hp.append( sal_hp )
            self.prime.append( prime )        



#######################################
# fonctions pour tracer des graphiques


def plot_modele(m, f, tit="", r=[]):
        
    if r==[]:
        r=[m.debut, m.fin]
    r2 = [ r[0]-m.debut, r[1]+1-m.debut ]
    r  = xrange(r[0],r[1]+1)
    plot(r,f[r2[0]:r2[1]], label=m.nom)

    axvline(ANNEE_REF, color="grey", linestyle="dashed")
    title(tit)


# fonction pour comparer les modèles macro

def plot_modeles(lm,r):

    for i in xrange(6):
        label = ["Prix (Inflation intégrée)","SMIC annuel","SMPT annuel","Valeur d' l'indice Fonction Publique","Valeur d'achat du point Macron","Valeur de vente du point Macron"][i]
        subplot(3,2,i+1)
        for m in lm:
            var = [m.prix, m.smic, m.smpt, m.indfp, m.achat_pt, m.vente_pt][i]
            plot_modele(m, var, dec(label),r)
        legend(loc='best')
    legend(loc='best')
    tight_layout()


# sur les carrières
            
def plot_carriere_corr(m, c, corr, div=12, couleur=(0.8,0.8,0.8),label=""):

    plot( xrange( c.annee_debut, c.annee_debut + carriere.age_max+1 - c.age_debut)  ,  [ c.sal[i]/div/corr[c.annee_debut+i-m.debut] for i in xrange(len(c.sal)) ], color=couleur, label=label  )

        

def plot_evolution_carriere_corr(ax, m, metier, prime, corr, focus, annees, labely, div, posproj=0.1):

    age_debut = 22

    # Evolution de carrière en fonction de l'année de départ
    for a in annees:
        c = carriere_public(m, age_debut, a, metier, prime)
        plot_carriere_corr(m,c,corr,div)

    # Courbes du SMIC et du SMPT
    rg = xrange( annees[0],  annees[-1] + carriere.age_max - age_debut )
    plot(rg, [m.smic[i-m.debut]/div/corr[i-m.debut] for i in rg], label="SMIC brut mensuel",color="red")
    plot(rg, [m.smpt[i-m.debut]/div/corr[i-m.debut] for i in rg], label="Salaire brut mensuel moyen)",color="blue")
    
    # Focus sur une annéee
    c = carriere_public(m, age_debut, focus, metier, prime)
    plot_carriere_corr(m,c,corr,div,"green",dec("Carrière commençant en %d"%focus))
    
    ylabel(labely)
    legend(loc="best")

    text(0.95, posproj, "Projection "+m.nom, ha='right', va='center', transform=ax.transAxes, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    axvline(ANNEE_REF, color="grey", linestyle="dashed")
    title( dec(c.nom_metier+", Prime(%d)=%d%%"%(ANNEE_REF,int(c.part_prime*100)) ) )
    
    
####################################################
# Partie principale



SAVE = True

debut, fin = 1945, 2120

# Modèle de projetion

m1 = modele_gouv(debut,fin)
m2 = modele_destinie(debut,fin)


def genere_comparaison_modeles(a,b):

    figure(figsize=(10,8))
    plot_modeles([m1,m2],[a,b])
    if SAVE:
        savefig("gouv_vs_dest.pdf")

print "Génération des courbes sur les modèles"
genere_comparaison_modeles(1950,2120)        

    
# Analyse des carrières 
    
tmp_dir = "./tmp/"
gif_dir = "./gif/"


def genere_anim( modeles, cas, annees ):

    for m in modeles:

        for metier_id,prime in cas:

            print metier_id, prime
            filename = "%s_%s_%d"%(m.nom,metier_id,int(prime*100))
            for focus in annees:
                print focus
            
                fig = figure()
                ax = fig.add_subplot(111)
                plot_evolution_carriere_corr(ax, m, metier_id, prime, m.smic, focus, annees, "Ratio salaire/SMIC", 1, posproj=0.5)
                if SAVE:
                    savefig(tmp_dir+"Ratio_"+filename+"_%d.png"%focus)

                fig = figure()
                ax = fig.add_subplot(111)
                plot_evolution_carriere_corr(ax, m,metier_id, prime, m.corr_prix_annee_ref, focus, annees, "Euros constants (2019)", 12, posproj=0.1)
                if SAVE:
                    savefig(tmp_dir+"Salaire_"+filename+"_%d.png"%focus)
                    
            if SAVE:    
                print "Génération de l'image animée Ratio_"+filename+".gif"
                shell_command( "convert -delay 50 -loop 0 "+tmp_dir+"Ratio_"+filename+"*.png "+gif_dir+"Ratio_"+filename+".gif" )
                shell_command( "rm "+tmp_dir+"Ratio_"+filename+"*.png" )
        
                print "Génération de l'image animée Salaire_"+filename+".gif"
                shell_command( "convert -delay 50 -loop 0 "+tmp_dir+"Salaire_"+filename+"*.png "+gif_dir+"Salaire_"+filename+".gif" )
                shell_command( "rm "+tmp_dir+"Salaire_"+filename+"*.png" )

                close('all')


                
cas = [ ("ProfEcoles",0.1), ("ProfAgrege",0.2), ("PR2",0.1), ("PR1",0.1), ("ATSEM1",0.2), ("ATSEM2",0.2), ("MCF",0.1), ("MCFHC",0.1), ("CR",0.1) ]
annees = xrange(1980,2041,5)
genere_anim( [m1], cas, annees )

show()
