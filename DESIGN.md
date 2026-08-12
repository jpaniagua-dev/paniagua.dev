# paniagua.dev — direction de conception

Version 3, 2026-08-12. Le site parle désormais au nom de l'entreprise, sur un substrat
sombre, et se parcourt par le défilement.

## Ce qui a changé, et pourquoi

**Version 1**, rejetée : elle avait la forme d'une page vitrine générée par défaut, et
changer la palette ne déguise pas ce squelette.

**Version 2**, fiche technique imprimée sur papier clair. La grammaire tenait, mais le site
restait centré sur la personne et le substrat clair combattait le portrait.

**Version 3** : la marque passe devant la personne, le substrat devient noir, et le
défilement devient la navigation.

## Contraintes du brief

1. Centré sur **Paniagua.dev, entreprise individuelle** au sens du régime genevois, tout en
   parlant de Julio.
2. Thème noir plus obscur, choisi pour respecter le portrait en clair-obscur.
3. Une expérience au défilement, dans l'esprit de `visit.withgoogle.com` et
   `antigravity.google`.
4. Marque concentrée sur la conception Web.
5. **Aucun texte nouveau.** Tout vient du site en ligne.
6. **Le site est bilingue**, anglais à la racine et français sous `/fr/`, alors que la
   référence publiée est majoritairement en français.

Les contraintes 5 et 6 se contredisent en apparence : traduire, c'est produire des chaînes
absentes de la référence. Le registre de provenance les réconcilie. `src/data/content.ts`
tient un dictionnaire `derivedFrom` où chaque chaîne pointe vers la chaîne publiée dont elle
vient, par traduction ou par recomposition, et `npm run check:content` exige que **chaque
source figure encore sur la page publiée**. Une chaîne sans source et absente de la référence
fait échouer le contrôle.

La colonne française de `content.ts` est le texte publié, mot pour mot. C'est elle la source ;
l'anglais en est la traduction.

Bilan actuel : **21 chaînes dérivées, 6 ajouts** marqués `ADDED`, soit trois notions dans les
deux langues (« Entreprise individuelle », « Genève », et le lien d'évitement, qui n'existe
pas sur le site publié). Les emoji d'origine ont été retirés, jamais remplacés.

## Bilinguisme

| | |
|---|---|
| `/` | Anglais, `og:locale` `en_GB` |
| `/fr/` | Français, `og:locale` `fr_CH` |

Les deux pages se déclarent mutuellement en `hreflang`, plus un `x-default` sur la racine, et
le plan de site porte les mêmes alternances. Un prospect genevois qui cherche en français
tombe sur `/fr/`, un lecteur international sur `/`.

Le sélecteur est **un lien réel vers l'autre page**, pas un script : il fonctionne sans
JavaScript et un moteur de recherche le suit.

`src/components/Page.astro` porte la structure entière et les deux routes ne diffèrent que
par une propriété `lang`. Une modification de structure ne peut donc pas diverger entre les
deux langues.

Le contrôle lit aussi le contenu publié **dans les attributs** : les cibles `mailto:` et la
balise `<meta name="description">`, qui n'apparaît jamais comme texte visible.

L'ordre des six domaines a été changé pour ouvrir sur `UI/UX Prototyping`, dont la
description commence par « Conception d'interfaces », là où le brief demande de concentrer
la marque.

## Substrat

Un seul, et il est sombre. Le portrait est un clair-obscur dont les noirs sont écrasés : sur
une page claire il combat la mise en page, sur celle-ci il s'y fond et seul le visage porte
la lumière.

**Le portrait est la photographie réelle, pas une trame.** La version tramée à un bit avait
été conçue pour du papier clair ; sur fond noir elle ressortait délavée et illisible.
`tools/grade-portrait.py` cale désormais le fond du studio exactement sur `#050506` : le
cadre disparaît et le sujet émerge de l'obscurité. Le contraste est appliqué **avant** le
calage, l'ordre inverse remontant le plancher et faisant réapparaître un bord gris.

| Rôle | Valeur | Contraste mesuré sur `#050506` |
|------|--------|-------------------------------|
| Fond | `#050506` | |
| Encre | `#F2F1ED` | **18,0:1** |
| Secondaire | `#8B8B85` | **6,0:1** |
| Rouge | `#FF3B21` | **5,7:1** |

Aucun angle arrondi, aucune ombre, aucun dégradé.

## Typographie

Switzer 900 pour la marque et les titres, JetBrains Mono 400 pour tout le reste. Pas de
troisième graisse.

