
from PyQt5.QtCore import Qt,pyqtSignal,QRect
from PyQt5.QtWidgets import QMainWindow,QApplication,QMenu,QAction,QWidget,QPushButton,QHBoxLayout,QLineEdit,QDialog,QMessageBox,QLabel,QSplitter,QColorDialog,QTabWidget,QCheckBox
from PyQt5.QtGui import QPixmap,QPainter,QPen,QColor,QIcon,QPalette    
from collections import OrderedDict
import numpy as np
from itertools import islice
import random
import math
import time
import Classes
from Classes import *



#Fonctions diverses utilisées dans le main 

# Générateur de prénoms
def firstNameGenerator():
    """->str
    retourne un prénom aléatoire du fichier prenoms.txt contenant 2666 prénoms"""
    name="doc/prenoms.txt"
    file=open(name,"r", encoding="utf8")
    linenumber=2666
    for _ in range(0,np.random.randint(1, linenumber)):
        line=file.readline()
        words=line.split("\n")
    return words[0]

# Générateur de noms
def lastNameGenerator():
    """->str
    retourne un nom aléatoire du fichier noms.txt"""
    name="doc/noms.txt"
    file=open(name,"r", encoding="utf8")
    linenumber=6338
    for _ in range(0,np.random.randint(1, linenumber)):
        line=file.readline()
        words=line.split("\n")
    return words[0]


def rating(candidates, n=1):
    """Dict[int,Candidate] * Optional[int] -> Dict[int,Candidate]
    Classe les candidats par ordre décroissant des votes reçus"""
    score= { k : v.score for (k,v) in candidates.items() }
    sortedscore=(sorted(score.items(), key=lambda t: t[1]))
    if (n==1):
        sortedscore2=list(reversed(sortedscore))
    else :
        sortedscore2=list(sortedscore)
    c=candidates
    results= [(k[0],c[k[0]]) for k in sortedscore2]
    return OrderedDict(results)
            
def resetElections(candidates):
    """Dict[int,Candidate] * Dict[int,Voter] -> None
    Réinitialise les scores à 0 """
    for (_,c) in candidates.items():
        c.resetVote()
def distance(p1, p2):
    """Participant * Partcipant -> float
    Renvoie la distance entre deux Participants
    """
    return np.linalg.norm(np.array([p1.pos[0], p1.pos[1]]) - np.array([p2.pos[0], p2.pos[1]]))

def n_best_votes(candidates, voters, n=-1, dist=False):
    """Dict[int,Candidate] * Dict[int,Voter] * Optional[int] -> Optional[Dict[int,List[int]], Dict[int,Dict[int,float]]
    (Renvoie les n meilleurs candidats pour chaque votant
    Args:
        candidates (dict): dictionnaire de la forme : id_candidate : Candidate
        voters (dict): dictionnaire de la forme : id_voter : Voter
        n (int, optional): nombre de candidats à renvoyer. Defaults to -1, renvoie tous les candidats."""

    if n == -1:
        n = len(candidates)
    dico = dict()
    for (k1,v1) in voters.items():
        dico[k1] = {}
        # Calcul de la distance entre le votant et chaque candidat
        for (k2,v2) in candidates.items():
            dico[k1][k2] = distance(v1,v2)
    # Tri des candidats par distance
    #dictResults : Dict[int,Dict[int,float]]
    dictResults = {voter: {candidate: dico[voter][candidate] for candidate in sorted(dico[voter], key=dico[voter].get)[:n]} for voter in dico}
    if dist:
        return dictResults
    #results : Dict [int,List[int]]
    results = { idvoter : [k for k in v] for (idvoter,v) in dictResults.items() }
    return results

# Calcul des Scores 

def plurality(candidates, voters):
    """Dict[int,Candidate] * Dict[int,Voter] -> None
    Args:
        candidates (dict): dictionnaire de la forme : id_candidate : Candidate
        voters (dict): dictionnaire de la forme : id_voter : Voter
    """
    best = n_best_votes(candidates, voters, 1)
    for (voter,listCandidates) in best.items():
        (voters[voter]).voteFor(candidates[listCandidates[0]])

