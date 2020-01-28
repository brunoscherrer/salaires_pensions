#!/usr/bin/python
# coding:utf-8

#####################################################################
### Simulateur micro de carrière (salaire et retraite à points)
#####################################################################

# Remarque: convert doit être installé pour générer les gif


ANNEE_REF = 2019 # année courante (délimite le futur du passé)
PREVISION_MAX = 2110 # on regarde pas trop loin (ça n'a pas de sens)


from pylab import *
import os

from prettytable import PrettyTable


def shell_command(com):
    print com
    os.system(com)


# pour les images (type de fichier)

ext_images = "png"

def mysavefig(f):
    savefig(dir_images+f)

# pour le codage utf8 (matplotlib)

def dec(s):
    return s.decode("utf-8")



###################################################################################
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

        self.age_pivot = [ max( 64, 65 + (i-2040)/12.) for i in xrange(debut,fin+1) ]
        
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

        inflation=1.0175
        self.nom="Gouvernement"
        present=ANNEE_REF
        super(modele_gouv,self).__init__(deb,present,fin)

        n = present-deb
        prix, smic, smpt, indfp = self.prix[n],self.smic[n],self.smpt[n],self.indfp[n]
        for i in xrange(present+1,fin+1):
            prix *= inflation
            smic *= (inflation+croissance/100.)
            smpt *= (inflation+croissance/100.)
            #if indfp_index_sur_smpt:
            #    indfp *= (inflation+croissance/100.)
            #else:
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

    age_max = 68   # age limite pour travailler (pour les simus)
    age_mort = 90  # age jusqu'auquel on simule la retraite
    
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

        # calculs des points et des pensions pour les différents âges de départ
        
        pts = 0      
        for i in range(carriere.age_max - self.age_debut + 1):

            an = self.annee_debut + i
            
            # calcul des points
            pts += self.sal[i] / self.m.achat_pt[ an - self.m.debut ] 
            nb_pts.append ( pts )
            
            # calcul de la pension (si possible)
            age = self.age_debut + i
            if age in xrange(60, carriere.age_max+1):
                
                d = .05*(age - self.m.age_pivot[ an - self.m.debut ] )
                p = (1.0+d) * pts * self.m.vente_pt[ an - self.m.debut ]

                if age - self.age_debut >= 43:  # retraite à "1000 euros" (85% du SMIC) si au moins 43 annuités
                    p = max(p, 0.85*self.m.smic[ an - self.m.debut ])
                
                pension.append( (age, d, p, p/self.sal[i]) )
                
        self.pension_macron = pension
        self.nb_pts = nb_pts


        # calculs des revenus pendant les retraites (selon les différents âges de départ)

        revenus_retraite = []
        m = self.m   # raccourci
        
        for i in xrange(0,len(self.pension_macron)):
            
            (age,_,pens,_) = self.pension_macron[i]

            revenus_retraite.append([])
            annee0 = self.annee_debut + age - self.age_debut
            for a in xrange(age, carriere.age_mort+1):   # années de retraites
                annee = self.annee_debut + a - self.age_debut
                p = pens / m.prix[ annee0 - m.debut ] * m.prix[ annee - m.debut ]  # hypothèse de revalorisation de la pension par rapport à l'inflation (ref=age de départ à la retraite)
                revenus_retraite[-1].append( p )
                
        self.revenus_retraite_macron = revenus_retraite
        

    def affiche_carriere(self, style="text"):

        m = self.m   # raccourci

        if style == "tex":

            pass

        else: # default style="text"

            x = PrettyTable()
            
            print self.nom_metier
            x.field_names = [ "Annee","Age","Salaire","Salaire EC","Pts","Ach.Pt","Vte.Pt" ]

            for i in xrange(carriere.age_max - self.age_debut + 1):
                an = self.annee_debut+i
                x.add_row( [ "%d"%an, "%d ans"%(self.age_debut+i),"%.2f"%( self.sal[i]/12),"%.2f"%(self.sal[i]/12/m.prix[ an - m.debut ]*m.prix[ ANNEE_REF - m.debut]),"%.2f"%(self.nb_pts[i]),"%.2f"%(m.achat_pt[an - m.debut]),"%.2f"%(m.vente_pt[ an - m.debut]) ] )

            print(x)
            self.affiche_pension_macron(style)

        
    def affiche_pension_macron(self, style="text"):

        m = self.m
        
        if style == "tex":

            pass

        else: # default style="text"
        
            x = PrettyTable()
            print "Retraite Macron (Synthèse départs)"
            x.field_names = ["Année", "Age", "AgePivot", "Sur-/dé-cote", "Brut ms", "Brut ms EC", "Tx rempl.", "%/SMIC" ]
            for (a,d,p,t) in self.pension_macron:
                an = self.annee_debut+a-self.age_debut
                ap = int(m.age_pivot[ an - m.debut])
                x.add_row( [ an, a, "%d ans %d mois"%(ap, round((m.age_pivot[ an - m.debut]-ap)*12)), d, "%.2f"%(p/12), "%.2f"%(p/12/m.corr_prix_annee_ref[ an - m.debut]), "%.2f"%(t*100), "%.2f"%(p/m.smic[ an - m.debut ]) ])
            print(x)

            print "Retraite Macron (détaillée selon départ)"
            i=0
            for (a,_,_,_) in self.pension_macron:
                an = self.annee_debut+a-self.age_debut
                print "Départ à %d ans (en %d)"%(a, an)
                x = PrettyTable()
                x.field_names = ["Année", "Age", "Brut ms", "Brut ms EC", "%/SMIC" ]
                for j in xrange(carriere.age_mort+1 - a):
                    an = self.annee_debut+a-self.age_debut + j
                    p = self.revenus_retraite_macron[i][j]
                    x.add_row( [ an, a+j, "%.2f"%(p/12), "%.2f"%(p/12/m.corr_prix_annee_ref[ an - m.debut]), "%.2f"%(p/m.smic[ an - m.debut ]) ] ) 
                #####
                print(x)
                i=i+1
            
        

