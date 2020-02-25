#!/usr/bin/python
# coding:utf-8


from SimulateurCarriere import *
from AnalyseCarriere import *
from tools import *
import matplotlib.pyplot as plt



def genere_anim( carrieres,  plot_retraite=0, filename="", dir="./", ):

    tmp_dir = "./tmp/"

    # calcul des limites de l'abscisse
    a1 = carrieres[0].annee_debut
    c = carrieres[-1]
    if plot_retraite==0:
        a2 = c.annee_debut + c.age_max - c.age_debut
    else:
        a2 = c.annee_debut + c.age_mort - c.age_debut
    
    for i in range(len(carrieres)):

        c=carrieres[i]
        m=c.m

        print(c.annee_debut)
        
        fig = plt.figure( figsize=(7, 5) )
        plt.xlim( (a1, a2) )
        ax = fig.add_subplot(111)
                
        AnalyseCarriere(c).plot_evolution_carriere_corr(ax, m.smic, i, carrieres, a2, "Ratio revenu/SMIC", 1, plot_retraite)
        if filename!="":
            plt.savefig(tmp_dir+"ratio_"+filename+"_%d.png"%c.annee_debut)
                
        fig = plt.figure( figsize=(7, 5) )
        plt.xlim( (a1, a2) )
        ax = fig.add_subplot(111)
        AnalyseCarriere(c).plot_evolution_carriere_corr(ax, m.corr_prix_annee_ref, i, carrieres, a2, "Euros constants (2019)", 12, plot_retraite)
        if filename!="":
            plt.savefig(tmp_dir+"salaire_"+filename+"_%d.png"%c.annee_debut)
                    
    if filename!="":    
        print "Génération de l'image animée ratio_"+filename+".gif"
        shell_command( "convert -delay 200 -loop 0 "+tmp_dir+"ratio_"+filename+"*.png "+dir+"ratio_"+filename+".gif" )
        shell_command( "rm "+tmp_dir+"ratio_"+filename+"*.png" )
        
        print "Génération de l'image animée salaire_"+filename+".gif"
        shell_command( "convert -delay 200 -loop 0 "+tmp_dir+"salaire_"+filename+"*.png "+dir+"salaire_"+filename+".gif" )
        shell_command( "rm "+tmp_dir+"salaire_"+filename+"*.png" )
            
        plt.close('all')




# pour les images (type de fichier)

ext_images = "png"

def plot_comparaison_modeles(lm, a,b, filename=""):

    plt.figure(figsize=(10,8))
    AnalyseModele.plot_modeles(lm,[a,b])
    if filename!="":
        plt.savefig(filename)
        plt.close('all')


# sur les carrières
    

def debug0():

    print "Details carrière et retraite pour deux professions"
    
    c=CarrierePublic(m1,22,2020,"ProfEcoles",0.08)
    
    a=AnalyseCarriere(c)
    a.affiche_carriere()


            
def simu0():

    print "Génération de la comparaison des modèles macro de prédiction"
    plot_comparaison_modeles([m1,m2],debut,fin,"./gouv_vs_dest.png")  
    
    print "Génération des grilles indiciaires"

    m=m1
    dir="./fig/grilles/"
    
    for id_metier, _, age in cas:

        plt.figure()
        filename = "grille_%s.%s"%( id_metier, ext_images)
        print "Génération du fichier",filename
        c = CarrierePublic(m, age, 2019, id_metier, 0.0)
        a = AnalyseCarriere(c)
        a.plot_grille()
        if dir!="":
            plt.savefig(filename)
            plt.close('all')
    

 
    
def simu1():
    
    print "Génération d'animations gif sur l'évolution de carrières dans le public"
    
    for m in [m1,m2]:
        for id_metier, prime, age in cas:
            filename="%s_%s_%d"%(m.id_modele, id_metier, int(prime*100))
            print(filename)
            carrieres = [CarrierePublic(m, age, annee, id_metier, prime) for annee in range(1980,2041,5)]
            genere_anim( carrieres, 1, filename, "./fig/salaires_retraites/" )
            genere_anim( carrieres, 0, filename, "./fig/salaires/")


    
def simu2():

    for m in [m1,m2]:
        carrieres = [ CarrierePrive(m1, 22, annee,"Privé") for annee in range(1980,2041,5) ]
        print "Génération d'animations gif sur l'évolution de carrières dans le privé"
        filename="%s_%s"%(m.id_modele, carrieres[0].nom_metier)
        print(filename)
        genere_anim( carrieres, 1, filename, "./fig/salaires_retraites/" )
        genere_anim( carrieres, 0, filename, "./fig/salaires/")



def simu3():

    dir = "./articles/1/"
       
    id_metier = "ProfEcoles"
    prime = 0.08
    age = 22
    
    m = m1

    c = CarrierePublic(m1, 22, 2020, id_metier, prime)
    AnalyseCarriere(c).plot_grille_prime()
    plt.savefig(dir+"grille.png")
    
    fig=plt.figure()
    plt.xlim( (2020,2070) )
    ax = fig.add_subplot(111)
    AnalyseCarriere(c).plot_evolution_carriere_corr(ax, m.prix, 0, [c], "Euros constants (2019)", 12)
    plt.savefig(dir+"salaireEC.png")
    
    fig=plt.figure()
    plt.xlim( (2020,2070) )
    ax = fig.add_subplot(111)
    AnalyseCarriere(c).plot_evolution_carriere_corr(ax, m.smpt, 0, [c], "Ratio revenu/SMPT", 1)
    plt.savefig(dir+"salaireRel.png")
    
    # animations
    filename="%s_%s_%d"%(m.id_modele, id_metier, int(prime*100))
    print(filename)
    carrieres = [CarrierePublic(m, age, annee, id_metier, prime) for annee in range(1980,2041,5)]
    genere_anim( carrieres, 1, filename, dir )
    shell_command("mv "+dir+"ratio_gouv_"+id_metier+"_%d"%(prime*100)+".gif "+dir+"selonannee.gif")
    genere_anim( carrieres, 0, filename, dir )
    shell_command("mv "+dir+"ratio_gouv_"+id_metier+"_%d"%(prime*100)+".gif "+dir+"selonannee_retraite.gif")


      

####################################################
# Partie principale
####################################################


####
# Modèles de projection

debut, fin = 1980, 2140

m1 = ModeleGouv(debut,fin, 1.3, False)
m2 = ModeleGouv(debut,fin, 1.3, True)



# Carrières considérées

cas = [ ("ProfEcoles",0.081,23), ("ProfCertifie",0.096,23), ("PR",0.071,32), ("ATSEM",0.16,22), ("MCF",0.034,29), ("CR",0.034,29), ("DR",0.071,32), ("Infirmier",0.299,22), ("AideSoignant",0.242,22), ("Redacteur",0.281,22), ("BIATSS",0.1,22), ("SecretaireAdmin",0.27,22), ("TechHosp",0.27,22), ("AdjTech", 0.18,22), ("Magistrat", 0.35,25), ("ProfAgrege",0.09,23) ]

cas = [ ("ProfEcoles",0.081,23) ]

### Génération d'un exemple

debug0()

### Génération comparaison des grilles
    
simu0()

### Génération comparaison modèles et infographies

simu1()

###

simu2()

###

simu3()


