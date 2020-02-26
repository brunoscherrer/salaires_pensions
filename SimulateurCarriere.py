#!/usr/bin/python
# coding:utf-8


###################################################################
### Simulateur micro de carrière (salaire et retraite à points) ###
###################################################################


###################################################################        
# classes pour décrire le contexte macro passé et futur


class ModeleAbs(object):  # classe abstraite


    def __init__(self, debut, fin, trucage):
        
        self.age_legal = 62
        self.trucage = trucage
        
        if self.trucage:
            self.age_pivot = [ max( 62+1./3., 62+1./3. + (i-2022)*1./3.) for i in range(debut,2027) ] + [ (64 + (i-2027)*1./12.) for i in range(2027,2039) ] + [ 65 ]*(fin-2039) 
        else:
            self.age_pivot = [ max( 62+1./3., 62+1./3. + (i-2022)*1./3.) for i in range(debut,2027) ] + [ (64 + (i-2027)*1./12.) for i in range(2027,fin) ]
        
        self.debut = debut
        self.fin = fin

        # initialisation
        n = fin + 1 - debut
        self.prix = [0.0]*n
        self.smic = [0.0]*n
        self.smpt = [0.0]*n
        self.indfp = [0.0]*n
                
        # charge l'historique des données passées (entre debut et debut_proj)
        n = self.annee_ref + 1 - debut
        self.prix[0:n], self.smic[0:n], self.smpt[0:n], self.indfp[0:n] = self.charge_donnees()

        
    def charge_donnees(self): # debut et fin compris    # fonction pour charger les données à partir du modèle Destinie2 (1,3% croissance)

        with open("./destinie2_1.3.csv","r") as f:

            n=self.annee_ref + 1 - self.debut
            prix, smic, indfp, smpt = [0.0]*n, [0.0]*n, [0.0]*n, [0.0]*n

            f.readline() # on vire la première ligne

            while True:
                l = f.readline()
                if not l:
                    break
                l = l.split("|")
                a = int( l[1] ) # annee
                if a > self.annee_ref:
                    break
                if a >= self.debut: # si l'année est bien dans la plage
                    b = a - self.debut
                    prix[b] = float( l[2].replace(',', '.') ) 
                    smic[b] = float( l[4].replace(',', '.') )
                    smpt[b] = float( l[6].replace(',', '.') )
                    indfp[b] = float( l[5].replace(',', '.') )

        return prix, smic, smpt, indfp

    
    def post_init(self):

        # Doit être lancé après l'initialisation pour calculer les valeurs du points, des corrections
        
        # calcul du point par rapport au valeurs 2020 (indexation sur interpolation inflation/smpt)
        n = self.fin+1-self.debut
        self.achat_pt = [0.0]*n
        self.vente_pt = [0.0]*n
        self.corr_prix_annee_ref = [0.0]*n

        # indexation progressive du point sur l'inflation vers le smpt (calcul du coef d'évolution
        coef=[1.0]*n

        for i in range(self.debut+1,self.fin+1):

            #if self.trucage: #### VIRER ?
            #    alpha=1.0  
            #else:
            alpha=max( 0, min (1, (i-2028)/17.) )  # évolution entre 2028 et 2045
            
            #print i-1, self.smpt[i-1-self.debut] 
            coef[i-self.debut] = coef[i-1-self.debut]*(
                alpha        * self.smpt[i-self.debut] / self.smpt[i-1-self.debut]  # interpolation linéaire du taux
                +(1.0-alpha) * self.prix[i-self.debut] / self.prix[i-1-self.debut]
                )
            
        for i in range(self.debut,self.fin+1):

            tmp = coef[i-self.debut] / coef[2025-self.debut]  # 1.0 en 2025 (date de mise en place des points)
            self.achat_pt[i-self.debut] = 10.0 / 0.9 / 0.2812 * tmp
            self.vente_pt[i-self.debut] = 0.55 * tmp
                        
            self.corr_prix_annee_ref[i-self.debut] = self.prix[ i - self.debut ] / self.prix[ self.annee_ref-self.debut ]

            
