// Játékmód kezelés
class GameModeManager {
    constructor(climateGame) {
        this.climateGame = climateGame;
        this.currentMode = 'test'; // 'test' vagy 'learn'
        this.cityMarkers = []; // Fontos: markers tömb inicializálása
        this.initEventListeners();
    }
    
    initEventListeners() {
        document.getElementById('testModeBtn').addEventListener('click', () => {
            this.switchMode('test');
        });
        
        document.getElementById('learnModeBtn').addEventListener('click', () => {
            this.switchMode('learn');
        });
    }
    
    switchMode(mode) {
        this.currentMode = mode;
        
        // Gombok aktív állapotának frissítése
        document.querySelectorAll('.btn-mode').forEach(btn => {
            btn.classList.remove('active');
        });
        
        if (mode === 'test') {
            document.getElementById('testModeBtn').classList.add('active');
            this.enableTestMode();
        } else {
            document.getElementById('learnModeBtn').classList.add('active');
            this.enableLearnMode();
        }
    }
    
    enableTestMode() {
        console.log('Teszt mód aktív');
	
	// Új játék gomb láthatóvá tétele
	const newGameBtn = document.querySelector('button[onclick="newGame()"]');
	if (newGameBtn) {
   	newGameBtn.style.visibility = 'visible';
    	newGameBtn.style.cursor = 'pointer';
	}
        
        // Város markerek eltávolítása
        if (this.cityMarkers) {
            this.cityMarkers.forEach(marker => this.climateGame.map.removeLayer(marker));
            this.cityMarkers = [];
        }
        
        // Eredeti kérdésszöveg visszaállítása
        const questionElement = document.getElementById('challenge-text');
        if (questionElement) {
            questionElement.textContent = 'Melyik európai fővárosra jellemző ez a klíma?';
        }
        
        // Teszt mód vezérlők megjelenítése
        document.getElementById('showAnswerBtn').style.display = 'inline-block';
        document.getElementById('nextRoundBtn').style.display = 'inline-block';
        
        // Diagram és statisztikák megjelenítése
        document.getElementById('climateChart').style.display = 'block';
        document.getElementById('climate-stats').style.display = 'block';
    }
    
    enableLearnMode() {
        console.log('Tanulás mód aktív');
	
	// Új játék gomb láthatatlanná tétele (de helyet foglal)
	const newGameBtn = document.querySelector('button[onclick="newGame()"]');
	if (newGameBtn) {
    	newGameBtn.style.visibility = 'hidden';
    	newGameBtn.style.cursor = 'default';
	}
        
        // Kérdésszöveg megváltoztatása
        const questionElement = document.getElementById('challenge-text');
        if (questionElement) {
            questionElement.textContent = 'Válassz egy várost a térképről és fedezd fel a klímáját!';
        }
        
        // Teszt mód vezérlők elrejtése
        document.getElementById('showAnswerBtn').style.display = 'none';
        document.getElementById('nextRoundBtn').style.display = 'none';
        
        // Diagram és statisztikák elrejtése kezdetben
        document.getElementById('climateChart').style.display = 'none';
        document.getElementById('climate-stats').style.display = 'none';
        
        // Város markerek megjelenítése
        this.showCityMarkers();
    }

    showCityMarkers() {
    	console.log('Város markerek megjelenítése...');
    
    	if (this.cityMarkers) {
       	 this.cityMarkers.forEach(marker => this.climateGame.map.removeLayer(marker));
    	}
    	this.cityMarkers = [];
    
    	const cities = this.climateGame.climateData.cities;
    	console.log('Elérhető városok:', Object.keys(cities)); // Debug: összes város
    
    	for (const [cityName, cityData] of Object.entries(cities)) {
    		const coords = cityData.coordinates.target;
    		const regionColor = this.getRegionColor(cityData.region);
    
    		console.log(`Marker létrehozása: ${cityName}, régió: ${cityData.region}, szín: ${regionColor}`); // Most már működik
        
        	try {
            	const marker = L.marker(coords, {
    			icon: L.divIcon({
        			className: 'custom-marker',
        			html: `<div style="background-color: ${regionColor}; width: 20px; height: 20px; border-radius: 50%; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);"></div>`,
        			iconSize: [20, 20],
        			iconAnchor: [10, 10]
    			})
		}).addTo(this.climateGame.map)

            	.bindPopup(`<strong>${cityName}</strong><br>${cityData.country}`)
            	.on('click', () => {
                	this.displayCityInfo(cityName);
            	});
            
            	this.cityMarkers.push(marker);
            	console.log(`${cityName} marker sikeresen hozzáadva`); // Debug: siker
        	} catch (error) {
            	console.error(`Hiba ${cityName} marker létrehozásakor:`, error); // Debug: hiba
        	}
    	}
    
    console.log(`Összesen ${this.cityMarkers.length} marker létrehozva`); // Debug: összesen
}

    getRegionColor(region) {
        const colors = {
            north: '#4A90E2',
            west: '#7ED321', 
            south: '#F5A623',
            central: '#D0021B',
            east: '#9013FE'
        };
        return colors[region] || '#666666';
    }

    displayCityInfo(cityName) {
        console.log(`Kiválasztott város: ${cityName}`);
        
        // Diagram és statisztikák megjelenítése
        document.getElementById('climateChart').style.display = 'block';
        document.getElementById('climate-stats').style.display = 'block';
        
        // Város klímadiagramjának rajzolása
        this.climateGame.drawClimateChart(cityName);
        this.climateGame.updateClimateStats(cityName);
        
        // Kérdésszöveg frissítése
        const questionElement = document.getElementById('challenge-text');
        if (questionElement) {
            questionElement.textContent = `${cityName} klímája`;
        }
    }
}