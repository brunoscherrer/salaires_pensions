# Simulation autonome de cas-types (revenus et retraites par points)

Ce projet permet de générer des simulations (sous forme de graphes synthétiques et de tableaux) de l'évolution de la carrière et des possibles retraites (dans un système à points) pour
plusieurs métiers de la fonction publique et trajectoires du privé. Il permet également de générer des documents synthétiques compilant toutes ces informations.

Nous considérons 3 cadres macro-économiques :

- un modèle truqué (âge-pivot bloqué), qui se veut aussi près que possible de celui utilisé par le gouvernement Philippe pour la génération de ses cas-types ;
- une version corrigée (âge pivot glissant) du modèle du gouvernement Philippe, ce qui permet de quantifier le trucage ;
- un modèle indépendant, issu du simulateur Destinie2, également utilisé pour étudier les retraites par le COR (Conseil d'Orientation des Retraites), évidemment sans trucage (âge pivot glissant) ; par rapport aux deux précédents modèles, ce dernier a pour principale différence de prévoir une revalorisation sérieuse de la fonction publique (via une indexation du point d'indice proche de l'évolution de salaire moyen et un taux de prime fixe).

De ces simulations, on peut tirer les enseignements suivants :

- **Le trucage des simulations diffusées par le gouvernement Philippe est significatif sur le niveau des pensions, entre 10 et 20% selon les générations**.
- **Pour la fonction publique** :
  - Pour les deux premiers modèles qui se basent sur des projections régressives des salaires dans la fonction publique (décrochage de 1.3% par an par rapport au SMIC), **on observe au cours du temps une smicardisation de l'ensemble des salaires qui induit une retraite minimum pour les fonctionnaires en bas et en milieu de l'échelle (catégories C, mais aussi B)**.
  - Dans le dernier modèle qui est moins régressif sur la rémunération dans le public, **le système de retraites par points fait que le taux de remplacement est d'autant plus faible que la carrière est revalorisée** c'est-à-dire recouvre le profil croissant (voulu par les grilles indiciaires). Par exemple, la revalorisation d'un professeur certifié de la génération 2003 fait baisser son taux de remplacement brut jusqu'à environ 37% s'il part à 62 ans, 47% s'il part à 65 ans, et 55% même s'il part à 67 ans.
- **Dans le privé** (situation pour laquelle les deux derniers modèles sont très proches) :
  - **La retraite par points est anti-redistributive** : pour des rémunérations évoluant au cours de la carrière entre i× SMIC et (i + 1)× SMIC, **on observe que le taux de remplacement est d'autant plus grand que le salaire est élevé** (que i est grand). Le meilleur taux de remplacement (et donc le meilleur rendement du système) est notamment obtenu pour les salariés étant toute leur vie au plafond (10 SMIC). 
- Globalement, le choix d'une indexation des retraites sur l'indice des prix fait chuter le revenu des retraités par rapport au SMIC, entraînant ceux qui sont partis avec les retraites les plus faibles vers la pauvreté. En particulier, **au cours de leur vieillesse, beaucoup de retraités se retrouvent très en dessous du seuil "85% du SMIC", même s'ils ont effectué une "carrière complète"**.