#########################
# carrière dans le privé


class carriere_prive(carriere):
    
    def __init__(self, m, age_debut, annee_debut, nom_metier="Privé", coefs=[]):

        if coefs == []:
            coefs=[1.0]*(carriere.age_max+1-age_debut)
        
        super(carriere_prive,self).__init__(m, age_debut, annee_debut, nom_metier)
        self.sal = [ coefs[i] * m.smpt[ i + annee_debut - m.debut ] for i in xrange(carriere.age_max+1-age_debut) ]

        self.calcule_retraite_macron()
        
        

##########################
# carrière dans le public


CORRECTION_GIPA = True # maintien du pouvoir d'achat

class carriere_public(carriere):

    # TODO: rentrer plus de grilles
    
    grilles = [
        ( [("ATSEM","ATSEM (C2 puis C1)"),("AdjAdm","Adjoint Administratif (C2 puis C1)")], [ (329,1), (330,2), (333,2), (336, 2), (345,2), (351,2), (364,2), (380,2), (390,3), (402,3), (411,4), (415, 3), (430,3), (450,3), (466,100) ] ),
        ( [("CR","Chargé de Recherche (CN puis HC)"), ("MCF","Maître de Conférences (CN puis HC)")], [ (474,1), (510,2), (560,2+3./12), (600,2.5), (643,2.5), (693,2.5), (693,2.5), (739,3), (769,3), (803,2+9./12), (830,100) ] ),
        ( [("DR","Directeur de Recherche (DR2 puis DR1)"), ("PR","Professeur d'Université (PR2 puis PR1)") ], [ (667, 1+3./12), (705, 1+3./12), (743, 1+3./12), (830, 1+3./12), (830, 3), (972,3), (1013,100) ] ),
        ( [("ProfCertifie","Professeur certifié"), ("ProfEcoles","Professeur des écoles")], [(450,1), (498,1), (513,2), (542,2), (579,2.5), (618,3), (710,3.5), (757,2), (800, 2), (830,100) ] ) ,
        ( [("Infirmier","Infirmière en soins généraux (CN, CS, puis HC)")], [(390,2), (404,3), (422,3), (446,3), (469,3), (501,3), (520,4), (544,4), (571,4), (594,4), (627,100) ] ),
        ( [("AideSoignant","Aide-soignante (CN puis HC)")], [(327,1), (328,2), (329,2), (330,2), (332,2), (334,2), (338,2), (342,2), (346,3), (356,3), (368,3+1./3), (380,2), (390,3), (402,3), (411,4), (418,100) ] ),
        ( [("Redacteur","Rédacteur territorial (C2 puis C1)")], [(356,2), (362,2), (369,2), (379,2), (390,2), (401,2), (416, 2), (436,3), (452,3), (461,3), (480,3), (504,4), (534,3), (551,3), (569,3), (587,100) ] )
        
    ]

    @classmethod
    def numero_metier(cls, id_metier):

        n_metier = [0,0]
        while ( n_metier[0] < len(carriere_public.grilles) ):
            lc = carriere_public.grilles[ n_metier[0] ][0]
            while n_metier[1] < len(lc):
                if id_metier == lc[ n_metier[1] ][0]:
                    return n_metier
                n_metier[1] += 1
            n_metier[0] +=1
            n_metier[1] = 0

        return(-1,0) # si pas trouvé
            
    
    def __init__(self, m, age_debut, annee_debut, id_metier, part_prime=0.0):
        
        super(carriere_public,self).__init__(m, age_debut, annee_debut)

        n_metier = carriere_public.numero_metier(id_metier)
        if n_metier == (-1,0):
            raise Exception(id_metier+" n'a pas été trouvé dans la liste des métiers publics")

        self.n_metier = n_metier
        self.nom_metier = carriere_public.grilles[ n_metier[0] ][0][n_metier[1]][1]
        
        grille = carriere_public.grilles[n_metier[0]][1]
        
        self.part_prime = part_prime
        
        self.sal,self. sal_hp, self.prime, self.indm, self.gipa = [], [], [], [], []

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

            # ajout d'une prime pour remonter au SMIC si nécessaire
            sal2 = self.m.smic[annee-self.m.debut]
            if sal < sal2:
                sal = sal2

            # calcul de l'indemnité GIPA pour suivre au moins l'inflation
            self.gipa.append( 0.0 )
            if i>0 and CORRECTION_GIPA:
                sal2 = self.sal[-1] / self.m.prix[annee-1 -self.m.debut] * self.m.prix[annee - self.m.debut] # salaire lié au maintien du pouvoir d'achat
                if sal2 > sal:
                    delta = sal2-sal
                    sal += delta
                    self.gipa[-1] = delta  # partie de la prime liée à la GIPA
                    
            self.sal.append( sal )
            self.sal_hp.append( sal_hp )
            self.prime.append( prime )        
            self.indm.append( indm )

        self.calcule_retraite_macron()


    def affiche_carriere(self, style="text"):

        if style == "tex":

            pass

        else: # default style="text"
        
            print self.nom_metier," - an=annuel, ms=mensuel, HP=Hors Prime, EC=euros constants",ANNEE_REF

            x = PrettyTable()

            x.field_names = ["Année", "Age", "IndMaj", "VInd an", "VInd ms", "BrutHP an", "BrutHP ms", "TxPrime", "GIPA ms", "Brut an", "Brut an EC", "Brut ms EC", "%/SMIC", "Tot Pts", "AchPt", "VtePt","Prix" ]

            
            for i in xrange(carriere.age_max - self.age_debut + 1):
                an = self.annee_debut+i
                m = self.m
                sal_cst = self.sal[i] / m.corr_prix_annee_ref[ an - m.debut]  #m.prix[ an - m.debut ]*m.prix[ ANNEE_REF - m.debut]

                x.add_row( [ an,
                             self.age_debut+i,
                             "%.1f"%self.indm[i],
                             "%.2f"%m.indfp[ an - m.debut ],
                             "%.2f"%(m.indfp[ an - m.debut ]/12),
                             "%.2f"%self.sal_hp[i],
                             "%.2f"%(self.sal_hp[i]/12),
                             "%.2f"%(self.prime[i]*100),
                             "%.2f"%(self.gipa[i]/12),
                             "%.2f"%self.sal[i],
                             "%.2f"%sal_cst,
                             "%.2f"%(sal_cst/12),
                             "%.2f"%(self.sal[i] / m.smic[ an - m.debut ]),
                             "%.2f"%self.nb_pts[i],
                             "%.2f"%m.achat_pt[ an - m.debut],
                             "%.2f"%m.vente_pt[ an - m.debut],
                             "%.2f"%m.prix[ an - m.debut ]
                ] )

            print(x)
            
            self.affiche_pension_macron(style)
        
    def plot_grille(self):

        g = carriere_public.grilles[self.n_metier[0]][1]
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
        legend(loc='upper right')
    tight_layout()


