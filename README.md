# Monky Agen – Plan 3D (mise à jour automatique des tarifs)

Ce dépôt héberge le plan 3D interactif du Monky Agen et un robot qui relève chaque nuit les prix
des pages activités de **monky.fr/agen**. Quand un prix change sur le site, `tarifs.json` est mis à
jour et la page publiée affiche le nouveau prix, sans intervention.

## Contenu


| Fichier | Rôle |
|---|---|
| `index.html` | Le plan 3D (autonome). Il lit `tarifs.json` au chargement. |
| `tarifs.json` | Tous les tarifs affichés. Seul fichier modifié par le robot. |
| `scripts/update_prices.py` | Le robot : lit les pages monky.fr et met à jour `tarifs.json`. |
| `.github/workflows/update-prices.yml` | Lance le robot chaque jour vers 6 h (heure de Paris). |
| `.nojekyll` | Fichier vide nécessaire à GitHub Pages. |

## Mise en place (une seule fois, ~15 min, tout depuis le navigateur)

1. **Créer un compte** sur https://github.com (idéalement avec une adresse @monky.fr).
2. **Créer le dépôt** : bouton **New repository** → nom `monky-agen-3d` → **Public** → *Create repository*.
   (GitHub Pages gratuit exige un dépôt public : le plan 3D sera visible par tous, ce qui est le but.)
3. **Envoyer les fichiers** : sur la page du dépôt, *uploading an existing file* → glisser `index.html`,
   `tarifs.json`, `README.md`, `.nojekyll` et le dossier `scripts` → **Commit changes**.
4. **Créer le robot** (le dossier `.github` est souvent masqué sur Mac/Windows, on le crée à la main) :
   **Add file → Create new file** → nom : `.github/workflows/update-prices.yml` →
   coller le contenu du fichier fourni → **Commit changes**.
5. **Publier la page** : **Settings → Pages** → *Source* : **Deploy from a branch** → Branch **main**, dossier **/ (root)** → *Save*.
   Après 1 à 2 minutes, la page est en ligne à `https://VOTRE-COMPTE.github.io/monky-agen-3d/`.
6. **Autoriser le robot à écrire** : **Settings → Actions → General → Workflow permissions** →
   **Read and write permissions** → *Save*.
7. **Premier passage (calibration)** : onglet **Actions** → *Mise à jour des tarifs Monky Agen* → **Run workflow**.
   Le robot associe chaque tarif à son emplacement sur la page monky.fr. Les tarifs absents du site
   (Battle Kart, billard, pass journée, anniversaires…) restent en **saisie manuelle**.
8. **Intégrer dans WordPress** : bloc *HTML personnalisé* :

```html
<div style="position:relative;width:100%;height:80vh;min-height:600px;">
  <iframe src="https://VOTRE-COMPTE.github.io/monky-agen-3d/" title="Plan 3D du Monky Agen"
          style="position:absolute;inset:0;width:100%;height:100%;border:0;border-radius:12px;"
          loading="lazy" allowfullscreen></iframe>
</div>
```

## Fonctionnement au quotidien

- **Chaque jour** le robot lit les pages : bowling, laser game, pixel games, quiz room, karaoké,
  jump park, kid park, baby park, blind test.
- **Prix modifié sur le site** → `tarifs.json` est mis à jour et commité → la page affiche le nouveau prix
  (délai : quelques minutes après le passage du robot).
- **Page monky.fr réorganisée** (un tarif ajouté ou supprimé) → le robot ne touche à rien et ouvre une
  **Issue** « Tarifs Monky Agen : vérification nécessaire » (vous recevez un e-mail de GitHub).
  Pour la régler : corriger les prix dans `tarifs.json` (crayon ✏️ sur GitHub), supprimer pour cette activité
  les lignes `"nb_montants"` et `"signature"`, enregistrer, puis relancer **Run workflow**.
- **Tarif manuel** (Battle Kart, billard, anniversaires…) : modifier la valeur `"p"` directement dans
  `tarifs.json` sur GitHub. La page est à jour 1 à 2 minutes après l'enregistrement.

## Limites

- Le robot ne détecte que les **montants** (ex. « 8,90 € ») ; il ne crée pas de nouvelle activité ni de nouvelle ligne de tarif.
- Les plans, l'emplacement des activités et la 3D ne changent pas automatiquement : pour toute évolution du parc,
  il faut remplacer `index.html`.
- Si GitHub désactive le robot après 60 jours sans activité sur le dépôt, un e-mail prévient : cliquer sur
  *Enable workflow* dans l'onglet Actions.
