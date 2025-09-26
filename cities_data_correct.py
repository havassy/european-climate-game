#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Európai városok klímaadatok kinyerése - HELYES verzió
A diagnosztika alapján: 
- temperature_1991_2020.nc fájlban a TP (csapadék) van
- precipitation_1991_2020.nc fájlban a T2M (hőmérséklet) van
"""

import os
import json
import netCDF4
import numpy as np
from datetime import datetime

# Tipikus európai városok koordinátái
CITIES = {
    "Stockholm": {
        "coords": [59.33, 18.07],
        "region": "north",
        "country": "Svédország"
    },
    "Oslo": {
        "coords": [59.91, 10.75],
        "region": "north", 
        "country": "Norvégia"
    },
    "Helsinki": {
        "coords": [60.17, 24.94],
        "region": "north",
        "country": "Finnország"
    },
    "London": {
        "coords": [51.51, -0.13],
        "region": "west",
        "country": "Egyesült Királyság"
    },
    "Dublin": {
        "coords": [53.33, -6.25],
        "region": "west",
        "country": "Írország"
    },
    "Amsterdam": {
        "coords": [52.37, 4.90],
        "region": "west",
        "country": "Hollandia"
    },
    "Madrid": {
        "coords": [40.42, -3.70],
        "region": "south",
        "country": "Spanyolország"
    },
    "Rome": {
        "coords": [41.90, 12.50],
        "region": "south",
        "country": "Olaszország"
    },
    "Athens": {
        "coords": [37.98, 23.73],
        "region": "south",
        "country": "Görögország"
    },
    "Berlin": {
        "coords": [52.52, 13.41],
        "region": "central",
        "country": "Németország"
    },
    "Vienna": {
        "coords": [48.21, 16.37],
        "region": "central",
        "country": "Ausztria"
    },
    "Budapest": {
        "coords": [47.50, 19.04],
        "region": "central",
        "country": "Magyarország"
    },
    "Warsaw": {
        "coords": [52.23, 21.01],
        "region": "east",
        "country": "Lengyelország"
    },
    "Bucharest": {
        "coords": [44.43, 26.10],
        "region": "east",
        "country": "Románia"
    }
}

def find_nearest_grid_point(lat, lon, lats, lons):
    """Legközelebbi rács pont keresése"""
    lat_idx = np.argmin(np.abs(lats - lat))
    lon_idx = np.argmin(np.abs(lons - lon))
    return lat_idx, lon_idx

def extract_climate_data():
    """Klímaadatok kinyerése a helyes fájl-változó hozzárendeléssel"""
    
    print("ERA5 klímaadatok kinyerése - helyes verzió")
    print("=" * 50)
    
    # NetCDF fájlok megnyitása
    # FIGYELEM: A nevek félrevezetők a tartalomhoz képest!
    temp_file = netCDF4.Dataset("data/precipitation_1991_2020.nc", 'r')  # T2M itt van
    precip_file = netCDF4.Dataset("data/temperature_1991_2020.nc", 'r')   # TP itt van
    
    print("Fájlok megnyitva:")
    print("  precipitation_1991_2020.nc -> T2M (hőmérséklet) adatok")
    print("  temperature_1991_2020.nc -> TP (csapadék) adatok")
    
    # Koordináták (mindkét fájlban ugyanazok)
    lats = temp_file.variables['latitude'][:]
    lons = temp_file.variables['longitude'][:]
    
    cities_data = {}
    
    for city_name, city_info in CITIES.items():
        print(f"\n{city_name} feldolgozása...")
        
        lat, lon = city_info["coords"]
        lat_idx, lon_idx = find_nearest_grid_point(lat, lon, lats, lons)
        
        actual_lat = lats[lat_idx]
        actual_lon = lons[lon_idx]
        
        print(f"  Koordináták: {lat:.2f}, {lon:.2f} -> {actual_lat:.2f}, {actual_lon:.2f}")
        
        try:
            # Hőmérséklet adatok (T2M a precipitation fájlból)
            temp_data = temp_file.variables['t2m'][:, lat_idx, lon_idx]
            
            # Csapadék adatok (TP a temperature fájlból) 
            precip_data = precip_file.variables['tp'][:, lat_idx, lon_idx]
            
            print(f"  Adatpontok: {len(temp_data)} hőmérséklet, {len(precip_data)} csapadék")
            
            # Havi átlagok számítása (30 év x 12 hónap = 360 hónap)
            n_years = 30
            
            # Reshape: 360 hónap -> (30 év, 12 hónap)
            temp_monthly = temp_data.reshape(n_years, 12)
            precip_monthly = precip_data.reshape(n_years, 12)
            
            # 30 év átlaga minden hónapra
            temp_avg = np.mean(temp_monthly, axis=0)
            precip_avg = np.mean(precip_monthly, axis=0)
            
            # HELYES KONVERZIÓK a diagnosztika alapján:
            
            # Hőmérséklet: Kelvin -> Celsius
            temp_celsius = temp_avg - 273.15
            
            # Csapadék: méter -> mm/hó (30-szoros szorzó)
            precip_mm = precip_avg * 1000 * 30
            
            print(f"  Hőmérséklet: {temp_celsius.mean():.1f}°C ({temp_avg.mean():.1f}K)")
            print(f"  Csapadék: {precip_mm.mean():.1f}mm/hó ({precip_avg.mean():.6f}m)")
            
            # Eredmények tárolása
            cities_data[city_name] = {
                "region": city_info["region"],
                "country": city_info["country"],
                "coordinates": {
                    "target": [lat, lon],
                    "actual": [float(actual_lat), float(actual_lon)]
                },
                "temperature": [round(float(t), 1) for t in temp_celsius],
                "precipitation": [round(float(p), 1) for p in precip_mm]
            }
            
        except Exception as e:
            print(f"  Hiba {city_name} feldolgozása során: {e}")
    
    # Fájlok bezárása
    temp_file.close()
    precip_file.close()
    
    return cities_data

def save_json_data(cities_data):
    """JSON adatok mentése"""
    
    if not cities_data:
        print("Nincs adat a mentéshez!")
        return False
    
    # js mappa létrehozása
    if not os.path.exists("js"):
        os.makedirs("js")
    
    # JSON struktúra
    output_data = {
        "metadata": {
            "source": "ERA5 Reanalysis 1991-2020",
            "extraction_date": datetime.now().isoformat(),
            "cities_count": len(cities_data),
            "note": "Helyes egységkonverziók: K->°C, m->mm"
        },
        "cities": cities_data
    }
    
    # JSON mentése
    with open("js/climate_data.json", 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nJSON mentve: js/climate_data.json")
    return True

def main():
    """Fő funkció"""
    
    cities_data = extract_climate_data()
    
    if cities_data:
        print(f"\n{len(cities_data)} város sikeresen feldolgozva")
        
        # Mintaadatok kiírása ellenőrzéshez
        budapest = cities_data.get('Budapest', {})
        if budapest:
            print(f"\nBudapest mintaadatok:")
            print(f"  Hőmérséklet: {budapest['temperature']}")
            print(f"  Csapadék: {budapest['precipitation']}")
        
        save_json_data(cities_data)
        print("\nKész! Frissítheted a GitHubon a js/climate_data.json fájlt.")
    else:
        print("Hiba történt az adatok feldolgozása során!")

if __name__ == "__main__":
    main()