def borda(candidates, voters):
    """Dict[int,Candidate] * Dict[int,Voter] -> None
    effectue un vote de Borda 
    Args:
        candidates (dict): dictionnaire de la forme : id_candidate : Candidate
        voters (dict): dictionnaire de la forme : id_voter : Voter
    """
    best = n_best_votes(candidates, voters)
    for (voter,listCandidates) in best.items():
        for k in range(len(listCandidates)):
            (voters[voter]).voteFor(candidates[listCandidates[k]],(len(listCandidates)-1-k))
    
def veto(candidates, voters, n=1):
    """Dict[Candidate] * Dict[Voters] * Optional[int] -> None
    effectue un vote de Veto et renvoie le résultat
    chaque dernière place rapporte n point (positif si pas de n)
    Args:
        candidates (dict): dictionnaire de la forme : id_candidate : Candidate
        voters (dict): dictionnaire de la forme : id_voter : Voter
    """
    best = n_best_votes(candidates, voters)
    for (voter,listCandidates) in best.items():
        (voters[voter]).voteFor(candidates[listCandidates[len(listCandidates)-1]],n)

def approval(candidates, voters, n=1):
    """Dict[Candidate] * Dict[Voters] * Optional[int] -> None
    effectue un vote d'approbation 
    Chaque candidat au dessus de la nième place gagne un point positif
    /!\ n doit être inférieur au nombre de candidats
    /!\ n est par défaut à 1 <=> pluralité 

    Args:
        candidates (dict): dictionnaire de la forme : id_candidate : Candidate
        voters (dict): dictionnaire de la forme : id_voter : Voter
    """
    best = n_best_votes(candidates, voters, n)
    for (voter,listCandidates) in best.items():
        for c in listCandidates:
            (voters[voter]).voteFor(candidates[c])


#----------------- Méthodes de Condorcet -----------------#

def condorcet_duel(candidates:dict, voters:dict, id1:int, id2:int, score:bool=False):
    """Dict[Candidate] * Dict[Voters] * int * int * Optional[bool] -> Optional[Dict[int,int],int]
    Duel de Condorcet entre deux candidats, si le bool score est vraie alors renvoie un dictionnaire 
    avec l'id de chaque candidat etsinon renvoie l'id du candidat gagnant, -1 si égalité

    Args:
        voters (dict): Voter 
        candidats (dict): Candidate
        id1 (int): id du candidat 1
        id2 (int): id du candidat 2

    Returns:
        int: l'id du vainqueur, -1 si égalité
    """
    score_id1 = 0
    score_id2 = 0
    dictCandidates={id1:candidates[id1],id2:candidates[id2]}
    best = n_best_votes(dictCandidates,voters)
    for (_,v) in best.items():
        if v[0]==id1:
            score_id1+=1
        else:
            score_id2+=1
    if score:
        return {id1:score_id1, id2:score_id2}
    else:
        return id1 if score_id1 > score_id2 else -1 if score_id2 == score_id1 else id2

    
def copeland(candidates:dict, voters:dict):
    """Dict[int,Candidate] * Dict[int,Voter] -> None
    Méthode de Copeland
    Args:
        candidates (dict): candidats (déf dans main)
        voters (dict): votants (déf dans main)
    """
    for id1 in candidates:
        for id2 in candidates:
            if id1 != id2:
                res = condorcet_duel(candidates, voters, id1, id2)
                candidates[id1].score += 1 if res == id1 else 0 if res == id2 else 0.5


def simpson(candidates:dict,voters:dict):
    """Dict[int,Candidate] * Dict[int,Voter] -> None
    Méthode de Simpson
    Args:
        candidates (dict): candidats (déf dans main)
        voters (dict): votants (déf dans main)
    """
    #On initialise tous les scores aux nombre max de vote possible, pour pouvoir ensuite retenir le minimum
    for (_,v) in candidates.items():
        v.score=len(voters)

    for id1 in candidates:
        for id2 in candidates:
            if id1 != id2:
                res = condorcet_duel(candidates, voters, id1, id2, True)
                candidates[id1].score = min(candidates[id1].score, res[id1])    

#----------------- Méthodes à plusieurs tours -----------------#
#Pluralité à 2 tours

