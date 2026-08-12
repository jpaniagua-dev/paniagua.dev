# Référence de contenu

Instantané de `https://paniagua.dev/` pris le **2026-08-12**, avant que la refonte ne le
remplace.

C'est la source dont vient tout le texte du site : `tools/check-content.py` vérifie que
chaque chaîne de `src/data/content.ts` y figure, directement ou via le registre
`derivedFrom`.

**Pourquoi un instantané plutôt que la page en ligne.** Une fois la refonte déployée,
`paniagua.dev` sert le nouveau site : la référence s'auto-remplacerait et le contrôle
perdrait tout son sens, en plus d'échouer sur les chaînes françaises passées sous `/fr/`.
Figée ici, la garantie reste vérifiable indéfiniment, et sans accès réseau.

Ne pas modifier ce fichier. Le régénérer reviendrait à réécrire l'histoire que le contrôle
est censé attester.

    sha256  cdbea45f41f5ed23f61c1a953b8d2c46b8bbe9a893c0376d30a2f2b122b0eccd
