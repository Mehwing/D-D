#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Application locale d'assistance au décompte des voix lors d'un vote à main levée."""

import tkinter as tk
from tkinter import ttk
from fractions import Fraction

NB_PARTIS = 8


class VoteCounterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Décompte de voix - Vote à main levée")
        self.geometry("720x640")
        self.resizable(True, True)

        self.pour = 0
        self.contre = 0
        self.abstention = 0

        self.variants_partis = []
        self.type_loi = tk.StringVar(value="basique")

        self._construire_interface()
        self.mettre_a_jour()

    def _construire_interface(self):
        cadre_partis = ttk.LabelFrame(self, text="Adhérents par parti (les champs vides sont ignorés)", padding=8)
        cadre_partis.pack(fill="x", padx=10, pady=(10, 5))

        for i in range(NB_PARTIS):
            ttk.Label(cadre_partis, text=f"Parti {i + 1} :").grid(row=i // 2, column=(i % 2) * 2, sticky="e", padx=(4, 2), pady=2)
            var = tk.StringVar()
            self.variants_partis.append(var)
            entree = ttk.Entry(cadre_partis, textvariable=var, width=8, justify="center")
            entree.grid(row=i // 2, column=(i % 2) * 2 + 1, padx=(2, 12), pady=2)
            var.trace_add("write", lambda *_: self.mettre_a_jour())

        cadre_type = ttk.LabelFrame(self, text="Type de loi", padding=8)
        cadre_type.pack(fill="x", padx=10, pady=5)

        ttk.Radiobutton(
            cadre_type, text="Loi basique (majorité +1/2 des voix exprimées)",
            variable=self.type_loi, value="basique", command=self.mettre_a_jour
        ).pack(anchor="w")
        ttk.Radiobutton(
            cadre_type, text="Loi constitutionnelle (majorité des 2/3 des voix exprimées)",
            variable=self.type_loi, value="constitutionnelle", command=self.mettre_a_jour
        ).pack(anchor="w")

        cadre_votes = ttk.LabelFrame(self, text="Décompte des voix", padding=8)
        cadre_votes.pack(fill="x", padx=10, pady=5)

        for texte, couleur, commande in (
            ("Pour", "#2e7d32", lambda: self.enregistrer_vote("pour")),
            ("Contre", "#c62828", lambda: self.enregistrer_vote("contre")),
            ("Abstention", "#f9a825", lambda: self.enregistrer_vote("abstention")),
        ):
            bouton = tk.Button(
                cadre_votes, text=texte, font=("TkDefaultFont", 12, "bold"),
                bg=couleur, fg="white", width=10, height=2, command=commande
            )
            bouton.pack(side="left", expand=True, fill="x", padx=6, pady=4)

        ligne_annulation = ttk.Frame(cadre_votes)
        ligne_annulation.pack(fill="x", pady=(8, 0))
        ttk.Button(ligne_annulation, text="-1 (annuler dernière voix)", command=self.annuler_derniere).pack(side="left", padx=4)
        ttk.Button(ligne_annulation, text="Réinitialiser les voix", command=self.reinitialiser).pack(side="left", padx=4)

        cadre_resultat = ttk.LabelFrame(self, text="Résultat", padding=10)
        cadre_resultat.pack(fill="both", expand=True, padx=10, pady=5)

        self.label_details = ttk.Label(cadre_resultat, font=("TkDefaultFont", 11), justify="center")
        self.label_details.pack(pady=6)

        self.label_verdict = ttk.Label(cadre_resultat, font=("TkDefaultFont", 16, "bold"))
        self.label_verdict.pack(pady=10)

    def total_adherents(self):
        total = 0
        for var in self.variants_partis:
            valeur = var.get().strip()
            if valeur:
                try:
                    total += int(valeur)
                except ValueError:
                    pass
        return total

    def enregistrer_vote(self, type_vote):
        if type_vote == "pour":
            self.pour += 1
        elif type_vote == "contre":
            self.contre += 1
        else:
            self.abstention += 1
        self.mettre_a_jour()

    def annuler_derniere(self):
        if self.abstention > 0:
            self.abstention -= 1
        elif self.contre > 0:
            self.contre -= 1
        elif self.pour > 0:
            self.pour -= 1
        self.mettre_a_jour()

    def reinitialiser(self):
        self.pour = 0
        self.contre = 0
        self.abstention = 0
        self.mettre_a_jour()

    def mettre_a_jour(self):
        total_exprime = self.pour + self.contre
        total_general = total_exprime + self.abstention

        if self.type_loi.get() == "constitutionnelle":
            seuil = Fraction(2, 3)
            libelle = "majorité des 2/3"
        else:
            seuil = Fraction(1, 2)
            libelle = "majorité +1/2 (strictement plus de la moitié)"

        if total_exprime == 0:
            voix_requises = 0
            acceptee = False
        elif seuil == Fraction(1, 2):
            voix_requises = total_exprime // 2 + 1
            acceptee = self.pour >= voix_requises
        else:
            voix_requises = -(-2 * total_exprime // 3)
            acceptee = self.pour * 3 >= 2 * total_exprime

        self.label_details.config(text=(
            f"Adhérents inscrits : {self.total_adherents()}\n"
            f"Pour : {self.pour}   Contre : {self.contre}   Abstention : {self.abstention}\n"
            f"Voix exprimées (abstentions exclues) : {total_exprime}\n"
            f"Voix totales (avec abstentions) : {total_general}\n"
            f"Seuil ({libelle}) : {voix_requises} voix Pour requises"
        ))

        if total_exprime == 0:
            self.label_verdict.config(text="Aucun vote exprimé", fg="#616161")
        elif acceptee:
            self.label_verdict.config(text="LOI ACCEPTÉE ✔", fg="#2e7d32")
        else:
            self.label_verdict.config(text="LOI REJETÉE ✘", fg="#c62828")


if __name__ == "__main__":
    app = VoteCounterApp()
    app.mainloop()