def maj2Turns(menu, candidates, voters):
    """Menu * Dict[int,Candidate] * Dict[int,Voter] -> None
    Effectue un vote majoritaire à 2 tours et affiche le résultat dans le menu"""
    plurality(candidates,voters)
    candidates=rating(candidates)
    tabs=QTabWidget()
    tabs.setTabBarAutoHide(True)
    menu.addnewTab(tabs,"Two-round Majority")
    tabFistRound=Classes.ViewResults(menu,candidates,width=5, height=4, dpi=100)
    tabs.addTab(tabFistRound,"First Round")
    _,c1=next(iter(candidates.items()))
    if(c1.score>len(voters)/2): #Si pas de Majorité absolue, on lance le second tout
        return None
    _,c2=list(islice(candidates.items(), 2))[1]
    menu.resetScores()
    finalecandidates={c1.id:c1,c2.id:c2}
    plurality(finalecandidates,voters)
    finalecandidates=rating(finalecandidates)
    tabSecondRound=Classes.ViewResults(menu,finalecandidates,width=5, height=4, dpi=100)
    tabs.addTab(tabSecondRound,"Second Round")
    tabs.setCurrentWidget(tabSecondRound)

#Vote alternatif (pluralité par éliminations successives)
def av(menu, tab, candidates, voters, n=1):
    """Menu * QTabWidget * Dict[int,Candidate] * Dict[int,Voters] * Optional[int] -> None
    Fonction récursive, effectue un vote alternatifet et affiche le résultat dans le menu"
    (correspond à une méthode de Harre, ici car les différents tours sont directement générés)
    Args:
        candidates (dict): dictionnaire de la forme : id_candidate : Candidate
        voters (dict): dictionnaire de la forme : id_voter : Voter
    """
    plurality(candidates,voters)
    candidates=rating(candidates)

    newtab=Classes.ViewResults(menu,candidates,width=5, height=4, dpi=100)
    tab.addTab(newtab,"Round "+str(n))
    _,c1=next(iter(candidates.items()))
    if((c1.score>len(voters)/2) or len(candidates)==2): #Si pas de Majorité absolue, on lance un autre tour
        tab.setCurrentWidget(newtab)
        return c1
    remainingcandidates=remaining(candidates,voters)
    resetElections(candidates)
    av(menu,tab,remainingcandidates,voters,n+1)

def remaining(candidates, voters):
    """Dict[Candidate] * Dict[Voters] -> Dict[int,Candidate]
    retourne les candidats en enlevant celui ou ceux avec le nombre de vote le plus faible,
    """
    score=len(voters)*len(candidates)
    eliminated=set()
    for (_,c) in candidates.items():
        if c.score==score:
            eliminated.add(c.id)
        elif c.score<score:
            score=c.score
            eliminated={c.id}
    s={id:c for (id,c) in candidates.items() if not(id in eliminated)}
    return s

def remainingHigt(candidates):
    """Dict[int,Candidate] -> Dict[int,Candidate]
    retourne les candidats en enlevant celui ou ceux avec le nombre de vote le plus élevé
    """
    score=0
    eliminated=set()
    for (_,c) in candidates.items():
        if c.score==score:
            eliminated.add(c.id)
        elif c.score>score:
            score=c.score
            eliminated={c.id}
    s={id:c for (id,c) in candidates.items() if not(id in eliminated)}
    return s

#Méthode de Nanson (borda par éliminations successives)

def nanson(main,tab,candidates, voters, n=1):
    """Menu * QTabWidget * Dict[int,Candidate] * Dict[int,Voters] * Optional[int] -> None
    Fonction récursive, effectue un vote avec la méthode de Nanson (aussi appelée méthode de Borda par éliminations
    successives) et affiche le résultat dans le menu
    Args:
        candidates (dict): dictionnaire de la forme : id_candidate : Candidate
        voters (dict): dictionnaire de la forme : id_voter : Voter
    """
    borda(candidates,voters)
    candidates=rating(candidates)
    newtab=Classes.ViewResults(main,candidates,width=5, height=4, dpi=100)
    tab.addTab(newtab,"Round "+str(n))
    _,c1=next(iter(candidates.items()))
    if(c1.score>((len(candidates)-1)*(len(voters)/2)+((len(candidates)-2)*(len(voters)/2))) or len(candidates) == 2): #Si pas de Majorité absolue, on lance un autre tour
        tab.setCurrentWidget(newtab)
        return c1
    remainingcandidates=remaining(candidates,voters)
    resetElections(candidates)
    nanson(main,tab,remainingcandidates,voters,n+1)