**Interligne d'affichage à 0,92, jamais moins.** En dessous, l'accent d'une capitale
française heurte la ligne précédente : « À GENÈVE » et « INGÉNIERIE DE PRÉCISION » étaient
rognés à 0,82. C'est un défaut invisible pour un œil anglophone et impardonnable ici.

## Chorégraphie du défilement

Entièrement en CSS, via les animations pilotées par le défilement (`animation-timeline`).
Aucun écouteur d'événement, aucun `IntersectionObserver`, aucune bibliothèque : le
compositeur exécute tout hors du fil principal, et **la page expédie toujours zéro kilooctet
de JavaScript**.

| Classe | Effet |
|--------|-------|
| `.rise` | Le contenu monte en entrant, décalé par `.rise-2/3/4` |
| `.settle-type` | Un titre arrive d'en dessous, légèrement réduit, et se pose |
| `.row-in` | Une ligne entre par la gauche ; les six domaines cascadent |
| `.word-in` | Chaque mot d'une phrase sur sa propre chronologie |
| `.swell` | L'adresse de contact grandit à l'approche |
| `.parallax` | La planche se découvre puis dérive à contre-défilement |
| `.draw` | Un filet se trace sur la largeur |
| `.dim-out` | Un contenu s'atténue en sortant |
| `.progress` | Barre de progression liée au défilement du document |
| `.marquee-scroll` | Le bandeau avance avec le lecteur, pas sur minuterie |

Tout est déclaré dans `@supports (animation-timeline: view())` : un navigateur sans
chronologie de défilement affiche l'état final au lieu d'une page vide.
`prefers-reduced-motion` coupe l'ensemble.

## Scènes

Ouverture · Domaines d'intervention · Expertise technique · Contact.

Les scènes « Marque » et « Positionnement » ont été supprimées, leur contenu étant jugé
superflu. La scène d'ouverture porte désormais **la marque, pas le nom** : « Paniagua.dev »
en deux lignes avec l'extension en rouge, suivi de la mention d'entreprise individuelle.
Le nom de Julio ne subsiste que dans la mention de droits et le texte alternatif du portrait.

**Sur mobile, le texte précède la photographie dans le DOM.** L'ordre inverse remplissait le
premier écran avec le portrait, et un visiteur devait faire défiler avant de savoir de quoi
le site parlait. La grille remet la photographie à gauche à partir de `md`, et sa hauteur est
plafonnée à `58vh` en dessous.

La scène « Domaines » emprunte le dispositif d'`antigravity.google` : le titre se fige à
gauche pendant que les six domaines défilent à droite. La scène « La personne » fait saigner
la planche jusqu'au bord gauche du viewport.

**Aucune animation d'entrée dans une colonne collante.** Un élément en `position: sticky`
calcule sa propre chronologie contre sa position figée : il n'atteint jamais la fin de sa
plage et reste à moitié transparent en permanence.

## Mesures

`tools/measure-page.py`, contre une construction fraîche.

| | |
|---|---|
| Premier chargement | **55 Ko** |
| JavaScript | **0 Ko** |
| Requêtes tierces | **0** |

La photographie réelle pèse 23,6 Ko en WebP contre 15 Ko pour la trame qu'elle remplace.
Échange assumé : la trame ne se lisait pas.

## Vérification

`npm run verify` construit puis enchaîne trois contrôles bloquants :

- **glyphes** : échoue si un caractère manque dans les polices réduites, ou si un cadratin
  apparaît. A déjà rattrapé le `©` absent de la mention de droits.
- **contenu** : échoue si une chaîne ne vient pas du site publié.
- **débordement** : échoue si un élément dépasse horizontalement, à 390, 768, 1024, 1440 et
  1920 px. A déjà rattrapé la marque qui débordait et le titre collant qui chevauchait les
  services.
- **animation** : échoue si un élément animé n'a **aucune animation liée au défilement**, ou
  s'il reste transparent au centre du viewport. Ce contrôle a révélé que toute la
  chorégraphie était morte (voir ci-dessous), ce qu'une capture ne peut pas montrer.

## Le piège du minifieur CSS

Lightning CSS replie `animation-timeline` dans le raccourci `animation` et produit
`animation: linear both rise view()`. Chrome rejette entièrement cette déclaration, ce qui
**tue silencieusement toutes les animations de défilement** : la page reste correcte et
parfaitement immobile.

Correctif dans `astro.config.mjs` : `vite.build.cssMinify: 'esbuild'`, dont le minifieur ne
replie pas ces propriétés.

