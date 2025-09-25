#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Európai városok klímaadatok kinyerése NetCDF fájlokból
ERA5 reanalysis adatok → JSON export a JavaScript játékhoz
"""

import os
import json
import netCDF4
import numpy as np
from datetime import datetime

# Tipikus európai városok koordinátái és régió besorolása
CITIES = {
    # ÉSZAK-EURÓPA
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
    "Reykjavik": {
        "coords": [64.13, -21.82],
        "region": "north",
        "country": "Izland"
    },
    
    # NYUGAT-EURÓPA
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
    "Brussels": {
        "coords": [50.85, 4.35],
        "region": "west",
        "country": "Belgium"
    },
    
    # DÉL-EURÓPA
    "Madrid": {
        "coords": [40.42, -3.70],
        "region": "south",
        "country": "Spanyolország"
    },
    "Lisbon": {
        "coords": [38.72, -9.13],
        "region": "south",
        "country": "Portugália"
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
    
    # KÖZÉP-EURÓPA
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
    "Prague": {
        "coords": [50.08, 14.42],
        "region": "central",
        "country": "Csehország"
    },
    "Budapest": {
        "coords": [47.50, 19.04],
        "region": "central",
        "country": "Magyarország"
    },
    
    # KELET-EURÓPA
    "Bucharest": {
        "coords": [44.43, 26.10],
        "region": "east",
        "country": "Románia"
    },
    "Sofia": {
        "coords": [42.70, 23.32],
        "region": "east",
        "country": "Bulgária"
    },
    "Warsaw": {
        "coords": [52.23, 21.01],
        "region": "east",
        "country": "Lengyelország"
    },
    "Kiev": {
        "coords": [50.45, 30.52],
        "region": "east",
        "country": "Ukrajna"
    }
}

def find_nearest_grid_point(lat, lon, lats, lons):
    """Megtalálja a legközelebbi rács pontot a megadott koordinátákhoz"""
    lat_idx = np.argmin(np.abs(lats - lat))
    lon_idx = np.argmin(np.abs(lons - lon))
    return lat_idx, lon_idx

def kelvin_to_celsius(temp_k):
    """Kelvin fokról Celsius fokra konvertál"""
    return temp_k - 273.15

def extract_city_climate_data():
    """Kivonja az összes város klímaadatait"""
    
    print("Európai városok klímaadatok kinyerése...")
    print("=" * 50)
    
    # NetCDF fájlok megnyitása
    temp_path = "data/temperature_1991_2020.nc"
    precip_path = "data/precipitation_1991_2020.nc"
    
    if not os.path.exists(temp_path) or not os.path.exists(precip_path):
        print("Hiba: NetCDF fájlok nem találhatók!")
        return None
    
    print("NetCDF fájlok betöltése...")
    temp_ds = netCDF4.Dataset(temp_path, 'r')
    precip_ds = netCDF4.Dataset(precip_path, 'r')
    
    # Koordináták beolvasása
    lats = temp_ds.variables['latitude'][:]
    lons = temp_ds.variables['longitude'][:]
    
    print(f"Térfogat: {len(lats)} szélesség x {len(lons)} hosszúság")
    print(f"Szélesség tartomány: {lats.min():.2f} - {lats.max():.2f}°")
    print(f"Hosszúság tartomány: {lons.min():.2f} - {lons.max():.2f}°")
    
    # Adatvariáblusok meghatározása
    temp_vars = list(temp_ds.variables.keys())
    precip_vars = list(precip_ds.variables.keys())
    
    print(f"Hőmérséklet változók: {temp_vars}")
    print(f"Csapadék változók: {precip_vars}")
    
    # Főbb adatváltozók keresése
    temp_var_name = None
    precip_var_name = None
    
    # Hőmérséklet változó keresése (t2m, temperature, temp, stb.)
    for var in ['t2m', 'temperature', 'temp', 't']:
        if var in temp_ds.variables:
            temp_var_name = var
            break
    
    # Csapadék változó keresése (tp, precipitation, precip, stb.)
    for var in ['tp', 'precipitation', 'precip', 'pr']:
        if var in precip_ds.variables:
            precip_var_name = var
            break
    
    if not temp_var_name or not precip_var_name:
        print(f"Hiba: Nem találhatók az adatváltozók!")
        print(f"Hőmérséklet keresés: {temp_var_name}")
        print(f"Csapadék keresés: {precip_var_name}")
        temp_ds.close()
        precip_ds.close()
        return None
    
    print(f"Használt változók: {temp_var_name} (hőmérséklet), {precip_var_name} (csapadék)")
    
    # Városok adatainak kinyerése
    cities_data = {}
    
    for city_name, city_info in CITIES.items():
        print(f"\n{city_name} feldolgozása...")
        
        lat, lon = city_info["coords"]
        
        # Legközelebbi rács pont keresése
        lat_idx, lon_idx = find_nearest_grid_point(lat, lon, lats, lons)
        
        actual_lat = lats[lat_idx]
        actual_lon = lons[lon_idx]
        
        print(f"  Célkoordináták: {lat:.2f}, {lon:.2f}")
        print(f"  Rács koordináták: {actual_lat:.2f}, {actual_lon:.2f}")
        
        try:
            # Hőmérséklet adatok beolvasása
            temp_data = temp_ds.variables[temp_var_name][:, lat_idx, lon_idx]
            
            # Csapadék adatok beolvasása  
            precip_data = precip_ds.variables[precip_var_name][:, lat_idx, lon_idx]
            
            # Havi átlagok számítása (feltételezzük hogy az első dimenzió az idő)
            # 12 hónapra átlagoljuk az összes évet
            
            # Reshape az adatokat évek és hónapok szerint (30 év x 12 hónap)
            n_months = len(temp_data)
            n_years = n_months // 12
            
            if n_months % 12 != 0:
                print(f"  Figyelem: {n_months} hónap nem osztható 12-vel")
                n_years = n_months // 12
                temp_data = temp_data[:n_years*12]
                precip_data = precip_data[:n_years*12]
            
            # Reshape (évek, hónapok)
            temp_monthly = temp_data.reshape(n_years, 12)
            precip_monthly = precip_data.reshape(n_years, 12)
            
            # Havi átlagok számítása
            temp_avg = np.mean(temp_monthly, axis=0)
            precip_avg = np.mean(precip_monthly, axis=0)
            
            # Kelvin → Celsius konverzió hőmérsékletre
            if np.mean(temp_avg) > 100:  # Ha > 100, valószínűleg Kelvin
                temp_avg = kelvin_to_celsius(temp_avg)
            
            # Csapadék egység ellenőrzése (m/s → mm/month konverzió ha szükséges)
            if np.mean(precip_avg) < 1:  # Ha nagyon kicsi, valószínűleg m/s
                # Átlagos napok száma havonta: ~30.44
                # m/s → mm/hó: * 1000 * 3600 * 24 * 30.44
                precip_avg = precip_avg * 1000 * 3600 * 24 * 30.44
            
            # Eredmények tárolása
            cities_data[city_name] = {
                "region": city_info["region"],
                "country": city_info["country"],
                "coordinates": {
                    "target": [lat, lon],
                    "actual": [float(actual_lat), float(actual_lon)]
                },
                "temperature": [round(float(t), 1) for t in temp_avg],
                "precipitation": [round(float(p), 1) for p in precip_avg]
            }
            
            print(f"  Hőmérséklet átlag: {np.mean(temp_avg):.1f}°C")
            print(f"  Csapadék átlag: {np.mean(precip_avg):.1f}mm/hó")
            
        except Exception as e:
            print(f"  Hiba {city_name} feldolgozása során: {e}")
    
    # NetCDF fájlok bezárása
    temp_ds.close()
    precip_ds.close()
    
    return cities_data

def save_climate_data_json(cities_data):
    """Klímaadatok mentése JSON formátumban"""
    
    if not cities_data:
        print("Nincs adat a mentéshez!")
        return False
    
    # JavaScript könyvtár létrehozása ha nem létezik
    js_dir = "js"
    if not os.path.exists(js_dir):
        os.makedirs(js_dir)
    
    # Teljes adatstruktúra JSON-hoz
    output_data = {
        "metadata": {
            "source": "ERA5 Reanalysis 1991-2020",
            "extraction_date": datetime.now().isoformat(),
            "cities_count": len(cities_data),
            "regions": ["north", "west", "south", "central", "east"]
        },
        "cities": cities_data
    }
    
    # JSON fájl mentése
    output_path = os.path.join(js_dir, "climate_data.json")
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\nJSON adatok sikeresen mentve: {output_path}")
        print(f"Fájl méret: {os.path.getsize(output_path)} bájt")
        
        return True
        
    except Exception as e:
        print(f"Hiba a JSON mentése során: {e}")
        return False

def main():
    """Fő funkcó"""
    print("European Climate Game - Klímaadatok Kinyerő")
    print("=" * 60)
    
    # Klímaadatok kinyerése
    cities_data = extract_city_climate_data()
    
    if not cities_data:
        print("Hiba történt az adatok kinyerése során!")
        return
    
    print(f"\nSikeresen feldolgozott városok száma: {len(cities_data)}")
    
    # Régió szerinti összesítő
    regions = {}
    for city, data in cities_data.items():
        region = data["region"]
        if region not in regions:
            regions[region] = []
        regions[region].append(city)
    
    print("\nRégiók szerinti bontás:")
    for region, city_list in regions.items():
        print(f"  {region.upper()}: {', '.join(city_list)}")
    
    # JSON mentése
    if save_climate_data_json(cities_data):
        print("\nSikeres adatkinyerés!")
        print("Következő lépés: JavaScript játék frissítése az új adatokkal")
    else:
        print("Hiba történt a JSON mentése során!")

if __name__ == "__main__":
    main()