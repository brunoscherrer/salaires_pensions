#!/usr/bin/python
# coding:utf-8


# Simulateur de carrière (salaire, retraite) pour le public et le privé


from pylab import *
import os

from prettytable import PrettyTable


# Remarque: convert doit être installé pour générer les gif


def shell_command(com):
    print com
    os.system(com)


# pour les images

ext_images = "jpg"

def mysavefig(f):
    savefig(dir_images+f)

    
ANNEE_REF = 2019 # année courante

PREVISION_MAX = 2100 # on regarde pas trop loin (ça n'a pas de sens)

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
    
    def __init__(self, deb, fin, croissance=1.3, indfp_index_sur_smpt=False):

        inflation=1.0175
        self.nom="Gouvernement_c%.1f_i%.2f_%s"%(croissance, (inflation-1)*100, str(indfp_index_sur_smpt))
        present=ANNEE_REF
        super(modele_gouv,self).__init__(deb,present,fin)

        n = present-deb
        prix, smic, smpt, indfp = self.prix[n],self.smic[n],self.smpt[n],self.indfp[n]
        for i in xrange(present+1,fin+1):
            prix *= inflation
            smic *= (inflation+croissance/100.)
            smpt *= (inflation+croissance/100.)
            if indfp_index_sur_smpt:
                indfp *= (inflation+croissance/100.)
            else:
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

    age_max = 69   # age limite pour travailler (pour les simus)
    age_mort = 82  # espérance de vie
    
    def __init__(self, m, age_debut, annee_debut, nom_metier="Travailleur/Travailleuse"):

        self.m = m
        self.age_debut = age_debut
        self.annee_debut = annee_debut
        self.pension = []
        self.nb_pts = [0.0]*(carriere.age_max+1-age_debut)
        self.nom_metier = nom_metier
        
        
    def calcule_retraite_macron(self):

        pension = []    
        nb_pts = []   
    
        pts = 0      
        for i in range(carriere.age_max - self.age_debut + 1):

            an = self.annee_debut + i
            
            # calcul des points
            pts += self.sal[i] / self.m.achat_pt[ an - self.m.debut ] 
            nb_pts.append ( pts )
            
            # calcul de la pension (si possible)
            age = self.age_debut + i
            if age in xrange(60, carriere.age_max+1):
                d = .05*(age - self.m.age_pivot)
                p = (1.0+d) * pts * self.m.vente_pt[ an - self.m.debut ]
                pension.append( (age, d, p, p/self.sal[i]) ) 

        self.pension_macron = pension
        self.nb_pts = nb_pts
        

    def affiche_carriere(self):

        print "Carrière"
        print "Annee   Age    Sal.cour Sal.cst   Pts    Ach.Pt  Vte.Pt"

        for i in xrange(carriere.age_max - self.age_debut + 1):
            an = self.annee_debut+i
            print "%d: %d ans   %.2f  %.2f   %.2f   %.2f  %.2f"%( an, self.age_debut+i, self.sal[i]/12, self.sal[i]/12/self.m.prix[ an - self.m.debut ]*self.m.prix[ ANNEE_REF - self.m.debut], self.nb_pts[i], self.m.achat_pt[an - self.m.debut], self.m.vente_pt[ an - self.m.debut] )
            
        self.affiche_pension_macron()

        
    def affiche_pension_macron(self):

        x = PrettyTable()
        
        print "Retraite Macron"
        x.field_names = ["Année de départ", "Age", "Surcote/décote", "Pension mens brute (EuroCour)", "Pension mens brute (EurCst)", "Taux de remplacement" ]
        for (a,d,p,t) in self.pension_macron:
            an = self.annee_debut+a-self.age_debut
            x.add_row( [ an, a, d, "%.2f"%(p/12), "%.2f"%(p/12/self.m.corr_prix_annee_ref[ an - self.m.debut]), "%.2f"%(t*100) ])

        print(x)
        

# carrière dans le privé


