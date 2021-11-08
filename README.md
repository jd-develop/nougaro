# Nougaro
 Un langage de programmation. Interpréteur écrit en Python.
 
 Pour l'instant, seul le shell fonctionne. Exécutez-le avec `python3 shell.py`.
 
 Minimum : python 3.9
 
 Prend en charge python 3.10 😁

## Syntaxe

### Opérateurs numériques
| Python    | Nougaro   | Remarques                       |
|-----------|-----------|---------------------------------|
| *         | *         | multiplication                  |
| /         | /         | division                        |
| +         | +         | addition                        |
| -         | -         | soustraction                    |
| **        | ^         | puissance                       |

### Tests
| Python    | Nougaro   | Remarques                       |
|-----------|-----------|---------------------------------|
| if        | if        | if <cond> then <expr>           |
| :         | then      | if <cond> then <expr>           |
| elif      | elif      | [if...] elif <cond> then <expr> |
| else      | else      | [if... (elif...)] else <expr>   |

### Opérateurs booléens et de tests
| Python    | Nougaro   | Remarques                       |
|-----------|-----------|---------------------------------|
| ==        | ==        | est égal à                      |
| !=        | !=        | est différent de                |
| <         | <         | strictement inférieur à         |
| <=        | <=        | inférieur ou égal à             |
| \>        | \>        | strictement supérieur à         |
| \>=       | \>=       | supérieur ou égal à             |

### Opérateurs et variables logiques
| Python    | Nougaro   | Remarques                       |
|-----------|-----------|---------------------------------|
| and       | and       | 'et' logique                    |
| or        | or        | 'ou' logique                    |
| ^         | exclor    | 'ou exclusif' logique           |
| not       | not       | 'non' logique (inverseur)       |
| True      | True      | 'vrai' logique, égal à 1        |
| False     | False     | 'faux' logique, égal à 0        |


### Variables :

Définition : `VAR nom = valeur`.

Définitions multiples avec une même valeur : `VAR nom = VAR nom1 = VAR nom2 = valeur`

Peut être utilisé dans les expressions mathématiques : `1 + (VAR a = 2)` renvoie 3


Accès aux variables : `nom`

Noms de variables protégées (constants) : `null`, `True`, `False`. Leurs valeurs sont respectivement 0, 1, 0