# classe pour décrire le contexte macro envisagé par le gouvernement

class ModeleGouv(ModeleAbs):
    
    def __init__(self, deb, fin, croissance=1.3, trucage=True):

        self.annee_ref=2019
        super(ModeleGouv,self).__init__(deb, fin, trucage)
        
        if self.trucage:
            self.nom="Gouvernement"
            self.id_modele="gouv"
        else:
            self.nom="Modèle corrigé (âge pivot glissant)"
            self.id_modele="corr"
                
        inflation=1.75
        n = self.annee_ref-deb
        prix, smic, smpt, indfp = self.prix[n], self.smic[n], self.smpt[n], self.indfp[n]
        for i in range(self.annee_ref+1,fin+1):
            prix *= (1+inflation/100.)
            smic *= (1+inflation/100.)*(1+croissance/100.)
            smpt *= (1+inflation/100.)*(1+croissance/100.)
            indfp *= (1+inflation/100.)
            n = i-deb
            self.prix[n],self.smic[n],self.smpt[n],self.indfp[n] = prix, smic, smpt, indfp

#            print "- ",i,deb,fin,self.smpt[i-deb]

#        print "1)", self.smpt
            
        self.post_init()

            
# classe pour décrire le contexte macro envisagé par le modèle Destinie2

class ModeleDestinie(ModeleAbs):

    def __init__(self, deb, fin, trucage=False):

        self.annee_ref = 2018
        super(ModeleDestinie,self).__init__(deb,fin,trucage)

        self.nom="Destinie2"
        
        i,j = self.annee_ref+1-deb, fin+1-deb
        self.prix[i:j], self.smic[i:j], self.smpt[i:j], self.indfp[i:j] = self.charge_donnees()

        self.post_init()




#########################################################
# classes pour décrire une carrière (salaire et pension)


class Carriere(object):

    # données générales

    age_max = 67   # age limite pour travailler (pour les simus)
    age_mort = 95  # age jusqu'auquel on simule la retraite


    def __init__(self, m, age_debut, annee_debut, id_metier, nom_metier):
    
        self.m = m
        self.id_metier = id_metier
        self.nom_metier = nom_metier
        self.age_debut = age_debut
        self.annee_debut = annee_debut
        self.pension = []
        self.nb_pts = [0.0]*(Carriere.age_max+1-age_debut)
        
        
    def calcule_retraite_macron(self):

        pension = []    
        nb_pts = []   

        # calculs des points et des pensions pour les différents âges de départ
        
        pts = 0      
        for i in range(Carriere.age_max - self.age_debut + 1):

            an = self.annee_debut + i
            
            # calcul des points
            pts += self.sal[i] / self.m.achat_pt[ an - self.m.debut ] 
            nb_pts.append ( pts )
            
            # calcul de la pension (si possible)
            age = self.age_debut + i
            if age in range(62, Carriere.age_max+1):
                
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
        
        for i in range(0,len(self.pension_macron)):
            
            (age,_,pens,_) = self.pension_macron[i]

            revenus_retraite.append([])
            annee0 = self.annee_debut + age - self.age_debut
            for a in range(age, Carriere.age_mort+1):   # années de retraites
                annee = self.annee_debut + a - self.age_debut
                p = pens / m.prix[ annee0 - m.debut ] * m.prix[ annee - m.debut ]  # hypothèse de revalorisation de la pension par rapport à l'inflation (ref=age de départ à la retraite)
                revenus_retraite[-1].append( p )
                
        self.revenus_retraite_macron = revenus_retraite
        


#########################
# carrière dans le privé