#Méthode de Coombs (Elimination succesive on ou enleve le projet qui a le plus de derniere places)
def coombs(main,tab,candidates, voters, n=1):
    """Menu * QTabWidget * Dict[int,Candidate] * Dict[int,Voters] * Optional[int] -> None
    Fonction récursive, effectue un vote avec la méthode de combs (on élimine celui avec le plus de dernière place) 
    et affiche le résultat dans le menu
    Args:
        candidates (dict): dictionnaire de la forme : id_candidate : Candidate
        voters (dict): dictionnaire de la forme : id_voter : Voter
    """
    veto(candidates, voters)
    candidates=rating(candidates,n=-1)

    newtab=Classes.ViewResults(main,candidates,width=5, height=4, dpi=100)
    tab.addTab(newtab,"Round "+str(n))
    _,c1=next(iter(candidates.items()))
    if(len(candidates)<=2): #Si majoritté absolue on renvoie l'id du candidat
        tab.setCurrentWidget(newtab)
        main.winners={c1.id}
        return None
    #Si pas de Majorité absolue, on lance un autre tour
    remainingcandidates=remainingHigt(candidates)
    resetElections(candidates)
    coombs(main,tab,remainingcandidates,voters,n+1)

#Fonctions pour la répartition et les déplacements

def goodPosition(x,y=0):
    """int x Optional[int] -> bool
    retourne True si la/les entiers en paramètres sont compris entre -400 et 400, False sinon
    """
    return ((x>=-400) and (x<=400)) and ((y>=-400) and (y<=400))

def gaussienne(n=0,e=100):
    """retourne un entier compris entre -400 et 400 choisit aléatoirement, avec une loi de Gauss 
    (centré sur n avec un écart type égale à 100) """
    i=-401
    while not goodPosition(i):
        i=random.gauss(n,e)
    return i

def somme(liste):
    _somme = 0
    for i in liste:
        _somme = _somme + i
    return _somme   

def r2017():
    tab=[24.21,21.31,19.98,19.58,6.36,4.70,1.21,1.09,0.92,0.64,0.18]
    i=random.random()
    e=42
    if i<somme(tab[:1])/100:
        x=random.gauss(214,e)
        y=random.gauss(199,e)
    elif i<somme(tab[:2])/100:
        x=random.gauss(-87,e)
        y=random.gauss(-246,e)
    elif i<somme(tab[:3])/100:
        x=random.gauss(366,e)
        y=random.gauss(-141,e)
    elif i<somme(tab[:4])/100:
        x=random.gauss(-324,e)
        y=random.gauss(63,e)
    elif i<somme(tab[:5])/100:
        x=random.gauss(-184,e)
        y=random.gauss(336,e)
    elif i<somme(tab[:6])/100:
        x=random.gauss(-15,e)
        y=random.gauss(-288,e)
    elif i<somme(tab[:7])/100:
        x=random.gauss(-231,e)
        y=random.gauss(-136,e)
    elif i<somme(tab[:8])/100:
        x=random.gauss(-336,e)
        y=random.gauss(280,e)
    elif i<somme(tab[:9])/100:
        x=random.gauss(-215,e)
        y=random.gauss(-190,e)
    elif i<somme(tab[:10])/100:
        x=random.gauss(-330,e)
        y=random.gauss(169,e)
    else :
        x=random.gauss(-180,e)
        y=random.gauss(-150,e)

    return (x,y)

#Fonction pour le Lobbying
def pos_r_set(h, k, r, show=False, menu=None):
    """int * int * int * Optional[bool] * Optional[Menu] -> Set[Tuple[int,int]]
    retourne l'ensemble des positions des points sur le cercle de centre (h,k), de rayon r
    et si show alors affiche ces points dans le menu
    """
    s=set()
    for y in range(max((k-r),-400),min((k+r+1),400)):
        rac=r*r-(y-k)*(y-k)
        if rac>=0:
            x1=round(math.sqrt(rac)+h)
            x2=round(-math.sqrt(rac)+h)
            if(goodPosition(x1)):
                s.add((x1,y))
            if(goodPosition(x2)):
                s.add((x2,y))
    for x in range(max((h-r),-400),min((h+r+1),400)):
        rac=r*r-(x-h)*(x-h)
        if rac>=0:
            y1=round(math.sqrt(rac)+k)
            y2=round(-math.sqrt(rac)+k)
            if(goodPosition(y1)):
                s.add((x,y1))
            if(goodPosition(y2)):
                s.add((x,y2))
    
    #Pour afficher ses points
    if show:
        for x,y in s:
            menu.image.drawEllipse(x,y,"black",1)
    return s
    