class carriere_prive(carriere):
    
    def __init__(self, m, age_debut, annee_debut, nom_metier="Privé", coefs=[]):

        if coefs == []:
            coefs=[1.0]*(carriere.age_max+1-age_debut)
        
        super(carriere_prive,self).__init__(m, age_debut, annee_debut, nom_metier)
        self.sal = [ coefs[i] * m.smpt[ i + annee_debut - m.debut ] for i in xrange(carriere.age_max+1-age_debut) ]

        self.calcule_retraite_macron()

        
        
# carrière dans le public

class carriere_public(carriere):

    grilles = [
        ( [("ATSEM2","ATSEM 2ème classe"),("AdjAdm2","Adjoint Administratif 2ème classe")], [ (329,1), (330,2), (333,2), (336, 2), (345,2), (351,2), (364,2), (380,2), (390,3), (402,3), (411,4), (418, 100) ] ),
        ( [("ATSEM1","ATSEM 1ère classe"),("AdjAdm1","Adjoint Administratif 1ère classe")], [ (350,1), (358,1), (368,2), (380,2), (393,2), (403,2), (415,3), (430,3), (450,3), (466,100) ] ),
        ( [("MCF","Maître de Conférences")], [ (474,1), (531,2+10./12), (584,2+10./12), (643,2+10./12), (693,2+10./12), (739,3.5), (769,2+10./12), (803,2+10./12), (830,100) ] ),
        ( [("CR","Chargé de Recherche Classe Normale")], [ (474,1), (510,2), (560,2+3./12), (600,2.5), (643,2.5), (693,2.5), (693,2.5), (739,3), (769,3), (803,2+9./12), (830,100) ] ),
        ( [("DR2","Directeur de Recherche 2ème classe")], [ (667, 1+3./12), (705, 1+3./12), (743, 1+3./12), (830, 1+3./12), (830, 3.5), (890,100) ] ),
        ( [("DR1","Directeur de Recherche 1ère classe")], [ (830,3), (972,3), (1013,3), (1067,100) ] ),
        ( [("MCFHC","Maître de Conférences Hors Classe")], [(678,1), (716,1), (754,1), (796,1), (830,5), (880,100) ] ),
        ( [("PR2","Professeur d'Université 2ème classe")], [(667,1), (705,1), (743,1), (785,1), (830,3), (880,100) ] ),
        ( [("PR1","Professeur d'Université 1ère classe")], [(830,3), (967,1), (1008,1), (1062,1), (1119,1), (1143,1), (1168,100) ] ),
        ( [("ProfEcoles","Professeur des écoles")], [(390,1), (441,1), (448,2), (461,2), (476,2.5), (492,3), (519,3), (557,3.5), (590,4), (629,4), (673,100) ] ), 
        ( [("ProfCertifie","Professeur certifié")], [(450,1), (498,1), (513,2), (542,2), (579,2.5), (618,3), (710,3.5), (757,4), (800, 4), (830,100) ] ) ,
        ( [("Infirmier","Infirmière en soins généraux")], [(422,2), (435,2), (455,2), (475,2), (498,3), (521,3.5), (544,4), (567,4), (594,4), (627,100)] ),
        ( [("AideSoignant","Aide-soignante hospitalière")], [(350,1), (358,1), (368,2), (380,2), (393,2), (403,2), (415,3), (430,3), (450,3), (466,100) ] )
    ]

    def __init__(self, m, age_debut, annee_debut, id_metier, part_prime=0.0):
        super(carriere_public,self).__init__(m, age_debut, annee_debut)

        n_metier=0
        while(True):
            if id_metier == carriere_public.grilles[n_metier][0][0][0]:
                break
            n_metier += 1

        self.n_metier = n_metier
        self.nom_metier = carriere_public.grilles[n_metier][0][0][1]
            
        self.metier, grille = carriere_public.grilles[n_metier]
        self.part_prime = part_prime
        
        self.sal,self. sal_hp, self.prime, self.indm = [],[],[], []

        echelon, t = 0, grille[0][1]  # echelon, duree restante avant le prochain changement

        for i in xrange(carriere.age_max+1 - age_debut):
            
            annee = annee_debut+i 

            if t <= 1: # changement de echelon dans l'année (ou à la fin)
                indm = (t * grille[echelon][0] + (1-t) * grille[echelon+1][0])
                echelon += 1
                t = grille[echelon][1]-(1-t)
            else:
                indm = grille[echelon][0]
                t -= 1

            sal_hp = indm * self.m.indfp[annee-self.m.debut] 
        
            prime = max( 0, part_prime + self.m.corr_part_prime[annee-self.m.debut] )
            
            sal = (sal_hp*(1+prime))
            if sal<self.m.smic[annee-self.m.debut]:
                sal = self.m.smic[annee-self.m.debut] 
            self.sal.append( sal )
            self.sal_hp.append( sal_hp )
            self.prime.append( prime )        
            self.indm.append( indm )

        self.calcule_retraite_macron()


    def affiche_carriere(self):

        print self.nom_metier," - an=annuel, mens=mensuel, HP=Hors Prime, EurCour=euros courants, EurConst=euros constants",ANNEE_REF

        x = PrettyTable()

        x.field_names = ["Année", "Age", "Ind maj", "IndFP an", "IndFP mens", "HP EuroCour an", "HP EuroCour mens", "Tx Prime", "EurCour an", "EurConst an", "EuroConst mens", "Tot Pts", "Val Ach Pt", "Val Vte Pt","Ind Prix" ]


        for i in xrange(carriere.age_max - self.age_debut + 1):
            an = self.annee_debut+i
            m = self.m
            sal_cst = self.sal[i]/m.corr_prix_annee_ref[ an - m.debut]  #m.prix[ an - m.debut ]*m.prix[ ANNEE_REF - m.debut]

            x.add_row( [ an, self.age_debut+i, "%.1f"%self.indm[i], "%.2f"%m.indfp[ an - m.debut ], "%.2f"%(m.indfp[ an - m.debut ]/12), "%.2f"%self.sal_hp[i], "%.2f"%(self.sal_hp[i]/12), "%.2f"%(self.prime[i]*100), "%.2f"%self.sal[i], "%.2f"%sal_cst, "%.2f"%(sal_cst/12), "%.2f"%self.nb_pts[i], "%.2f"%m.achat_pt[ an - m.debut], "%.2f"%m.vente_pt[ an - m.debut], "%.2f"%m.prix[ an - m.debut ] ])

        print(x)
            
        self.affiche_pension_macron()
        
    def plot_grille(self):

        g = carriere_public.grilles[self.n_metier][1]
        x,y = 0, g[0][0]
        lx, ly = [x], [y]
    
        for i in xrange(1,len(g)):
            dx = g[i-1][1]
            lx.append(x+dx)
            ly.append(y)
            x = x+dx
            y = g[i][0]
            lx.append(x)
            ly.append(y)
        lx.append(45)
        ly.append(y)
        
        plot(lx,ly)
        xlabel(dec("Ancienneté"))
        ylabel(dec("Indice majoré"))
        title(dec("Grille indiciaire ("+self.nom_metier)+")")
        

    def plot_grille_prime(self):

        figure(figsize=(11,4))

        subplot(1,2,1)
        self.plot_grille()
        
        subplot(1,2,2)
        plot( [self.prime[i]*100 for i in xrange(len(self.prime))] )
        xlabel(dec("Ancienneté"))
        ylabel(dec("Pourcentage du salaire brut"))
        title(dec("Prime ("+self.nom_metier)+")")



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
        label = ["Prix (Inflation intégrée)","SMIC annuel","SMPT annuel","Valeur du point d'indice de la Fonction Publique","Valeur d'achat du point Macron","Valeur de vente du point Macron"][i]
        subplot(3,2,i+1)
        for m in lm:
            var = [m.prix, m.smic, m.smpt, m.indfp, m.achat_pt, m.vente_pt][i]
            plot_modele(m, var, dec(label),r)
        legend(loc='best')
    tight_layout()


