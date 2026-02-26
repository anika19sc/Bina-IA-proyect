const { app, BrowserWindow, Menu } = require('electron');
const path = require('path');
const url = require('url');
const { spawn } = require('child_process');

let win;
let backendProcess;

const PY_DIST_FOLDER = 'backend-dist';
const PY_FOLDER = '../backend';
const PY_MODULE = 'start'; // without .py suffix

const textDecoder = new TextDecoder('utf-8');

const guessPackaged = () => {
    const fullPath = path.join(__dirname, PY_DIST_FOLDER);
    return require('fs').existsSync(fullPath);
};

const getScriptPath = () => {
    if (!app.isPackaged) {
        return path.join(__dirname, PY_FOLDER, PY_MODULE + '.py');
    }
    if (process.platform === 'win32') {
        return path.join(process.resourcesPath, 'backend.exe');
    }
    return path.join(process.resourcesPath, 'backend');
};


function startBackend() {
    let script = getScriptPath();
    console.log(`Starting backend from: ${script}`);

    if (app.isPackaged || script.endsWith('.exe')) {
        backendProcess = spawn(script);
    } else {
        // In dev, usually python is in path.
        // If specific python needed, needs configuration.
        backendProcess = spawn('python', [script]);
    }

    if (backendProcess != null) {
        console.log('Backend process started');
        backendProcess.stdout.on('data', (data) => {
            console.log(`BACKEND: ${textDecoder.decode(data)}`);
        });
        backendProcess.stderr.on('data', (data) => {
            console.error(`BACKEND ERROR: ${textDecoder.decode(data)}`);
        });
    }
}

function createWindow() {
    win = new BrowserWindow({
        width: 1200,
        height: 800,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false
        },
        icon: path.join(__dirname, 'src/assets/logo_Escritorio.png')
    });

    startBackend();

    // Wait a moment for backend? Or just load Angular and let it retry connection.
    // Angular usually retries or we can add a splash screen.

    // Check if we are running in dev mode
    const args = process.argv.slice(1);
    const serve = args.some(val => val === '--serve');

    if (serve) {
        win.loadURL('http://localhost:4200');
    } else {
        win.loadURL(
            url.format({
                pathname: path.join(__dirname, 'dist/bina-legal/browser/index.html'),
                protocol: 'file:',
                slashes: true
            })
        );
    }

    // win.webContents.openDevTools();

    win.on('closed', () => {
        win = null;
    });

    // Create Spanish Menu
    const template = [
        {
            label: 'Archivo',
            submenu: [
                { label: 'Salir', role: 'quit' }
            ]
        },
        {
            label: 'Edición',
            submenu: [
                { label: 'Deshacer', role: 'undo' },
                { label: 'Rehacer', role: 'redo' },
                { type: 'separator' },
                { label: 'Cortar', role: 'cut' },
                { label: 'Copiar', role: 'copy' },
                { label: 'Pegar', role: 'paste' }
            ]
        },
        {
            label: 'Ver',
            submenu: [
                { label: 'Recargar', role: 'reload' },
                { label: 'Pantalla Completa', role: 'togglefullscreen' },
                { label: 'Herramientas de Desarrollo', role: 'toggledevtools' }
            ]
        },
        {
            label: 'Ventana',
            submenu: [
                { label: 'Minimizar', role: 'minimize' },
                { label: 'Cerrar', role: 'close' }
            ]
        },
        {
            label: 'Ayuda',
            submenu: [
                { label: 'Acerca de Bina IA', role: 'about' }
            ]
        }
    ];

    const menu = Menu.buildFromTemplate(template);
    Menu.setApplicationMenu(menu);
}

app.on('ready', createWindow);

app.on('will-quit', () => {
    if (backendProcess) {
        console.log('Killing backend process');
        backendProcess.kill();
        backendProcess = null;
    }
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (win === null) {
        createWindow();
    }
});
