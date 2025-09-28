// European Climate Game - JavaScript logika (JAVÍTOTT VERZIÓ)
// Valós ERA5 adatokkal működő klímajáték

class ClimateGame {
    constructor() {
        this.climateData = null;
        this.currentCity = null;
	this.hasGuessed = false;
	this.recentCities = [];	
        this.gameLevel = 1; // 1 = régió, 2 = pontos város
        this.gameStats = {
            score: 0,
            round: 1,
            correct: 0,
            total: 0,
            regionCorrect: 0
        };
        this.map = null;
        this.guessMarker = null;
        this.answerMarker = null;
        
        this.months = ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D'];
        
        this.regionColors = {
            north: '#4A90E2',    // Kék
            west: '#7ED321',     // Zöld  
            south: '#F5A623',    // Narancssárga
            central: '#D0021B',  // Piros
            east: '#9013FE'      // Lila
        };
        
        this.regionNames = {
            north: 'Észak-Európa',
            west: 'Nyugat-Európa', 
            south: 'Dél-Európa',
            central: 'Közép-Európa',
            east: 'Kelet-Európa'
        };
    }
    
    async init() {
        console.log('Climate Game inicializálás...');
        
        try {
            // JSON adatok betöltése - JAVÍTOTT VERZIÓ
            await this.loadClimateData();
            
            // Ellenőrizzük hogy sikerült-e betölteni
            if (!this.climateData) {
                console.error('Klímaadat betöltés sikertelen!');
                return;
            }
            
            // Térkép inicializálás
            this.initMap();
            
            // Új játék indítása
            this.newGame();
            
            console.log('Climate Game kész!');
        } catch (error) {
            console.error('Climate Game inicializálási hiba:', error);
            this.showError('A játék inicializálása sikertelen. Próbáld frissíteni az oldalt.');
        }
    }
    
    async loadClimateData() {
        try {
            console.log('JSON betöltés indítása...');
            const response = await fetch('js/climate_data.json');
            
            if (!response.ok) {
                throw new Error(`HTTP hiba! status: ${response.status}`);
            }
            
            this.climateData = await response.json();
            console.log(`Betöltve ${this.climateData.cities ? Object.keys(this.climateData.cities).length : 0} város adata`);
            
            // Ellenőrizzük hogy valóban van-e adat
            if (!this.climateData || !this.climateData.cities) {
                throw new Error('Érvénytelen JSON struktúra');
            }
            
            return true;
        } catch (error) {
            console.error('Hiba a klímaadat betöltésekor:', error);
            // Fallback: demo adatok használata
            console.log('Demo adatok használata...');
            this.climateData = this.createDemoData();
            return false;
        }
    }
    
    showError(message) {
        const resultElement = document.getElementById('result');
        if (resultElement) {
            resultElement.innerHTML = `<strong>Hiba:</strong> ${message}`;
            resultElement.className = 'result-panel info';
        }
    }
    
    createDemoData() {
        // Fallback demo adatok ha a JSON nem tölthetö be
        return {
            metadata: {
                source: "Demo adatok",
                cities_count: 3
            },
            cities: {
                "Budapest": {
                    region: "central",
                    country: "Magyarország",
                    coordinates: { target: [47.50, 19.04] },
                    temperature: [0, 2, 7, 12, 17, 21, 23, 22, 17, 12, 6, 1],
                    precipitation: [31, 32, 30, 36, 66, 64, 72, 60, 53, 41, 46, 40]
                },
                "London": {
                    region: "west",
                    country: "Egyesült Királyság", 
                    coordinates: { target: [51.51, -0.13] },
                    temperature: [4, 5, 7, 9, 13, 16, 18, 18, 15, 11, 7, 5],
                    precipitation: [55, 40, 42, 44, 49, 45, 57, 59, 49, 69, 59, 55]
                },
                "Madrid": {
                    region: "south",
                    country: "Spanyolország",
                    coordinates: { target: [40.42, -3.70] },
                    temperature: [6, 8, 12, 14, 18, 24, 27, 26, 22, 16, 10, 7],
                    precipitation: [47, 35, 26, 47, 52, 25, 15, 10, 28, 49, 56, 56]
                }
            }
        };
    }
    
