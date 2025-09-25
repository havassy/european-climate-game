#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NetCDF fájlok tesztelése - javított verzió
Windows fájlrendszer kompatibilitás javítással
"""

import os
import sys

def peek_netcdf_structure():
    """Megnézi a NetCDF fájl alapvető struktúráját"""
    print("NetCDF struktúra vizsgálata...")
    
    try:
        import xarray as xr
        
        # Aktuális munkamappa
        current_dir = os.getcwd()
        print(f"Aktuális mappa: {current_dir}")
        
        # Temperature fájl teljes elérési útvonala
        temp_path = os.path.join(current_dir, "data", "temperature_1991_2020.nc")
        precip_path = os.path.join(current_dir, "data", "precipitation_1991_2020.nc")
        
        print(f"Keresett útvonal (hőmérséklet): {temp_path}")
        print(f"Fájl létezik: {os.path.exists(temp_path)}")
        
        if os.path.exists(temp_path):
            print(f"\nHőmérséklet fájl struktúra:")
            ds_temp = xr.open_dataset(temp_path)
            
            print(f"Dimenziók: {list(ds_temp.dims.keys())}")
            print(f"Változók: {list(ds_temp.data_vars.keys())}")  
            print(f"Koordináták: {list(ds_temp.coords.keys())}")
            
            # Koordináta információk
            for coord_name in ds_temp.coords:
                coord = ds_temp.coords[coord_name]
                if coord_name in ['longitude', 'lon']:
                    print(f"Hosszúság: {coord.min().values:.2f} - {coord.max().values:.2f}")
                elif coord_name in ['latitude', 'lat']: 
                    print(f"Szélesség: {coord.min().values:.2f} - {coord.max().values:.2f}")
                elif coord_name == 'time':
                    print(f"Időtartomány: {coord.min().values} - {coord.max().values}")
            
            # Első adatváltozó részletei
            if ds_temp.data_vars:
                var_name = list(ds_temp.data_vars.keys())[0]
                var_data = ds_temp[var_name]
                print(f"Első változó '{var_name}' alakja: {var_data.shape}")
                
            ds_temp.close()
            print("Hőmérséklet fájl bezárva.")
        
        # Csapadék fájl ellenőrzése
        if os.path.exists(precip_path):
            print(f"\nCsapadék fájl struktúra:")
            ds_precip = xr.open_dataset(precip_path)
            
            print(f"Dimenziók: {list(ds_precip.dims.keys())}")
            print(f"Változók: {list(ds_precip.data_vars.keys())}")
            
            # Első adatváltozó részletei
            if ds_precip.data_vars:
                var_name = list(ds_precip.data_vars.keys())[0]
                var_data = ds_precip[var_name]
                print(f"Első változó '{var_name}' alakja: {var_data.shape}")
            
            ds_precip.close()
            print("Csapadék fájl bezárva.")
        
        return True
        
    except Exception as e:
        print(f"Hiba a NetCDF vizsgálat közben: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Fő tesztfüggvény"""
    print("European Climate Game - NetCDF Teszt (Javított)")
    print("=" * 50)
    
    # Könyvtárak ellenőrzése
    try:
        import xarray as xr
        print("xarray elérhető")
    except ImportError:
        print("xarray hiányzik!")
        return
    
    try:
        import netCDF4
        print("netCDF4 elérhető") 
    except ImportError:
        print("netCDF4 hiányzik!")
        return
    
    # NetCDF struktúra vizsgálata
    if peek_netcdf_structure():
        print("\nSikeres NetCDF elemzés!")
        print("Következő lépés: városok koordinátáinak meghatározása")
    else:
        print("\nHiba történt a NetCDF elemzés során")

if __name__ == "__main__":
    main()