def plot_comparaison_modeles(a,b):

    figure(figsize=(10,8))
    plot_modeles([m1,m2],[a,b])
    if SAVE:
        mysavefig("gouv_vs_dest.jpg")
        close('all')



# sur les carrières

def plot_grilles( m, cas ):

    for id_metier,_ in cas:

        figure()
        filename = "grille_%s.%s"%( id_metier, ext_images)
        print "Génération du fichier",filename
        c = carriere_public(m, 25, 2019, id_metier, 0.0)
        c.plot_grille()
        if SAVE:
            mysavefig(filename)
            close('all')
    


def plot_carriere_corr(ax, m, c, corr, div=12, plot_retraite=0, couleur=(0.8,0.8,0.8),label="", ):

    # plot_retraite: 0:rien, 1:retraite macron, 2:retraite actuelle
    
    plot( xrange( c.annee_debut, c.annee_debut + carriere.age_max+1 - c.age_debut)  ,  [ c.sal[i] / div / corr[c.annee_debut + i - m.debut] for i in xrange(len(c.sal)) ], color=couleur, label=label  )

    if plot_retraite==1:
        for i in xrange(0,len(c.pension_macron),2):
            (age,_,pens,t) = c.pension_macron[i]
            annee0 = c.annee_debut + age - c.age_debut
            lx = [ annee0 ]    # age de départ
            ly = [ c.sal[age - c.age_debut] / div / corr[ annee0 - m.debut  ]  ]   # dernier salaire
            for a in xrange(age, carriere.age_mort+1):   # années de retraites
                annee = c.annee_debut + a-c.age_debut
                lx.append( annee )
                p = pens / m.prix[ annee0 - m.debut ] * m.prix[ annee - m.debut ]  # revalorisation de la pension par rapport à l'inflation (ref=age de départ à la retraite)
                ly.append( p / div / corr[ annee - m.debut ] )                
            plot( lx, ly, color=couleur, linestyle="dashed", label=dec("Retraite (âge, tx remp)") )

            p1 = ax.transData.transform_point((lx[1], ly[1]))
            p2 = ax.transData.transform_point((lx[-1], ly[-1]))
            dy = (p2[1] - p1[1])
            dx = (p2[0] - p1[0])
            rotn = degrees(np.arctan2(dy, dx))
            text( p1[0]+2,p1[1]+2, dec("%d ans, %d%%"%(age,t*100)), transform=None, rotation=rotn )

            
