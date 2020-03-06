#!/usr/bin/python
# coding:utf-8

from SimulateurCarriere import *
from AnalyseCarriere import *
from tools import *
import matplotlib.pyplot as plt
import sys

# Modèle de projection: Gouvernement corrigé

debut, fin = 1980, 2120
m = ModeleGouv(1980,2120,1.3,False) # modèle du gouv avec age glissant corrigé

###

# Cas d'une trajectoire dans le privé

c = CarrierePrive(m, # le modèle
                  22,                             # age de début
                  1995,                           # année de début
                  "IdPrive",                      # ce qu'on veut (sert pour générer des fichiers images)
                  "travailleur, travailleuse",    # description du métier
                  [1.0]*10 + [2.0]*20 + [1.5]*20, # tableau décrivant la courbe salaire du métier par rapport au...
                  "SMIC",                         # ... SMIC
                  [1.0, (30, 0.6), (40, 1.)]      # PARAMETRE FACULTATIF: quotité temps plein au début, passage à 60% à 30 ans, retour à 100% à 40 ans  (par défaut, temps plein: [1.0]))
                  )

a = AnalyseCarriere(c)
print(c.nom_metier)
a.affiche_carriere(False, sys.stdout )        # sortie texte d'un tableau récapitulatif de la carrière, flux en paramètre
a.affiche_pension_macron(0, False, sys.stdout)   # 
print("\n")

fig = plt.figure()
ax = fig.add_subplot(1,1,1)
AnalyseCarriere.plot_evolution_carriere_corr(0, ax, m.smic, 0, [c], c.annee_debut+60, "Revenu/SMIC", dec("Titre: "+c.nom_metier), 12, 1)  # trace la courbe normalisée par le smic



###

# Cas d'une trajectoire dans le public

# Rajout d'une grille indiciaire
CarrierePublic.grilles.append(  ( [("Toto",  # IDIENTIFIANT METIER PUBLIC
                                    "Métier Public Toto")], [ (329,1),  # Indice majoré 329 pendant 1 an
                                                                      (330,2),  # Indice majoré 330 pendant 2 ans
                                                                      (333,2.6),  # etc.
                                                                      (466,100) ] ) # Indice terminal
                                 )
c = CarrierePublic(m,
                   23,                             # age début
                   1997,                           # année début
                   "Toto",                         # IDENTIFIANT METIER PUBLIC  (voir dans le fichier SimulateurCarriere.py pour les grilles déja rentrées)
                   .1,                             # taux de prime en fin de carrière
                   [1.0, (30, 0.6), (40, 1.)]      # PARAMETRE FACULTATIF: quotité temps plein au début, passage à 60% à 30 ans, retour à 100% à 40 ans  (par défaut, temps plein: [1.0])
                   )

a = AnalyseCarriere(c)
print(c.nom_metier)
a.affiche_carriere(False, sys.stdout )        # sortie texte d'un tableau récapitulatif de la carrière, flux en paramètre
a.affiche_pension_macron(0, False, sys.stdout)   # 
print("\n")

fig = plt.figure()
ax = fig.add_subplot(1,1,1)
AnalyseCarriere.plot_evolution_carriere_corr(0, ax, m.smic, 0, [c], c.annee_debut+60, "Revenu/SMIC", dec("Titre: "+c.nom_metier), 12, 1)  # trace la courbe normalisée par le smic


# affiche les graphiques
plt.show()
