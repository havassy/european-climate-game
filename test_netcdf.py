#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NetCDF fájlok tesztelése - első lépés
Cél: Megnézni, hogy mit tartalmaznak a climate adatfájlok
"""

import os

def check_files():
    """Ellenőrzi, hogy a NetCDF fájlok elérhetők-e"""
    print("🔍 NetCDF fájlok ellenőrzése...")
    
    data_dir = "data"
    files_to_check = [
        "temperature_1991_2020.nc",
        "precipitation_1991_2020.nc"
    ]
    
    for filename in files_to_check:
        filepath = os.path.join(data_dir, filename)
        if os.path.exists(filepath):
            size_mb = os.path.getsize(filepath) / (1024 * 1024)
            print(f"✅ {filename}: {size_mb:.1f} MB")
        else:
            print(f"❌ {filename}: Nem található!")
    
    return True

def test_xarray_import():
    """Teszteli, hogy a szükséges könyvtárak elérhetők-e"""
    print("\n📚 Python könyvtárak ellenőrzése...")
    
    try:
        import xarray as xr
        print("✅ xarray elérhető")
    except ImportError:
        print("❌ xarray hiányzik! Telepítsd: pip install xarray")
        return False
    
    try:
        import netCDF4
        print("✅ netCDF4 elérhető") 
    except ImportError:
        print("❌ netCDF4 hiányzik! Telepítsd: pip install netCDF4")
        return False
    
    try:
        import pandas as pd
        print("✅ pandas elérhető")
    except ImportError:
        print("❌ pandas hiányzik! Telepítsd: pip install pandas")
        return False
    
    return True

def peek_netcdf_structure():
    """Megnézi a NetCDF fájl alapvető struktúráját"""
    print("\n🔬 NetCDF struktúra vizsgálata...")
    
    try:
        import xarray as xr
        
        # Temperature fájl vizsgálata
        temp_path = os.path.join("data", "temperature_1991_2020.nc")
        if os.path.exists(temp_path):
            print(f"\n📊 {temp_path} struktúra:")
            ds = xr.open_dataset(temp_path)
            
            print(f"Dimenziók: {list(ds.dims.keys())}")
            print(f"Változók: {list(ds.data_vars.keys())}")
            print(f"Koordináták: {list(ds.coords.keys())}")
            
            # Koordináta tartományok
            if 'longitude' in ds.coords:
                lon_range = f"{ds.longitude.min().values:.2f} - {ds.longitude.max().values:.2f}"
                print(f"Hosszúság tartomány: {lon_range}")
            
            if 'latitude' in ds.coords:
                lat_range = f"{ds.latitude.min().values:.2f} - {ds.latitude.max().values:.2f}"
                print(f"Szélesség tartomány: {lat_range}")
            
            if 'time' in ds.coords:
                print(f"Időtartomány: {ds.time.min().values} - {ds.time.max().values}")
            
            ds.close()
        
    except Exception as e:
        print(f"❌ Hiba a NetCDF vizsgálat közben: {e}")
        return False
    
    return True

def main():
    """Fő tesztfüggvény"""
    print("🌍 European Climate Game - NetCDF Teszt")
    print("=" * 50)
    
    # Alapvető ellenőrzések
    if not check_files():
        return
    
    if not test_xarray_import():
        print("\n💡 Hiányzó könyvtárak telepítése:")
        print("pip install xarray netcdf4 pandas")
        return
    
    # NetCDF struktúra vizsgálata
    if not peek_netcdf_structure():
        return
    
    print("\n✅ Minden teszt sikeres!")
    print("\n🚀 Következő lépés: konkrét városok adatainak kinyerése")

if __name__ == "__main__":
    main()