class CarrierePrive(Carriere):
    
    def __init__(self, m, age_debut, annee_debut, id_metier="Travailleur", nom_metier="Travailleur", coefs=[]):

        self.public = False
        
        if coefs == []:
            coefs=[1.0]*(Carriere.age_max+1-age_debut)
        
        super(CarrierePrive,self).__init__(m, age_debut, annee_debut, id_metier, nom_metier)
        self.sal = [ coefs[i] * m.smpt[ i + annee_debut - m.debut ] for i in range(Carriere.age_max+1-age_debut) ]

        self.calcule_retraite_macron()
        
        

##########################
# carrière dans le public


class CarrierePublic(Carriere):

    CORRECTION_GIPA = True # maintien du pouvoir d'achat
    
    HEA1,HEA2,HEA3,HEB1,HEB2,HEB3,HEBb1, HEBb2, HEBb3 = 890, 925,972, 972, 1013, 1067, 1067, 1095, 1124  # indices hors échelle
    grilles = [
        ( [("ATSEM","ATSEM (C2 puis C1)"),("AdjAdm","Adjoint Administratif (C2 puis C1)")], [ (329,1), (330,2), (333,2), (336, 2), (345,2), (351,2), (364,2), (380,2), (390,3), (402,3), (411,4), (415, 3), (430,3), (450,3), (466,100) ] ),
        ( [("CR","Chargé de Recherche (CN puis HC)"), ("MCF","Maître de Conférences (CN puis HC)")], [ (474,1), (510,2), (560,2+3./12), (600,2.5), (643,2.5), (693,2.5), (739,3), (769,3), (803,2+9./12), (830,5), (HEA1,1), (HEA2,1), (HEA3,100) ] ),
        ( [("DR","Directeur de Recherche (CRCN, DR2 puis DR1)"), ("PR","Professeur d'Université (MCF, PR2 puis PR1)") ], [ (474,1), (510,2), (560,2+3./12), (600,2.5), (643,2.5), (667, 1+3./12), (705, 1+3./12), (743, 1+3./12), (830, 1+3./12), (830, 3), (972,3), (1013,100) ] ),
        ( [("ProfCertifie","Professeur certifié"), ("ProfEcoles","Professeur des écoles")], [(450,1), (498,1), (513,2), (542,2), (579,2.5), (618,3), (710,3.5), (757,2), (800, 2), (830,100) ] ) ,
        ( [("Infirmier","Infirmière en soins généraux (CN, CS, puis HC)")], [(390,2), (404,3), (422,3), (446,3), (469,3), (501,3), (520,4), (544,4), (571,4), (594,4), (627,100) ] ),
        ( [("AideSoignant","Aide-soignante (CN puis HC)")], [(327,1), (328,2), (329,2), (330,2), (332,2), (334,2), (338,2), (342,2), (346,3), (356,3), (368,3+1./3), (380,2), (390,3), (402,3), (411,4), (418,100) ] ),
        ( [("Redacteur","Rédacteur territorial (C2 puis C1)")], [(356,2), (362,2), (369,2), (379,2), (390,2), (401,2), (416, 2), (436,3), (452,3), (461,3), (480,3), (504,4), (534,3), (551,3), (569,3), (587,100) ] ),
        ( [("BIATSS","BIATSS (CN puis CS)")], [(343,2), (349,2), (355,2), (361,2), (369,2), (381,2), (396,2), (415,3), (431,3), (441,3), (457,3), (477,4), (503,4), (534,100)] ),
        ( [("TechHosp","Technicien hospitalier"),("SecretaireAdmin","Secrétaire administratif")], [(339,2), (344,2), (349,2), (356,2), (366,2), (379,2), (394,2), (413,3), (429,3), (440,3), (453,3), (477,4), (503,100) ] ),
        ( [("AdjTech","Adjoint Technique (devenant principal C2 puis C1)")], [(326,1), (327,2), (328,2), (329,2), (330,2), (332,2), (335,2), (339,2), (343,3), (354,3), (367,3.33), (380,2), (390,3), (402,3), (411,4), (415,3), (430,3), (450,3), (466,100) ] ),
        ( [("Magistrat","Magistrat (second puis premier grade)")], [(461,1), (505,1), (555,2), (591,2), (667,1.5), (705,1.5), (743,1.5), (792,1.5), (830,2), (HEA1, 1), (HEA2,1), (HEA3,1), (HEB1,1), (HEB2,1), (HEB3,1), (HEBb1,1), (HEBb2,1), (HEBb3,100) ] ),
        ( [("ProfAgrege","Professeur agrégé")], [(450,1), (498,1), (513,2), (542,2), (579,2.5), (618,3), (710,3.5), (757,2), (800, 2), (830,3), (HEA1,1), (HEA2,1), (HEA3,100) ] )
        
    ]
    
    @classmethod
    def numero_metier_public(cls, id_metier):

        n_metier = [0,0]
        while ( n_metier[0] < len(CarrierePublic.grilles) ):
            lc = CarrierePublic.grilles[ n_metier[0] ][0]
            while n_metier[1] < len(lc):
                #print id_metier, lc[ n_metier[1] ][0]
                if id_metier == lc[ n_metier[1] ][0]:
                    return n_metier
                n_metier[1] += 1
            n_metier[0] +=1
            n_metier[1] = 0

        return(-1,0) # si pas trouvé
    
    
    def __init__(self, m, age_debut, annee_debut, id_metier, part_prime=0.0):

        self.public = True
        
        n_metier = CarrierePublic.numero_metier_public(id_metier)
        if n_metier == (-1,0):
            raise Exception("L'identifiant "+id_metier+" n'a pas été trouvé dans la liste des métiers publics!")
        self.n_metier = n_metier
        nom_metier = CarrierePublic.grilles[ n_metier[0] ][0][n_metier[1]][1]

        super(CarrierePublic,self).__init__(m, age_debut, annee_debut, id_metier, nom_metier)
        
        grille = CarrierePublic.grilles[n_metier[0]][1]
        
        self.part_prime = part_prime
        
        self.sal,self. sal_hp, self.prime, self.indm, self.gipa = [], [], [], [], []

        echelon, t = 0, grille[0][1]  # echelon, duree restante avant le prochain changement

        for i in range(Carriere.age_max+1 - age_debut):
            
            annee = annee_debut + i 
            
            if t <= 1: # changement de echelon dans l'année (ou à la fin)
                indm = (t * grille[echelon][0] + (1-t) * grille[echelon+1][0])
                echelon += 1
                t = grille[echelon][1]-(1-t)
            else:
                indm = grille[echelon][0]
                t -= 1

            sal_hp = indm * self.m.indfp[annee-self.m.debut] 
        
            prime = max( 0, part_prime - 0.0023*(43-i) )

            sal = (sal_hp*(1+prime))

            # calcul de l'indemnité GIPA pour suivre au moins l'inflation
            self.gipa.append( 0.0 )
            if i>=4 and self.CORRECTION_GIPA:
                sal2 = (  self.sal[i-1]/self.m.prix[annee+i-1 -self.m.debut]
                        + self.sal[i-2]/self.m.prix[annee+i-2 -self.m.debut]
                        + self.sal[i-3]/self.m.prix[annee+i-3 -self.m.debut]
                        + self.sal[i-4]/self.m.prix[annee+i-4 -self.m.debut]) / 4. * self.m.prix[annee+i - self.m.debut] # salaire lié au maintien du pouvoir d'achat 
                if sal2 > sal:
                    delta = sal2-sal
                    sal += delta
                    self.gipa[-1] = delta  # partie de la prime liée à la GIPA

            # ajout d'une prime pour remonter au SMIC si nécessaire
            sal2 = self.m.smic[annee-self.m.debut]
            if sal < sal2:
                sal = sal2
            
            self.sal.append( sal )
            self.sal_hp.append( sal_hp )
            self.prime.append( prime )        
            self.indm.append( indm )

        self.calcule_retraite_macron()


