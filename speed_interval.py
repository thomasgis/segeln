
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

datei = "/Users/Shared/tmp/28.csv"

# CSV automatisch einlesen
df = pd.read_csv(datei, sep=None, engine="python")

# Spaltennamen bereinigen
df.columns = df.columns.str.strip()

# Gewünschte Spalten
speed_field = "sog_knots_smooth"
length_field = "length_m"

# Prüfen, ob Spalten vorhanden sind
for spalte in [speed_field, length_field]:
    if spalte not in df.columns:
        raise ValueError(
            f"Spalte {spalte} nicht gefunden! "
            f"Vorhandene Spalten: {list(df.columns)}"
        )

# Werte numerisch umwandeln
df[speed_field] = pd.to_numeric(
    df[speed_field].astype(str).str.replace(",", ".", regex=False),
    errors="coerce"
)

df[length_field] = pd.to_numeric(
    df[length_field].astype(str).str.replace(",", ".", regex=False),
    errors="coerce"
)

# Ungültige und negative Werte entfernen
df = df.dropna(subset=[speed_field, length_field])
df = df[(df[speed_field] >= 0) & (df[length_field] >= 0)]

# Meter in Seemeilen umrechnen
df["length_nm"] = df[length_field] / 1852

# Intervalle berechnen
max_wert = int(np.ceil(df[speed_field].max()))
bins = np.arange(0, max_wert + 2, 1)

df["Intervall"] = pd.cut(
    df[speed_field],
    bins=bins,
    right=False,
    include_lowest=True
)

# Strecke je Geschwindigkeitsintervall summieren
ergebnis = (
    df.groupby("Intervall", observed=False)["length_nm"]
    .sum()
    .reset_index()
)

# Intervallbezeichnungen
ergebnis["Intervall_kn"] = [
    f"{int(interval.left)}-{int(interval.right)}"
    for interval in ergebnis["Intervall"]
]

ergebnis = ergebnis[["Intervall_kn", "length_nm"]]
ergebnis.columns = ["Intervall_kn", "Strecke_NM"]

# Gesamtstrecke
gesamtstrecke = ergebnis["Strecke_NM"].sum()

print("\nGefahrene Strecke je Geschwindigkeitsintervall:")
print(ergebnis.to_string(index=False))

print(f"\nGesamtstrecke: {gesamtstrecke:.3f} NM")

# Plot
plt.figure(figsize=(14, 6))

plt.bar(
    ergebnis["Intervall_kn"],
    ergebnis["Strecke_NM"],
    edgecolor="black"
)

plt.xlabel("Geschwindigkeit (kn)")
plt.ylabel("Gefahrene Strecke (Seemeilen)")
plt.title("Gefahrene Strecke nach Geschwindigkeitsintervallen")

plt.grid(axis="y", alpha=0.3)
plt.tight_layout()

plt.savefig(
    "sog_streckenverteilung.png",
    dpi=300
)

plt.show()

# CSV exportieren
ergebnis.to_csv(
    "sog_streckenverteilung.csv",
    sep=";",
    index=False
)
