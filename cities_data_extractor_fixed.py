#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Európai városok klímaadatok kinyerése NetCDF fájlokból - JAVÍTOTT VERZIÓ
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
    
    # DÉL-EURÓPA
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
    "Budapest": {
        "coords": [47.50, 19.04],
        "region": "central",
        "country": "Magyarország"
    },
    
    # KELET-EURÓPA
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
    """Megtalálja a legközelebbi rács pontot a megadott koordinátákhoz"""
    lat_idx = np.argmin(np.abs(lats - lat))
    lon_idx = np.argmin(np.abs(lons - lon))
    return lat_idx, lon_idx

def kelvin_to_celsius(temp_k):
    """Kelvin fokról Celsius fokra konvertál"""
    return temp_k - 273.15

def find_data_variables(temp_ds, precip_ds):
    """Intelligens keresés az adatváltozókhoz"""
    print("Adatváltozók keresése...")
    
    # Összes változó listázása
    temp_vars = list(temp_ds.variables.keys())
    precip_vars = list(precip_ds.variables.keys())
    
    print(f"Hőmérséklet fájl változói: {temp_vars}")
    print(f"Csapadék fájl változói: {precip_vars}")
    
    temp_var = None
    precip_var = None
    temp_source_file = None
    precip_source_file = None
    
    # Keresés: t2m változó (hőmérséklet)
    if 't2m' in temp_vars:
        temp_var = 't2m'
        temp_source_file = 'temperature'
    elif 't2m' in precip_vars:
        temp_var = 't2m' 
        temp_source_file = 'precipitation'
    
    # Keresés: tp változó (csapadék)
    if 'tp' in temp_vars:
        precip_var = 'tp'
        precip_source_file = 'temperature'
    elif 'tp' in precip_vars:
        precip_var = 'tp'
        precip_source_file = 'precipitation'
    
    print(f"Talált hőmérséklet változó: {temp_var} a {temp_source_file} fájlban")
    print(f"Talált csapadék változó: {precip_var} a {precip_source_file} fájlban")
    
    return temp_var, precip_var, temp_source_file, precip_source_file

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
    
    # Adatváltozók intelligens keresése
    temp_var, precip_var, temp_file, precip_file = find_data_variables(temp_ds, precip_ds)
    
    if not temp_var or not precip_var:
        print("Hiba: Nem találhatók az adatváltozók!")
        temp_ds.close()
        precip_ds.close()
        return None
    
    # Megfelelő dataset kiválasztása minden változóhoz
    if temp_file == 'temperature':
        temp_dataset = temp_ds
    else:
        temp_dataset = precip_ds
        
    if precip_file == 'temperature':
        precip_dataset = temp_ds
    else:
        precip_dataset = precip_ds
    
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
            temp_data = temp_dataset.variables[temp_var][:, lat_idx, lon_idx]
            
            # Csapadék adatok beolvasása  
            precip_data = precip_dataset.variables[precip_var][:, lat_idx, lon_idx]
            
            print(f"  Beolvasott adatpontok: {len(temp_data)} hőmérséklet, {len(precip_data)} csapadék")
            
            # Havi átlagok számítása (feltételezzük hogy az első dimenzió az idő)
            # 12 hónapra átlagoljuk az összes évet
            
            # Reshape az adatokat évek és hónapok szerint
            n_months_temp = len(temp_data)
            n_months_precip = len(precip_data)
            
            # Legkisebb közös többszörös a 12-vel
            n_years_temp = n_months_temp // 12
            n_years_precip = n_months_precip // 12
            
            if n_years_temp > 0 and n_years_precip > 0:
                # Levágás a teljes évekre
                temp_data_cut = temp_data[:n_years_temp*12]
                precip_data_cut = precip_data[:n_years_precip*12]
                
                # Reshape (évek, hónapok)
                temp_monthly = temp_data_cut.reshape(n_years_temp, 12)
                precip_monthly = precip_data_cut.reshape(n_years_precip, 12)
                
                # Havi átlagok számítása
                temp_avg = np.mean(temp_monthly, axis=0)
                precip_avg = np.mean(precip_monthly, axis=0)
                
                # Kelvin → Celsius konverzió hőmérsékletre
                if np.mean(temp_avg) > 100:  # Ha > 100, valószínűleg Kelvin
                    temp_avg = kelvin_to_celsius(temp_avg)
                
                # Csapadék egység ellenőrzése (m/s → mm/month konverzió ha szükséges)
                if np.mean(precip_avg) < 1:  # Ha nagyon kicsi, valószínűleg m/s
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
            else:
                print(f"  Hiba: Nem elegendő adatpont a havi átlagok számításához")
            
        except Exception as e:
            print(f"  Hiba {city_name} feldolgozása során: {e}")
            import traceback
            traceback.print_exc()
    
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
    """Fő funkció"""
    print("European Climate Game - Klímaadatok Kinyerő (Javított)")
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