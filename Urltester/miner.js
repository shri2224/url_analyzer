// Dummy miner script for security analysis test
console.log("Miner started... (simulation)");
function mine() {
    let x = 0;
    while (true) { x++; } // Heavy loop simulation
}
// mine(); // Commented out to prevent browser lockup during simple serve
