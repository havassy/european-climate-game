// Játékmód kezelés
class GameModeManager {
    constructor(climateGame) {
        this.climateGame = climateGame;
        this.currentMode = 'test'; // 'test' vagy 'learn'
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
        // Jelenlegi teszt mód logika marad
        console.log('Teszt mód aktív');
        // Itt később további módosítások jöhetnek
    }
    
    enableLearnMode() {
        // Tanulás mód logika
        console.log('Tanulás mód aktív');
        // Itt később kifejlesztjük a térképre kattintás logikát
    }
}