def winners(candidates:dict,n=1):
    """Dict[int:Candidate] * Optional[int]->Set[Candidate]
    retourne l'ensemble des ids des candidats ayant le score le plus élevé (ou le plus faible si n=-1)"""
    _,c1=next(iter(candidates.items()))
    score=c1.score
    winners=set()
    for (_,c) in candidates.items() :
        if c.score==score:
            winners.add(c.id)
        elif n==1 and c.score>score :
            score=c.score
            winners={c.id}
        elif n==-1 and c.score<score :
            score=c.score
            winners={c.id} 
    return winners

def testposition(candidates, voters, id):
    """Dict[int,Candidate] * Dict[int,Voter] * int -> int
    Renvoie le score que le candidat d'id id aurait comme score avec un vote plural
    Args:
    candidates (dict): dictionnaire de la forme : id_candidate : Candidate
    voters (dict): dictionnaire de la forme : id_voter : Voter
    id (int): id du candidat à renvoyer
    """
    best = n_best_votes(candidates, voters, 1)
    score=0
    for (_,listCandidates) in best.items():
        if listCandidates[0]==id:
            score+=1
    return score

## Sprint 04/04
def getSumScores(self,candidates:dict):
        somme_scores=0
        for _,c in self.dictcandidates.items():
            somme_scores+=c.score
        return somme_scores

def delegate(candidates:dict, voters:dict, distanceMin=200, prob=1, nbtours=5):
    """Effectue la délégation des votes
    Args :
        distanceMin :  distance à partir de laquelle un votant considère déléguer son vote
        prob : proba de déléguer son vote
        nbtours : nombre de tours à effectuer avant le vote"""
    for n in range(nbtours):
        print("Turn {}\n".format(n+1))
        best_distances=n_best_votes(candidates, voters, n=1, dist=True)
        for (_,v) in voters.items():
            if v.weight>0: #On vérifie que le votant n'a pas déjà délégué
                dist=best_distances[v.id][(next(iter(best_distances[v.id])))]
                if dist<distanceMin and random.random()<=prob:
                    #v2 votant à qui déléguer
                    id=whotodelegateto(v, voters) 
                    if id > 0:
                        v2=voters[id]
                        print("Poid des votants")
                        print("{} : {} et {} : {}".format(v.firstName,v.weight,v2.firstName,v2.weight))
                        print("{} Délégue à {}".format(v.firstName,v2.firstName))
                        v.delegate(v2)
                        print("{} : {} et {} : {}\n".format(v.firstName,v.weight,v2.firstName,v2.weight))

def pluralityWithWeight(candidates,voters):
    """Dict[int,Candidate] * Dict[int,Voter] -> None
    Effectue un vote plural en tenant compte du poid de vote des votants
    Args:
        candidates (dict): dictionnaire de la forme : id_candidate : Candidate
        voters (dict): dictionnaire de la forme : id_voter : Voter
    """
    best = n_best_votes(candidates, voters, 1)
    for (voter,listCandidates) in best.items():
        (voters[voter]).voteFor(candidates[listCandidates[0]],voters[voter].weight)

def whotodelegateto(voter, voters):
    """Voter * Dict[int,Voter] * Optional[int] -> int
    Renvoie le votant les plus proche du votant, n'ayant pas délégué son vote
    Args:
        voter : Voter
        voters (dict): dictionnaire de la forme : id_voter : Voter
        n (int, optional): nombre de candidats à renvoyer. Defaults to -1, renvoie tous les votants."""


    dico=dict()
    # Calcul de la distance entre le votant et chaque voter
    for (k,v) in voters.items():
        if v!=voter:
            if v.weight!=0: #Si ce votant n'a pas déjà délégué alors on peut lui déléguer son/ses vote(s)
                dico[k] = distance(voter,v)
    if len(dico)==0:
        return 0
    #Dictionnaire des votants n'ayant pas délégué trié par distance avec le votant croissante
    sorteddistance=OrderedDict((sorted(dico.items(), key=lambda t: t[1])))
    #On renvoie le premier élement de ce dictionnaire (s'il existe)
    s = next(iter(sorteddistance.items()))
    return s[0]
    
    
