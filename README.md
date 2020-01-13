# Simulateur de carrière (salaire et pension de retraite)


Ce projet a pour objectif de 

- de simuler des carrières dans le public comme dans le privé ;
- de donner une vison d'ensemble des carrières (comparaison public, privé, SMIC, salaire moyen) ;
- de calculer pour ces carrières les retraites (système actuel et réforme Macron).

Il permet d'utiliser plusieurs types de projections macro-économiques pour les années à venir:

- les hypothèses du gouvernement (inflation 1.75%/an, croissance 1.3%) ;
- les hypothèses extraites du modèle Destinie2 utilisé par le COR (inflation 1.75%, croissance 1.3%)

Le code permet de générer des figures, gif animés.

Voila une comparaison 2 modèles macro-économiques pour l'instant considérés:

![](./gouv_vs_dest.jpg)

Voici, par exemple, dans les hypothèses du gouvernement, l'évolution du salaire en euros constants (2019) d'un *professeur des écoles ayant une prime de 10% en 2019* en fonction de l'année de son début de carrière:

![](./gif/Salaire_Gouvernement_ProfEcoles_10.gif)

Voici la même chose où le salaire est montré en proportion du SMIC:

![](./gif/Ratio_Gouvernement_ProfEcoles_10.gif)