Second piège du même ordre : la classe `.grow` entrait en collision avec l'utilitaire
Tailwind homonyme. Renommée `.swell`.

### Le cœur du pied de page

« Made with ♥ by paniagua.dev » reprend la ligne du site publié, emoji en moins. Ni Switzer
ni JetBrains Mono ne portent de glyphe cœur, et Google Fonts ne le sert pas non plus pour
cette famille : le cœur est donc un tracé SVG unique, forme empruntée à Material Symbols
(Apache 2.0). Installer une bibliothèque d'icônes pour un seul glyphe coûterait plus que la
feuille de style entière. Il porte `role="img"` et `aria-label="love"`, de sorte qu'un lecteur
d'écran annonce la phrase complète.

## Déploiement continu

`.github/workflows/deploy.yml` construit, vérifie et publie à chaque poussée sur `main`.
Rien n'est publié si l'un des cinq contrôles échoue.

**Le workflow réutilise `deploy.py`, pas une action FTP du marché.** Une action tierce
recevrait le mot de passe FTP, c'est-à-dire un accès en écriture complet au site : une
dépendance de chaîne d'approvisionnement dont ce dépôt n'a pas besoin pour une boucle
d'envoi. Accessoirement, CI emprunte alors exactement le même chemin de code qu'un envoi
manuel, et refuse comme lui de retomber sur du FTP en clair.

Les secrets attendus dans le dépôt GitHub sont préfixés par projet, le compte en hébergeant
plusieurs : `FTP_HOST_PANIAGUA_DEV`, `FTP_USER_PANIAGUA_DEV`, `FTP_PASS_PANIAGUA_DEV`, et
`FTP_DIR_PANIAGUA_DEV` si le dossier distant n'est pas la racine. Le workflow les remappe
vers les noms simples que `deploy.py` attend ; la correspondance vit à un seul endroit. `tools/set-ci-secrets.sh` les recopie
depuis `pass` en les passant par l'entrée standard, jamais en argument de commande. Julio
le lance lui-même : il faut une passphrase GPG et une session `gh`.

**Le chemin de publication est testé de bout en bout.** `npm run test:deploy` monte un vrai
serveur FTPS sur la boucle locale, avec certificat auto-signé jetable, et fait tourner
`deploy.py` dessus sans le modifier : poignée de main TLS, création des dossiers distants,
envoi des seize fichiers, contrôle des tailles, et signalement des orphelins. Le test tourne
en CI juste avant la publication.

Le serveur tourne dans un **processus séparé**, pas un fil d'exécution. `pyftpdlib`
implémente `CWD` par un `os.chdir`, qui vaut pour tout le processus : dans le même, le
serveur déplace le répertoire courant sous les pieds du client entre deux envois, et un
fichier présent devient introuvable au hasard. Un déploiement réel parle à une autre
machine, le harnais doit reproduire cette séparation.

`deploy.py` ne dépend plus du répertoire courant du tout : `dist/` est résolu par rapport au
fichier lui-même et les fichiers sont ouverts en chemin absolu. Le script publie donc le
même arbre d'où qu'on l'appelle.

Il existe parce que deux bugs ont atteint la production dans ce chemin, tous deux invisibles
en local faute qu'une connexion réelle soit jamais ouverte : l'envoi en FTP non chiffré, puis
la lecture de `FTP_TLS.ssl_version`, propriété supprimée dans Python 3.12, juste après une
poignée de main parfaitement réussie. Vérifié : le test échoue si l'un de ces bugs est
réintroduit.

**`deploy.py` ne supprime rien à distance.** Un effacement distant piloté par CI est la
façon dont un site perd un fichier que personne ne voulait toucher. En revanche il **nomme**
désormais les fichiers présents sur le serveur qu'aucune construction n'a produits :
`api.php` et `data.json` ont survécu à leur retrait du dépôt précisément parce que personne
n'était prévenu qu'ils étaient encore là.

## La référence de contenu est figée

`reference/paniagua.dev-2026-08-12.html` est l'instantané du site publié avant refonte.
Le contrôle de contenu s'y réfère au lieu d'interroger le réseau : une fois la refonte
déployée, `paniagua.dev` sert le nouveau site, la référence s'auto-remplacerait et le
contrôle perdrait tout sens, en plus d'échouer sur les chaînes françaises passées sous
`/fr/`.

`npm run shots` capture la page en clair, en sombre et en 390 px. `tools/scroll-shots.mjs`
la capture à plusieurs positions de défilement, ce qui est le seul moyen de relire une
chorégraphie.
