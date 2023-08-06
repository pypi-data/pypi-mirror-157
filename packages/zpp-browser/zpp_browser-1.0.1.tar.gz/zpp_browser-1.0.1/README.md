# zpp-browser
## Informations
Librairie pour l'utilisateur d'un explorateur de fichier en cli pour la sélection d'un fichier

### Prérequis
- Python 3
<br>

# Installation
```console
pip install zpp_browser
```

# Utilisation
### Conseil d'importation du module
```python
from zpp_browser import Browser
```

<br>

### Initialisaton du browser
```python
c = Browser("Chemin_de_depart")
```
>En paramètre supplémentaire, nous pouvons mettre:<br/>
>- Filter: Permet de filtrer sur une liste d'extension de fichier. (Par défaut: ne filtre pas)
>- ShowHidden: Afficher les fichiers et dossiers cachés. True ou False  (Par défaut: True)
>- ShowDir: Afficher les dossiers. True ou False  (Par défaut: True)
>- ShowFirst: Choisir si on souhaite afficher les dossiers ou les fichiers en premier. dir, file ou None (Par défaut: dir)
>- Color: Permet de configurer la colorisation des fichiers en fonction de l'extensions (Voir annexe pour la configuration)
>- Pointer: Choisir un pointer custom (Par défaut: " >")
>- Padding: Choisir la taille de la marge à gauche (Par defaut: 2)

### Configuration des couleurs

Il est possible d'envoyer à la fonction une liste de couleur pour permettre de customiser l'affichage des fichiers en fonction de leur extension.
Pour cela, la fonction attends une liste à 2 dimensions contenant [extension, couleur du texte, couleur de fond]
<br>

Pour l'extension il suffit de mettre le nom. 
Par exemple, .txt pour les fichiers txt
Cas particulier pour la configuration de certains éléments:
- \_\_default__: Pour la couleur par défaut
- \_\_hidden__: Pour les fichiers et dossiers cachés
- \_\_dir__: Pour les dossiers
- \_\_selected__: Pour l'élément sélectionné

Dans le cas où on veut configurer plusieurs extensions avec la même couleur, il suffit de mettre une virgule entre le nom des extensions.
Exemple:
```python
['.crt,.pfx,.key,.txt','yellow','black']
```

#### Exemple de liste de couleur
```python
[['__default__','white','black'],['__hidden__','red','black'],['__selected__','red','black'],['__dir__','green','black'],['.crt,.pfx,.key,.txt','yellow','black']]
```