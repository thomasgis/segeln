import csv
import gpxpy
from geopy.distance import great_circle

# --- EINSTELLUNGEN ---
INPUT_GPX = 'track_pints.gpx'
OUTPUT_CSV = 'sog_auswertung.csv'
SMOOTHING_WINDOW = 3  # Anzahl der Punkte für den gleitenden Mittelwert gegen GPS-Spikes

def calculate_sog_data(gpx_path):
    with open(gpx_path, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)

    raw_data = []

    for track in gpx.tracks:
        for segment in track.segments:
            for i in range(len(segment.points) - 1):
                p1 = segment.points[i]
                p2 = segment.points[i+1]
                
                time_diff = (p2.time - p1.time).total_seconds()
                
                if time_diff > 0:
                    # Distanz in Seemeilen (NM) und Metern berechnen
                    dist_nm = great_circle((p1.latitude, p1.longitude), (p2.latitude, p2.longitude)).nautical
                    dist_m = dist_nm * 1852.0
                    
                    # SOG Rohwerte berechnen
                    sog_knots_raw = dist_nm / (time_diff / 3600)
                    sog_kmh_raw = sog_knots_raw * 1.852
                    
                    raw_data.append({
                        'timestamp': p2.time.strftime('%Y-%m-%d %H:%M:%S'),
                        'latitude': p2.latitude,
                        'longitude': p2.longitude,
                        'elevation': p2.elevation,
                        'dist_m': dist_m,
                        'time_diff_sec': time_diff,
                        'sog_knots_raw': sog_knots_raw,
                        'sog_kmh_raw': sog_kmh_raw
                    })
                    
    # Glättung (Moving Average) anwenden, um GPS-Rauschen zu minimieren
    for i in range(len(raw_data)):
        start_idx = max(0, i - SMOOTHING_WINDOW + 1)
        window = raw_data[start_idx:i + 1]
        
        avg_knots = sum(p['sog_knots_raw'] for p in window) / len(window)
        avg_kmh = sum(p['sog_kmh_raw'] for p in window) / len(window)
        
        raw_data[i]['sog_knots_smooth'] = round(avg_knots, 2)
        raw_data[i]['sog_kmh_smooth'] = round(avg_kmh, 2)
        
    return raw_data

# Daten berechnen und als CSV speichern
data = calculate_sog_data(INPUT_GPX)

if data:
    headers = ['timestamp', 'latitude', 'longitude', 'elevation', 'sog_knots_smooth', 'sog_kmh_smooth']
    
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(data)
        
    print(f"Erfolgreich! Die Datei wurde als '{OUTPUT_CSV}' gespeichert.")
else:
    print("Keine gültigen Trackpunkte in der GPX-Datei gefunden.")