def plot_evolution_carriere_corr(ax, m, id_metier, prime, corr, focus, annees, labely, div, plot_retraite=0, posproj=0.95):

    age_debut = 22

    # Evolution de carrière en fonction de l'année de départ
    for a in annees:
        if id_metier=="Privé":
            c = carriere_prive(m, age_debut, a )
        else:
            c = carriere_public(m, age_debut, a, id_metier, prime)
        plot_carriere_corr(ax,m,c,corr,div)

    # Courbes du SMIC et du SMPT
    rg = xrange( annees[0], PREVISION_MAX )
    plot(rg, [m.smic[i-m.debut]/div/corr[i-m.debut] for i in rg], label="SMIC",color="red")
    plot(rg, [m.smpt[i-m.debut]/div/corr[i-m.debut] for i in rg], label="Salaire moyen",color="blue")
    
    # Focus sur une année
    if id_metier=="Privé":
        c = carriere_prive(m, age_debut, focus )
    else:
        c = carriere_public(m, age_debut, focus, id_metier, prime)
    plot_carriere_corr(ax, m, c, corr, div, plot_retraite, "green", dec("Salaire (déb:%d"%focus)+")")
    
    ylabel(labely)
    legend(loc="best")

    text(0.45, 0.95 , "Projection "+m.nom, ha='left', va='top', transform=ax.transAxes, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    axvline(ANNEE_REF, color="grey", linestyle="dashed")
    if id_metier=="Privé":
        title( dec(c.nom_metier) )
    else:
        title( dec(c.nom_metier+", Prime(%d)=%d%%"%(ANNEE_REF,int(c.part_prime*100)) ) )

            
def genere_anim( modeles, cas, annees, plot_retraite=0 ):

    tmp_dir = "./tmp/"
    
    for m in modeles:

        for id_metier,prime in cas:

            print id_metier, prime
            filename = "%s_%s_%d"%(m.nom,id_metier,int(prime*100))

            for focus in annees:
                print focus
            
                fig = figure( figsize=(8,6) )
                a = annees[0]
                xlim( (a, PREVISION_MAX) )
                ax = fig.add_subplot(111)
                plot_evolution_carriere_corr(ax, m, id_metier, prime, m.smpt, focus, annees, "Ratio revenu/SMPT", 1, plot_retraite)
                if SAVE:
                    savefig(tmp_dir+"Ratio_"+filename+"_%d.png"%focus)

                fig = figure( figsize=(8,6) )
                a = annees[0]
                xlim( (a, PREVISION_MAX) )
                ax = fig.add_subplot(111)
                plot_evolution_carriere_corr(ax, m,id_metier, prime, m.corr_prix_annee_ref, focus, annees, "Euros constants (2019)", 12, plot_retraite)
                if SAVE:
                    savefig(tmp_dir+"Salaire_"+filename+"_%d.png"%focus)
                    
            if SAVE:    
                print "Génération de l'image animée Ratio_"+filename+".gif"
                shell_command( "convert -delay 300 -loop 0 "+tmp_dir+"Ratio_"+filename+"*.png "+dir_images+"Ratio_"+filename+".gif" )
                shell_command( "rm "+tmp_dir+"Ratio_"+filename+"*.png" )
        
                print "Génération de l'image animée Salaire_"+filename+".gif"
                shell_command( "convert -delay 300 -loop 0 "+tmp_dir+"Salaire_"+filename+"*.png "+dir_images+"Salaire_"+filename+".gif" )
                shell_command( "rm "+tmp_dir+"Salaire_"+filename+"*.png" )
            
                close('all')




####################################################
# Partie principale
####################################################


def simu0():

    global dir_images
    dir_images="./fig/modeles/"
    
    print "Génération de la comparaison des modèles macro de prédiction"
    plot_comparaison_modeles(debut,fin)        

    print "Génération des grilles indiciaires"
    plot_grilles( m1, cas )

    c=carriere_public(m1,25,2019,"ProfEcoles",0.07)
    c.plot_grille_prime()
    mysavefig("Carriere_ProfEcoles")

    
def simu1():

    global dir_images

    print "Génération d'animations gif sur l'évolution de carrières dans le public"

    dir_images = "./fig/salaires_retraites/"
    genere_anim( [m1,m2], cas, range(1980,2041,5), 1 )

    dir_images = "./fig/salaires/"
    genere_anim( [m1,m2], cas, range(2020, 2061, 5), 0 )
    

def debug0():

    c=carriere_public(m1,22,2012,"ProfEcoles",0.08)
    c.affiche_carriere()

    c=carriere_public(m1,22,2012,"ProfCertifie",0.09)
    c.affiche_carriere()


####

SAVE = True   # si False: ne génère pas les fichiers images/animations


# Modèles de projection

debut, fin = 1980, 2120

m1 = modele_gouv(debut,fin,1.3,False)
m2 = modele_gouv(debut,fin,1.3,True)
#m3 = modele_destinie(debut,fin)


# Carrières considérées

cas = [ ("ProfEcoles",0.08), ("ProfCertifie",0.09), ("PR2",0.1), ("PR1",0.1), ("ATSEM1",0.1), ("ATSEM2",0.1), ("MCF",0.1), ("MCFHC",0.1), ("CR",0.1), ("DR1",0.1), ("DR2",0.1), ("Infirmier",0.23), ("AideSoignant",0.19) ]


### Génération d'un exemple

debug0()

### Génération comparaison modèles
    
simu0()


### Génération infographies

simu1()

###

if not SAVE:
    show()
