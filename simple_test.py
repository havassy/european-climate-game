#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Egyszerű fájl teszt - NetCDF fájlok alapvető ellenőrzése
"""

import os

def check_file_headers():
    """Ellenőrzi a fájlok első bájtjait"""
    print("Fájlfejlécek ellenőrzése...")
    
    files = [
        "data/temperature_1991_2020.nc",
        "data/precipitation_1991_2020.nc"
    ]
    
    for filepath in files:
        if os.path.exists(filepath):
            print(f"\n{filepath}:")
            print(f"Méret: {os.path.getsize(filepath)} bájt")
            
            # Első 50 bájt olvasása
            try:
                with open(filepath, 'rb') as f:
                    header = f.read(50)
                    print(f"Első 20 bájt (hex): {header[:20].hex()}")
                    
                    # Keresünk NetCDF jelöléseket
                    if b'CDF' in header[:10]:
                        print("✅ NetCDF aláírás található")
                    elif b'HDF' in header[:10]:
                        print("📄 HDF formátum (NetCDF4)")
                    else:
                        print("❓ Ismeretlen formátum")
                        print(f"Első 20 karakter: {header[:20]}")
                        
            except Exception as e:
                print(f"❌ Hiba a fájl olvasásakor: {e}")

def try_different_libraries():
    """Különböző könyvtárakkal próbálja meg megnyitni"""
    print("\nKülönböző könyvtárak tesztelése...")
    
    filepath = "data/temperature_1991_2020.nc"
    
    # 1. Próba: netCDF4 könyvtár közvetlenül
    try:
        import netCDF4
        print("netCDF4 könyvtár próba...")
        ds = netCDF4.Dataset(filepath, 'r')
        print(f"✅ netCDF4: Dimenziók: {list(ds.dimensions.keys())}")
        print(f"✅ netCDF4: Változók: {list(ds.variables.keys())}")
        ds.close()
        return True
    except Exception as e:
        print(f"❌ netCDF4 hiba: {e}")
    
    # 2. Próba: xarray különböző engine-ekkel
    try:
        import xarray as xr
        print("xarray netcdf4 engine próba...")
        ds = xr.open_dataset(filepath, engine='netcdf4')
        print(f"✅ xarray (netcdf4): {list(ds.data_vars.keys())}")
        ds.close()
        return True
    except Exception as e:
        print(f"❌ xarray netcdf4 hiba: {e}")
    
    try:
        print("xarray h5netcdf engine próba...")
        ds = xr.open_dataset(filepath, engine='h5netcdf')
        print(f"✅ xarray (h5netcdf): {list(ds.data_vars.keys())}")
        ds.close()
        return True
    except Exception as e:
        print(f"❌ xarray h5netcdf hiba: {e}")
    
    return False

def main():
    """Fő funkció"""
    print("NetCDF Fájl Diagnosztika")
    print("=" * 40)
    
    check_file_headers()
    
    success = try_different_libraries()
    
    if not success:
        print("\n🤔 Lehetséges problémák:")
        print("1. Fájl sérült vagy nem szabványos NetCDF")
        print("2. Speciális NetCDF4 formátum")
        print("3. Hiányzó függőségek")
        print("\n💡 Javasolt megoldás:")
        print("pip install h5py h5netcdf")
    else:
        print("\n✅ Sikerült megnyitni a fájlt!")

if __name__ == "__main__":
    main()