#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NetCDF fájlok részletes diagnosztika
Cél: Az ERA5 adatok pontos egységeinek és struktúrájának feltárása
"""

import os
import netCDF4
import numpy as np

def analyze_netcdf_file(filepath, file_description):
    """Részletes NetCDF fájl elemzés"""
    
    print(f"\n{'='*60}")
    print(f"ELEMZÉS: {file_description}")
    print(f"Fájl: {filepath}")
    print(f"{'='*60}")
    
    if not os.path.exists(filepath):
        print(f"❌ Fájl nem található: {filepath}")
        return None
    
    try:
        # NetCDF fájl megnyitása
        ds = netCDF4.Dataset(filepath, 'r')
        
        # Globális attribútumok
        print("\n📋 GLOBÁLIS ATTRIBÚTUMOK:")
        for attr in ds.ncattrs():
            value = getattr(ds, attr)
            print(f"  {attr}: {value}")
        
        # Dimenziók
        print("\n📏 DIMENZIÓK:")
        for dim_name, dim in ds.dimensions.items():
            size = len(dim) if not dim.isunlimited() else "UNLIMITED"
            print(f"  {dim_name}: {size}")
        
        # Koordináta változók
        print("\n🗺️ KOORDINÁTÁK:")
        coord_vars = ['longitude', 'latitude', 'time', 'valid_time']
        for coord_name in coord_vars:
            if coord_name in ds.variables:
                var = ds.variables[coord_name]
                print(f"\n  {coord_name.upper()}:")
                print(f"    Alakja: {var.shape}")
                print(f"    Típus: {var.dtype}")
                
                # Attribútumok
                for attr in var.ncattrs():
                    print(f"    {attr}: {getattr(var, attr)}")
                
                # Tartomány
                if len(var) > 0:
                    print(f"    Tartomány: {var[:].min():.6f} - {var[:].max():.6f}")
                    if coord_name == 'time' and len(var) > 1:
                        print(f"    Első érték: {var[0]}")
                        print(f"    Utolsó érték: {var[-1]}")
        
        # Adatváltozók
        print("\n🌡️ ADATVÁLTOZÓK:")
        data_vars = [var for var in ds.variables.keys() 
                    if var not in ['longitude', 'latitude', 'time', 'valid_time', 'number', 'expver']]
        
        for var_name in data_vars:
            var = ds.variables[var_name]
            print(f"\n  {var_name.upper()}:")
            print(f"    Alakja: {var.shape}")
            print(f"    Típus: {var.dtype}")
            print(f"    Dimenziók: {var.dimensions}")
            
            # Minden attribútum
            print("    Attribútumok:")
            for attr in var.ncattrs():
                value = getattr(var, attr)
                print(f"      {attr}: {value}")
            
            # Statisztikák minta adatokon
            try:
                # Első időpont, középső koordináta
                if len(var.shape) == 3:  # (time, lat, lon)
                    mid_lat = var.shape[1] // 2
                    mid_lon = var.shape[2] // 2
                    sample_data = var[:10, mid_lat, mid_lon]  # Első 10 időpont
                    
                    print(f"    Minta adatok (első 10 időpont, középső koordináta):")
                    print(f"      Értékek: {sample_data[:5]}...")
                    print(f"      Min: {sample_data.min():.8f}")
                    print(f"      Max: {sample_data.max():.8f}")
                    print(f"      Átlag: {sample_data.mean():.8f}")
                    print(f"      Std: {sample_data.std():.8f}")
            except Exception as e:
                print(f"    ⚠️ Nem sikerült minta adatokat olvasni: {e}")
        
        ds.close()
        
        print(f"\n✅ {file_description} elemzés befejezve")
        return True
        
    except Exception as e:
        print(f"❌ Hiba a fájl elemzése során: {e}")
        return False

def analyze_specific_location(temp_path, precip_path, lat=47.5, lon=19.0, location_name="Budapest"):
    """Konkrét helyszín részletes elemzése"""
    
    print(f"\n{'='*60}")
    print(f"HELYSZÍN ELEMZÉS: {location_name} ({lat}, {lon})")
    print(f"{'='*60}")
    
    try:
        # Fájlok megnyitása
        temp_ds = netCDF4.Dataset(temp_path, 'r')
        precip_ds = netCDF4.Dataset(precip_path, 'r')
        
        # Koordináták
        lats = temp_ds.variables['latitude'][:]
        lons = temp_ds.variables['longitude'][:]
        
        # Legközelebbi rács pont keresése
        lat_idx = np.argmin(np.abs(lats - lat))
        lon_idx = np.argmin(np.abs(lons - lon))
        
        actual_lat = lats[lat_idx]
        actual_lon = lons[lon_idx]
        
        print(f"Célkoordináták: {lat}, {lon}")
        print(f"Rács koordináták: {actual_lat:.2f}, {actual_lon:.2f}")
        print(f"Távolság: {abs(lat-actual_lat)*111:.1f}km N-S, {abs(lon-actual_lon)*111*np.cos(np.radians(lat)):.1f}km E-W")
        
        # Adatváltozók keresése
        temp_vars = [var for var in temp_ds.variables.keys() 
                    if var not in ['longitude', 'latitude', 'time', 'valid_time', 'number', 'expver']]
        precip_vars = [var for var in precip_ds.variables.keys() 
                      if var not in ['longitude', 'latitude', 'time', 'valid_time', 'number', 'expver']]
        
        print(f"\nHőmérséklet fájl változói: {temp_vars}")
        print(f"Csapadék fájl változói: {precip_vars}")
        
        # Hőmérséklet elemzése
        if temp_vars:
            temp_var_name = temp_vars[0]
            temp_var = temp_ds.variables[temp_var_name]
            temp_data = temp_var[:, lat_idx, lon_idx]
            
            print(f"\nHŐMÉRSÉKLET ELEMZÉS ({temp_var_name}):")
            print(f"  Idősorok száma: {len(temp_data)}")
            print(f"  Első 12 érték: {temp_data[:12]}")
            print(f"  Utolsó 12 érték: {temp_data[-12:]}")
            print(f"  Minimum: {temp_data.min():.2f}")
            print(f"  Maximum: {temp_data.max():.2f}")
            print(f"  Átlag: {temp_data.mean():.2f}")
            
            # Egységek ellenőrzése
            if hasattr(temp_var, 'units'):
                units = temp_var.units
                print(f"  Egységek: {units}")
                if 'K' in units or temp_data.mean() > 100:
                    print("  ⚠️ Valószínűleg Kelvin egységben van")
                else:
                    print("  ✅ Valószínűleg Celsius egységben van")
        
        # Csapadék elemzése  
        if precip_vars:
            precip_var_name = precip_vars[0]
            precip_var = precip_ds.variables[precip_var_name]
            precip_data = precip_var[:, lat_idx, lon_idx]
            
            print(f"\nCSAPADÉK ELEMZÉS ({precip_var_name}):")
            print(f"  Idősorok száma: {len(precip_data)}")
            print(f"  Első 12 érték: {precip_data[:12]}")
            print(f"  Utolsó 12 érték: {precip_data[-12:]}")
            print(f"  Minimum: {precip_data.min():.8f}")
            print(f"  Maximum: {precip_data.max():.8f}")
            print(f"  Átlag: {precip_data.mean():.8f}")
            
            # Egységek és lehetséges konverziók
            if hasattr(precip_var, 'units'):
                units = precip_var.units
                print(f"  Egységek: {units}")
                
                # Tipikus ERA5 egységek elemzése
                if 'm' in units.lower():
                    if 's' in units.lower():
                        print("  💡 m/s egység - szorzás szükséges mm/hó-hoz")
                        monthly_mm = precip_data.mean() * 1000 * 30.44 * 24 * 3600 / (30.44 * 24 * 3600)
                        print(f"     Havi mm becslés (×1000): {precip_data.mean() * 1000:.1f}")
                        print(f"     Havi mm becslés (teljes konv.): {precip_data.mean() * 1000 * 30.44 * 24 * 3600:.1f}")
                    else:
                        print("  💡 Méter egység - szorzás 1000-rel mm-hez")
                        print(f"     mm becslés: {precip_data.mean() * 1000:.3f}")
                elif 'kg' in units.lower() and 'm-2' in units.lower() and 's-1' in units.lower():
                    print("  💡 kg/m²/s egység - egyenértékű mm/s-val")
                    print(f"     Havi mm becslés: {precip_data.mean() * 30.44 * 24 * 3600:.1f}")
            else:
                print("  ⚠️ Nincs egység információ")
        
        temp_ds.close()
        precip_ds.close()
        
        print(f"\n✅ {location_name} helyszín elemzés befejezve")
        
    except Exception as e:
        print(f"❌ Hiba a helyszín elemzése során: {e}")

def main():
    """Fő diagnosztikai függvény"""
    
    print("NetCDF FÁJLOK DIAGNOSZTIKÁJA")
    print("="*60)
    print("Cél: ERA5 adatok pontos egységeinek és struktúrájának megértése")
    
    # Fájl elérési utak
    temp_path = "data/temperature_1991_2020.nc"
    precip_path = "data/precipitation_1991_2020.nc"
    
    # Hőmérséklet fájl elemzése
    analyze_netcdf_file(temp_path, "HŐMÉRSÉKLET FÁJL")
    
    # Csapadék fájl elemzése  
    analyze_netcdf_file(precip_path, "CSAPADÉK FÁJL")
    
    # Konkrét helyszín elemzése
    analyze_specific_location(temp_path, precip_path, 47.5, 19.0, "Budapest")
    
    print(f"\n{'='*60}")
    print("DIAGNOSZTIKA BEFEJEZVE")
    print("="*60)
    print("A fenti információk alapján meghatározható:")
    print("1. Az adatok pontos egységei")
    print("2. A szükséges konverziók (ha vannak)")
    print("3. Az időbeli felbontás és tartomány")
    print("4. A térbeli koordináta rendszer")
    

if __name__ == "__main__":
    main()