    initMap() {
        // Leaflet térkép inicializálás
        this.map = L.map('map').setView([54.5, 15.0], 4);
        
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(this.map);
        
        // Kattintás eseménykezelő
        this.map.on('click', (e) => {
                if (this.currentCity && gameModeManager && gameModeManager.currentMode === 'test') {
                this.makeGuess(e.latlng);
            }
        });
    }
    
    selectRandomCity() {
    	if (!this.climateData || !this.climateData.cities) {
        	console.error('Nincs elérhető klímaadat!');
        	this.showError('Klímaadatok nem elérhetők. Próbáld frissíteni az oldalt.');
        	return;
    	}
    
    	const allCityNames = Object.keys(this.climateData.cities);
    
    	// Elérhető városok szűrése (kizárva az utolsó 5-öt)
    	let availableCities = allCityNames.filter(city => !this.recentCities.includes(city));
    
    	// Ha nincs elérhető város, nullázás és újra próbálkozás
    	if (availableCities.length === 0) {
        	this.recentCities = [];
        	availableCities = allCityNames;
    	}
    
    	// Random kiválasztás az elérhető városokból
    	const randomIndex = Math.floor(Math.random() * availableCities.length);
    	this.currentCity = availableCities[randomIndex];
    	this.hasGuessed = false;
    
    	// Recent cities frissítése
    	this.recentCities.push(this.currentCity);
    	if (this.recentCities.length > 5) {
        this.recentCities.shift(); // Első elem törlése
    	}
    
    	// Diagram rajzolása
    	this.drawClimateChart(this.currentCity);
    
    	// Statisztikák megjelenítése
    	this.updateClimateStats(this.currentCity);
    
    	// UI frissítése
    	this.updateQuestionText();
	}
    
    updateQuestionText() {
        const questionElement = document.getElementById('challenge-text');
        if (questionElement) {
            questionElement.textContent = 'Melyik európai fővárosra jellemző ez a klíma?';
        }
    }
    
