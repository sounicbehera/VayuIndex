
const { spawn } = require('child_process');

const startProcess = (command, args, cwd = '.') => {
    const proc = spawn(command, args, { cwd, shell: true, stdio: 'inherit' });
    proc.on('error', (err) => console.error(`Failed to start ${command}: ${err}`));
};

console.log("Bootstrapping vayuIndex Architecture...");

// Assuming Docker is already up and backtest is completed
startProcess('uvicorn', ['app.main:app', '--reload', '--port', '8000'], './backend');
startProcess('python', ['pipeline/stream_consumer.py']);
startProcess('npm', ['run', 'dev'], './dashboard');