def plot_comparaison_modeles(lm, a,b):

    figure(figsize=(10,8))
    plot_modeles(lm,[a,b])
    if SAVE:
        mysavefig("gouv_vs_dest.png")
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
            lx = [ c.annee_debut + a - c.age_debut   for a in xrange(age, carriere.age_mort+1) ]  # années de retraite
            ly = [ c.revenus_retraite_macron[i][j] / div / corr[ lx[j] - m.debut ]   for j in xrange(carriere.age_mort+1 - age) ]  # revenus de retraite

            lx = [ lx[0] ] + lx
            ly = [ pens/t / div / corr[ lx[0] - m.debut ] ] + ly

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
    legend(loc="upper right")

    y1,y2 = ax.get_ylim()
    y = y1+(y2-y1)*0.98
    text(ANNEE_REF+2, y, dec("Projection "+m.nom), ha='left', va='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    if annees[0]<ANNEE_REF:
        text(ANNEE_REF-2, y, dec("Données réelles"), ha='right', va='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
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
    dir_images="./fig/grilles/"
      
    print "Génération des grilles indiciaires"
    plot_grilles( m1, cas )

    c=carriere_public(m1,25,2019,"ProfEcoles",0.08)
    c.plot_grille_prime()
    mysavefig("Carriere_ProfEcoles")

    
def simu1():

    global dir_images

    dir_images="./fig/"
    print "Génération de la comparaison des modèles macro de prédiction"
    plot_comparaison_modeles([m1,m2],debut,fin)  
    
    print "Génération d'animations gif sur l'évolution de carrières dans le public"
    dir_images = "./fig/salaires_retraites/"
    genere_anim( [m1, m2], cas, range(1980,2041,5), 1 )
    dir_images = "./fig/salaires/"
    genere_anim( [m1, m2], cas, range(1980,2041,5), 0 )
    

def debug0():

    print "Details carrière et retraite pour deux professions"
    
    c=carriere_public(m1,22,2020,"ProfEcoles",0.08)
    c.affiche_carriere()

    c=carriere_prive(m1,22,2002)
    c.affiche_carriere()


def pour_article_1():

    global dir_images
    dir_images = "./articles/1/"
       
    id_metier = "ProfEcoles"
    prime = 0.08

    m = m1

    c = carriere_public(m1,22,2020, id_metier, prime)
    c.plot_grille_prime()
    mysavefig("grille.png")
    
    fig=figure()
    xlim( (2020,2070) )
    ax = fig.add_subplot(111)
    plot_evolution_carriere_corr(ax, m, id_metier, prime, m.prix, 2020, [2020], "Euros constants (2019)", 12)
    if SAVE:
        mysavefig("salaireEC.png")
    
    fig=figure()
    xlim( (2020,2070) )
    ax = fig.add_subplot(111)
    plot_evolution_carriere_corr(ax, m, id_metier, prime, m.smpt, 2020, [2020], "Ratio revenu/SMPT", 1)
    if SAVE:
        mysavefig("salaireRel.png")
    
    # animations
    genere_anim( [m1], [ (id_metier,prime) ], range(2020,2051,5), 0 )
    shell_command("mv "+dir_images+"Ratio_Gouvernement_"+id_metier+"_%d"%(prime*100)+".gif "+dir_images+"selonannee.gif")
    genere_anim( [m1], [ (id_metier,prime) ], range(1980,2051,5), 1 )
    shell_command("mv "+dir_images+"Ratio_Gouvernement_"+id_metier+"_%d"%(prime*100)+".gif "+dir_images+"selonannee_retraite.gif")
    
    

####

SAVE = True   # si False: ne génère pas les fichiers images/animations


# Modèles de projection

debut, fin = 1980, 2120

m1 = modele_gouv(debut,fin)
m2 = modele_destinie(debut,fin)


# Carrières considérées

cas = [ ("ProfEcoles",0.081), ("ProfCertifie",0.096), ("PR",0.071), ("ATSEM",0.16), ("MCF",0.034), ("CR",0.034), ("DR",0.071), ("Infirmier",0.299), ("AideSoignant",0.242), ("Redacteur",0.281) ]



### Génération d'un exemple

debug0()

### Génération comparaison des grilles
    
simu0()


### Génération comparaison modèles et infographies

simu1()

###

pour_article_1()

###

if not SAVE:
    show()