    drawClimateChart(cityName) {
        const city = this.climateData.cities[cityName];
        if (!city) {
            console.error('Város nem található:', cityName);
            return;
        }
        
        const canvas = document.getElementById('climateChart');
        if (!canvas) {
            console.error('Canvas elem nem található!');
            return;
        }
        
        const ctx = canvas.getContext('2d');
        
        // Canvas törlése
        ctx.fillStyle = 'white';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Diagram dimenziók
        const chartLeft = 60;
        const chartRight = 440;
        const chartTop = 30;
        const chartBottom = 280;
        const chartWidth = chartRight - chartLeft;
        const chartHeight = chartBottom - chartTop;
        
        // Skálák meghatározása
        const temps = city.temperature;
        const precips = city.precipitation;
        
        // Skálák meghatározása - intelligens hőmérséklet tartomány (JAVÍTOTT)
        const tempMin_raw = Math.min(...temps);
        const tempMax_raw = Math.max(...temps);

        let tempMin, tempMax;

        if (tempMin_raw < 0) {
            // Ha van negatív hőmérséklet, intelligens skálázás
            const range = tempMax_raw - tempMin_raw;
            const margin = Math.max(2, range * 0.1); // Minimum 2°C margó, vagy 10% a tartományból
            
            tempMin = Math.floor(tempMin_raw - margin);
            tempMax = Math.ceil(tempMax_raw + margin);
            
            // Ha a minimális érték csak kicsit negatív (-5°C alatt), akkor finomhangolás
            if (tempMin_raw > -5) {
                tempMin = Math.floor(tempMin_raw / 5) * 5; // 5°C-os lépésekhez igazítás
            }
        } else {
            // Ha nincs negatív hőmérséklet, 0-tól indulunk
            tempMin = 0;
            tempMax = Math.ceil(tempMax_raw + 3);
        }

        // Biztosítjuk, hogy a skála legalább 15°C széles legyen a jobb olvashatóságért
        const minRange = 15;
        if (tempMax - tempMin < minRange) {
            const center = (tempMax + tempMin) / 2;
            tempMin = Math.floor(center - minRange/2);
            tempMax = Math.ceil(center + minRange/2);
        }

        const tempRange = tempMax - tempMin;
        const precipMax = Math.max(...precips) + 20;
        
        // Tengelyek és rács rajzolása
        this.drawAxes(ctx, chartLeft, chartRight, chartTop, chartBottom, tempMin, tempMax, precipMax);
        
        // 0°C és 0mm vonalak ugyanazon magasságban
        const zeroY = chartBottom - ((0 - tempMin) / tempRange) * chartHeight;
        ctx.strokeStyle = '#666';
        ctx.lineWidth = 1;
        ctx.setLineDash([3, 3]);
        ctx.beginPath();
        ctx.moveTo(chartLeft, zeroY);
        ctx.lineTo(chartRight, zeroY);
        ctx.stroke();
        ctx.setLineDash([]);

        // Csapadék oszlopok (kék)
        ctx.fillStyle = 'rgba(70, 130, 180, 0.7)';
        const monthWidth = chartWidth / 12;
        
        for (let i = 0; i < 12; i++) {
            const x = chartLeft + i * monthWidth + monthWidth * 0.25;
            const barWidth = monthWidth * 0.5;
            const barHeight = (precips[i] / precipMax) * chartHeight;
            const y = chartBottom - barHeight;
            
            ctx.fillRect(x, y, barWidth, barHeight);
        }
        
        // Hőmérséklet vonal (piros)
        ctx.strokeStyle = '#DC143C';
        ctx.lineWidth = 3;
        ctx.beginPath();
        
        for (let i = 0; i < 12; i++) {
            const x = chartLeft + (i + 0.5) * monthWidth;
            const y = chartBottom - ((temps[i] - tempMin) / tempRange) * chartHeight;
            
            if (i === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        }
        ctx.stroke();
    }
    
    drawAxes(ctx, left, right, top, bottom, tempMin, tempMax, precipMax) {
        const height = bottom - top;
        const tempRange = tempMax - tempMin;
        
        // Bal tengely (Hőmérséklet)
        ctx.strokeStyle = '#333';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(left, top);
        ctx.lineTo(left, bottom);
        ctx.stroke();
        
        // Hőmérséklet címkék és rács
        ctx.fillStyle = '#333';
        ctx.font = '12px Arial';
        ctx.textAlign = 'right';
        
        const tempStep = Math.ceil(tempRange / 8);
        for (let temp = Math.ceil(tempMin / tempStep) * tempStep; temp <= tempMax; temp += tempStep) {
            const y = bottom - ((temp - tempMin) / tempRange) * height;
            ctx.fillText(temp + '°C', left - 10, y + 4);
            
            // Rács vonalak
            ctx.strokeStyle = '#eee';
            ctx.beginPath();
            ctx.moveTo(left, y);
            ctx.lineTo(right, y);
            ctx.stroke();
        }
        
        // Jobb tengely (Csapadék)
        ctx.strokeStyle = '#333';
        ctx.beginPath();
        ctx.moveTo(right, top);
        ctx.lineTo(right, bottom);
        ctx.stroke();
        
        // Csapadék címkék
        ctx.textAlign = 'left';
        const precipStep = Math.ceil(precipMax / 6 / 10) * 10;
        for (let precip = 0; precip <= precipMax; precip += precipStep) {
            const y = bottom - (precip / precipMax) * height;
            ctx.fillText(precip + 'mm', right + 10, y + 4);
        }
        
        // Alsó tengely
        ctx.strokeStyle = '#333';
        ctx.beginPath();
        ctx.moveTo(left, bottom);
        ctx.lineTo(right, bottom);
        ctx.stroke();
        
        // Hónap címkék
        ctx.textAlign = 'center';
        const monthWidth = (right - left) / 12;
        for (let i = 0; i < 12; i++) {
            const x = left + (i + 0.5) * monthWidth;
            ctx.fillText(this.months[i], x, bottom + 20);
        }
    }
    
    makeGuess(latlng) {
    	// Korábbi marker törlése
    	if (this.guessMarker) {
        	this.map.removeLayer(this.guessMarker);
    	}
    
    	// Távolság számítása
    	const cityData = this.climateData.cities[this.currentCity];
    	const actualCoords = cityData.coordinates.target;
    	const distance = Math.round(L.latLng(actualCoords).distanceTo(latlng) / 1000);
    
    	// Szín meghatározása távolság alapján
    	let markerColor;
    	if (distance <= 20) {
        	markerColor = '#48bb78'; // zöld (success)
    	} else if (distance <= 100) {
        	markerColor = '#ed8936'; // narancssárga (good)
    	} else if (distance <= 500) {
        	markerColor = '#ed8936'; // narancssárga (good)
    	} else {
        	markerColor = '#4299e1'; // kék (info)
    	}
    
    	// Új tipp marker a megfelelő színnel
    	this.guessMarker = L.marker(latlng, {
        	icon: L.icon({
            	iconUrl: 'data:image/svg+xml;base64,' + btoa(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="${markerColor}"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>`),
            	iconSize: [30, 30],
            	iconAnchor: [15, 30]
        	})
    	}).addTo(this.map);
    
    // Értékelés
    this.evaluateGuess(latlng);
}
    
    evaluateGuess(latlng) {
    const cityData = this.climateData.cities[this.currentCity];
    const actualCoords = cityData.coordinates.target;
    
    // Távolság számítása
    const distance = Math.round(L.latLng(actualCoords).distanceTo(latlng) / 1000);
    
    // Pontszámítás - csak ha még nem tippelt
    let points = 0;
    if (!this.hasGuessed) {  // <-- ÚJ: csak első tipp ad pontot
        if (distance <= 20) {
            points = 100;
        } else if (distance >= 1000) {
            points = 0;
        } else {
            points = Math.round(100 - ((distance - 20) * 100) / (1000 - 20));
            points = Math.max(0, Math.min(100, points));
        }
        
        this.gameStats.score += points;  // Pont hozzáadás csak egyszer
        if (points > 0) this.gameStats.correct++;
    }
    
    // Eredmény szöveg (mindig mutatja a távolságot)
    let resultText = '';
    let resultClass = 'info';
    
    if (distance <= 20) {
        resultText = `Kiváló! Csak ${distance} km-re vagy!`;
        resultClass = 'success';
    } else if (distance <= 100) {
        resultText = `Jó! ${distance} km távolság.`;
        resultClass = 'good';
    } else if (distance <= 500) {
        resultText = `Közepes. ${distance} km távolság.`;
        resultClass = 'good';
    } else {
        resultText = `Távol vagy. ${distance} km távolság.`;
        resultClass = 'info';
    }
    
    // Ha nem az első tipp, jelezd
    if (this.hasGuessed) {
        resultText += " (Nincs további pont)";
    }
    
    this.hasGuessed = true;  // <-- ÚJ: jelöld hogy volt már tipp
    this.gameStats.total++;  // Total mindig nő
    
    this.updateStats();
    this.showResult(resultText, resultClass, points);
}
    
    getRegionFromCoords(lat, lng) {
        // Egyszerű régió meghatározás koordináták alapján
        if (lat > 58) return 'north';           // Skandinávia
        if (lng < 2 && lat > 50) return 'west'; // Brit-szigetek
        if (lng < 5 && lat < 52) return 'west'; // Atlanti Európa
        if (lat < 45) return 'south';           // Mediterráneum  
        if (lng > 23) return 'east';            // Kelet-Európa
        return 'central';                       // Közép-Európa
    }
    
    showResult(text, className, points) {
        const resultElement = document.getElementById('result');
        if (resultElement) {
            resultElement.innerHTML = text + `<br><strong>+${points} pont</strong>`;
            resultElement.className = `result-panel ${className}`;
        }
    }
    
    updateStats() {
        const elements = {
            score: document.getElementById('score'),
            round: document.getElementById('round'), 
            correct: document.getElementById('correct'),
            total: document.getElementById('total')
        };
        
        if (elements.score) elements.score.textContent = this.gameStats.score;
        if (elements.round) elements.round.textContent = this.gameStats.round;
        if (elements.correct) elements.correct.textContent = this.gameStats.correct;
        if (elements.total) elements.total.textContent = this.gameStats.total;
    }
    
    showAnswer() {
        if (!this.currentCity) return;
        
        const cityData = this.climateData.cities[this.currentCity];
        const coords = cityData.coordinates.target;
        
        // Válasz marker hozzáadása
        this.answerMarker = L.marker(coords, {
            icon: L.icon({
                iconUrl: 'data:image/svg+xml;base64,' + btoa('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="green"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>'),
                iconSize: [35, 35],
                iconAnchor: [17, 35]
            })
        }).addTo(this.map)
        .bindPopup(`<strong>${this.currentCity}</strong><br>${cityData.country}<br>Régió: ${this.regionNames[cityData.region]}`)
        .openPopup();
        
        // Nagyítás a válaszra
        this.map.setView(coords, 8);
        
    }
    
    nextRound() {
        // Markerek törlése
        if (this.guessMarker) {
            this.map.removeLayer(this.guessMarker);
            this.guessMarker = null;
        }
        if (this.answerMarker) {
            this.map.removeLayer(this.answerMarker);
            this.answerMarker = null;
        }
        
        // Térkép visszaállítása
        this.map.setView([54.5, 15.0], 4);
        
        // Eredmény visszaállítása
        const resultElement = document.getElementById('result');
        if (resultElement) {
            resultElement.innerHTML = 'Eredmény visszajelző panel';
            resultElement.className = 'result-panel';
        }
        
        // Kör növelése
        this.gameStats.round++;
        this.updateStats();
        
        // Új város kiválasztása
        this.selectRandomCity();
        
    }
    
    newGame() {
        // Statisztikák visszaállítása
        this.gameStats = {
            score: 0,
            round: 1,
            correct: 0,
            total: 0,
            regionCorrect: 0
        };
        
        // Markerek törlése
        if (this.guessMarker) {
            this.map.removeLayer(this.guessMarker);
            this.guessMarker = null;
        }
        if (this.answerMarker) {
            this.map.removeLayer(this.answerMarker);
            this.answerMarker = null;
        }
        
        // Térkép visszaállítása
        if (this.map) {
            this.map.setView([54.5, 15.0], 4);
        }
        
        // UI visszaállítása
        const resultElement = document.getElementById('result');
        if (resultElement) {
            resultElement.innerHTML = 'Eredmény visszajelző panel';
            resultElement.className = 'result-panel';
        }
        
        // Statisztikák és új város
        this.updateStats();
        this.selectRandomCity();
    }

    updateClimateStats(cityName) {
        const city = this.climateData.cities[cityName];
        if (!city) return;
    
        // Évi középhőmérséklet számítása
        const avgTemp = (city.temperature.reduce((a, b) => a + b, 0) / 12).toFixed(1);
    
        // Évi csapadékátlag számítása  
        const avgPrecip = Math.round(city.precipitation.reduce((a, b) => a + b, 0));
    
        // Valós tengerszint feletti magasság adatok
        const elevationData = {
            "Stockholm": 40,
            "Oslo": 26,
            "Helsinki": 13,
            "London": 11,
            "Dublin": 17,
            "Amszterdam": 14,
            "Madrid": 660,
            "Róma": 24,
            "Athén": 85,
            "Berlin": 34,
            "Bécs": 171,
            "Budapest": 110,
            "Varsó": 108,
            "Bukarest": 72
        };

        const elevation = elevationData[cityName] || 100; // fallback érték
        
        // HTML frissítése
        const statsElement = document.getElementById('climate-stats');
        if (statsElement) {
            statsElement.innerHTML = `
                <strong>Évi kh.:</strong> ${avgTemp}°C | <strong>Évi cs.á.:</strong> ${avgPrecip}mm | <strong>Tszfm.:</strong> ${elevation}m
            `;
        }
    }
}

// Globális game objektum
let climateGame = null;
let gameModeManager = null;

// Inicializálás amikor a DOM betöltődött
document.addEventListener('DOMContentLoaded', async function() {
    console.log('DOM betöltve, Climate Game inicializálás...');
    
    try {
        climateGame = new ClimateGame();
        await climateGame.init();
        
        // Játékmód manager inicializálása
        gameModeManager = new GameModeManager(climateGame);
        console.log('Game Mode Manager inicializálva');
    } catch (error) {
        console.error('Játék inicializálási hiba:', error);
    }
});

// Globális függvények a HTML gombokhoz
function newGame() {
    if (climateGame) {
        climateGame.newGame();
    }
}

function showAnswer() {
    if (climateGame) {
        climateGame.showAnswer();
    }
}

function nextRound() {
    if (climateGame) {
        climateGame.nextRound();
    }
}