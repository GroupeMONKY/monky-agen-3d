#!/usr/bin/env python3
"""
Met à jour tarifs.json à partir des pages activités de monky.fr/agen.

Principe (auto-calibrage, sans dépendre de la mise en page du site) :
  1. Pour chaque activité suivie, on télécharge sa page et on relève, dans l'ordre,
     tous les montants en euros du texte (ex. « 8,90 € », « 14€ »).
  2. Au premier passage, chaque ligne de tarif est associée à la position du montant
     identique sur la page (champ "pos"). C'est la « calibration ».
  3. Aux passages suivants, si la page contient toujours le même nombre de montants,
     chaque ligne reprend le montant situé à sa position : un changement de prix
     est donc appliqué automatiquement.
  4. Si la structure de la page change (nombre de montants différent, page absente…),
     on ne touche à rien et on signale l'anomalie (fichier anomalies.md → Issue GitHub).
"""
import json, re, sys, datetime, pathlib, hashlib
import requests
from bs4 import BeautifulSoup

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "tarifs.json"
REPORT = ROOT / "anomalies.md"
UA = {"User-Agent": "Mozilla/5.0 (compatible; MonkyAgen3D-bot/1.0; +https://monky.fr)"}
PRICE = re.compile(r"(\d{1,3}(?:[.,]\d{1,2})?)\s*(?:€|euros?\b)", re.I)

def page_prices(url):
    r = requests.get(url, headers=UA, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    for t in soup(["script", "style", "noscript", "header", "footer", "nav", "svg"]):
        t.decompose()
    main = soup.find("main") or soup.body or soup
    text = re.sub(r"\s+", " ", main.get_text(" "))
    return [float(m.group(1).replace(",", ".")) for m in PRICE.finditer(text)], text

def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    changes, problems = [], []
    for aid, act in data["activites"].items():
        if not act.get("suivi_auto"):
            continue
        try:
            prices, text = page_prices(act["url"])
        except Exception as e:
            problems.append(f"- **{act['nom']}** : page inaccessible ({e})")
            continue
        sig = hashlib.sha1(" ".join(map(str, prices)).encode()).hexdigest()[:10]
        n = len(prices)
        calibrated = act.get("nb_montants") is not None
        if not calibrated:
            used = set()
            for ln in act["lignes"]:
                if not isinstance(ln.get("p"), (int, float)):
                    continue
                idx = next((i for i, v in enumerate(prices) if abs(v - ln["p"]) < 0.001 and i not in used), None)
                if idx is None:
                    ln["pos"] = None
                    problems.append(f"- **{act['nom']}** – « {ln['l']} » ({ln['p']} €) introuvable sur la page : ligne laissée en manuel.")
                else:
                    ln["pos"] = idx; used.add(idx)
            act["nb_montants"] = n
            act["signature"] = sig
            continue
        if n != act["nb_montants"]:
            problems.append(f"- **{act['nom']}** : la page affiche maintenant {n} montants au lieu de {act['nb_montants']} "
                            f"({', '.join(f'{p:g} €' for p in prices)}). Mise à jour automatique suspendue : vérifier et recalibrer.")
            continue
        for ln in act["lignes"]:
            pos = ln.get("pos")
            if pos is None or not isinstance(ln.get("p"), (int, float)):
                continue
            new = prices[pos]
            if abs(new - ln["p"]) > 0.001:
                changes.append(f"- **{act['nom']}** – {ln['l']} : {ln['p']:g} € → {new:g} €")
                ln["p"] = new
        act["signature"] = sig

    if changes:
        data["maj"] = datetime.date.today().isoformat()
        data["source"] = "monky.fr/agen (mise à jour automatique)"
    DATA.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if problems:
        REPORT.write_text("Le robot de mise à jour des tarifs a besoin d'une vérification :\n\n" + "\n".join(problems) +
                          "\n\nPour recalibrer une activité : dans tarifs.json, corriger les prix si besoin puis supprimer "
                          "ses champs \"nb_montants\" et \"signature\" ; le prochain passage la recalibrera.\n", encoding="utf-8")
    elif REPORT.exists():
        REPORT.unlink()
    print("\n".join(changes) or "Aucun changement de prix.")
    if problems:
        print("\nAnomalies :\n" + "\n".join(problems))

if __name__ == "__main__":
    sys.exit(main())
