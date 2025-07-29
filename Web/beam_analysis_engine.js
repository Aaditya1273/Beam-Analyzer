// 3D Beam Analysis Engine
let scene, camera, renderer, controls;
let beam, supports = [], loads = [], forceArrows = [];
let beamLength = 10;
let analysisResults = null;
let animationId;
let isAnimating = false;
let currentChart = 'shear';
let chartInstance = null;

// Material properties
const materials = {
    steel: { E: 200e9, density: 7850, color: 0xcccccc },
    concrete: { E: 30e9, density: 2400, color: 0x888888 },
    wood: { E: 12e9, density: 600, color: 0xd2691e },
    aluminum: { E: 70e9, density: 2700, color: 0xc0c0c0 }
};

// Initialize Three.JS scene
function initThreeJS() {
    const container = document.getElementById('canvas-container');
    
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a1428);
    
    camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
    camera.position.set(15, 10, 15);
    camera.lookAt(0, 0, 0);
    
    renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    container.appendChild(renderer.domElement);
    
    // Add lights
    const ambientLight = new THREE.AmbientLight(0x404040, 0.3);
    scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0x00ffaa, 1);
    directionalLight.position.set(20, 20, 20);
    directionalLight.castShadow = true;
    scene.add(directionalLight);
    
    // Add grid
    const gridHelper = new THREE.GridHelper(50, 50, 0x00ffaa, 0x004455);
    gridHelper.position.y = -2;
    scene.add(gridHelper);
    
    setupMouseControls();
    window.addEventListener('resize', onWindowResize);
    animate();
}

function setupMouseControls() {
    let isDragging = false;
    let previousMousePosition = { x: 0, y: 0 };
    
    renderer.domElement.addEventListener('mousedown', (e) => {
        isDragging = true;
        previousMousePosition = { x: e.clientX, y: e.clientY };
    });
    
    renderer.domElement.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        
        const deltaMove = {
            x: e.clientX - previousMousePosition.x,
            y: e.clientY - previousMousePosition.y
        };
        
        const deltaRotationQuaternion = new THREE.Quaternion()
            .setFromEuler(new THREE.Euler(
                toRadians(deltaMove.y * 0.5),
                toRadians(deltaMove.x * 0.5),
                0,
                'XYZ'
            ));
        
        camera.quaternion.multiplyQuaternions(deltaRotationQuaternion, camera.quaternion);
        previousMousePosition = { x: e.clientX, y: e.clientY };
    });
    
    renderer.domElement.addEventListener('mouseup', () => {
        isDragging = false;
    });
    
    renderer.domElement.addEventListener('wheel', (e) => {
        const scale = e.deltaY > 0 ? 1.1 : 0.9;
        camera.position.multiplyScalar(scale);
    });
}

function toRadians(angle) {
    return angle * (Math.PI / 180);
}

function onWindowResize() {
    const container = document.getElementById('canvas-container');
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
}

function animate() {
    requestAnimationFrame(animate);
    
    if (isAnimating && analysisResults) {
        const time = Date.now() * 0.001;
        animateDeformation(time);
    }
    
    renderer.render(scene, camera);
}

function createBeam() {
    beamLength = parseFloat(document.getElementById('beamLength').value);
    const material = document.getElementById('beamMaterial').value;
    
    if (beam) scene.remove(beam);
    
    const beamGeometry = new THREE.BoxGeometry(beamLength, 0.5, 0.8);
    const beamMaterial = new THREE.MeshPhongMaterial({ 
        color: materials[material].color,
        shininess: 100,
        transparent: true,
        opacity: 0.9
    });
    beam = new THREE.Mesh(beamGeometry, beamMaterial);
    beam.position.set(0, 0, 0);
    beam.castShadow = true;
    beam.receiveShadow = true;
    scene.add(beam);
    
    document.getElementById('supportPosition').max = beamLength;
    document.getElementById('loadPosition').max = beamLength;
    
    updateDisplay();
}

function addSupport() {
    const position = parseFloat(document.getElementById('supportPosition').value);
    const type = document.getElementById('supportType').value;
    
    if (isNaN(position) || position < 0 || position > beamLength) {
        alert('Invalid support position!');
        return;
    }
    
    supports = supports.filter(s => Math.abs(s.position - position) > 0.1);
    
    const supportGroup = new THREE.Group();
    const x = position - beamLength/2;
    
    if (type === 'pin') {
        const geometry = new THREE.ConeGeometry(0.5, 1, 3);
        const material = new THREE.MeshPhongMaterial({ color: 0x00ffaa });
        const support = new THREE.Mesh(geometry, material);
        support.position.set(x, -1, 0);
        support.rotation.x = Math.PI;
        supportGroup.add(support);
        
        const baseGeometry = new THREE.BoxGeometry(1.2, 0.2, 0.8);
        const baseMaterial = new THREE.MeshPhongMaterial({ color: 0x008866 });
        const base = new THREE.Mesh(baseGeometry, baseMaterial);
        base.position.set(x, -1.6, 0);
        supportGroup.add(base);
    } else if (type === 'roller') {
        const geometry = new THREE.ConeGeometry(0.5, 1, 3);
        const material = new THREE.MeshPhongMaterial({ color: 0x00ffaa });
        const support = new THREE.Mesh(geometry, material);
        support.position.set(x, -1, 0);
        support.rotation.x = Math.PI;
        supportGroup.add(support);
        
        for (let i = 0; i < 3; i++) {
            const rollerGeometry = new THREE.SphereGeometry(0.15, 16, 16);
            const rollerMaterial = new THREE.MeshPhongMaterial({ color: 0xffffff });
            const roller = new THREE.Mesh(rollerGeometry, rollerMaterial);
            roller.position.set(x - 0.3 + i * 0.3, -1.5, 0);
            supportGroup.add(roller);
        }
    } else if (type === 'fixed') {
        const geometry = new THREE.BoxGeometry(0.8, 1.5, 1);
        const material = new THREE.MeshPhongMaterial({ color: 0x00aaff });
        const support = new THREE.Mesh(geometry, material);
        support.position.set(x, -1, 0);
        supportGroup.add(support);
    }
    
    scene.add(supportGroup);
    supports.push({ position, type, mesh: supportGroup });
    updateDisplay();
}

function updateLoadInputs() {
    const loadType = document.getElementById('loadType').value;
    const loadInputs = document.getElementById('loadInputs');
    
    if (loadType === 'concentrated') {
        loadInputs.innerHTML = `
            <div class="input-group">
                <label>Position (m)</label>
                <input type="number" id="loadPosition" min="0" max="${beamLength}" step="0.1">
            </div>
            <div class="input-group">
                <label>Magnitude (kN)</label>
                <input type="number" id="loadMagnitude" step="0.1">
            </div>
        `;
    } else if (loadType === 'distributed') {
        loadInputs.innerHTML = `
            <div class="input-group">
                <label>Start Position (m)</label>
                <input type="number" id="loadStartPos" min="0" max="${beamLength}" step="0.1">
            </div>
            <div class="input-group">
                <label>End Position (m)</label>
                <input type="number" id="loadEndPos" min="0" max="${beamLength}" step="0.1">
            </div>
            <div class="input-group">
                <label>Intensity (kN/m)</label>
                <input type="number" id="loadIntensity" step="0.1">
            </div>
        `;
    } else if (loadType === 'varying') {
        loadInputs.innerHTML = `
            <div class="input-group">
                <label>Start Position (m)</label>
                <input type="number" id="loadStartPos" min="0" max="${beamLength}" step="0.1">
            </div>
            <div class="input-group">
                <label>End Position (m)</label>
                <input type="number" id="loadEndPos" min="0" max="${beamLength}" step="0.1">
            </div>
            <div class="input-group">
                <label>Start Intensity (kN/m)</label>
                <input type="number" id="loadStartIntensity" step="0.1">
            </div>
            <div class="input-group">
                <label>End Intensity (kN/m)</label>
                <input type="number" id="loadEndIntensity" step="0.1">
            </div>
        `;
    }
}

function addLoad() {
    const loadType = document.getElementById('loadType').value;
    
    if (loadType === 'concentrated') {
        const position = parseFloat(document.getElementById('loadPosition').value);
        const magnitude = parseFloat(document.getElementById('loadMagnitude').value);
        
        if (isNaN(position) || isNaN(magnitude)) {
            alert('Invalid load parameters!');
            return;
        }
        
        addConcentratedLoad(position, magnitude);
    } else if (loadType === 'distributed') {
        const startPos = parseFloat(document.getElementById('loadStartPos').value);
        const endPos = parseFloat(document.getElementById('loadEndPos').value);
        const intensity = parseFloat(document.getElementById('loadIntensity').value);
        
        if (isNaN(startPos) || isNaN(endPos) || isNaN(intensity) || startPos >= endPos) {
            alert('Invalid load parameters!');
            return;
        }
        
        addDistributedLoad(startPos, endPos, intensity, intensity);
    } else if (loadType === 'varying') {
        const startPos = parseFloat(document.getElementById('loadStartPos').value);
        const endPos = parseFloat(document.getElementById('loadEndPos').value);
        const startIntensity = parseFloat(document.getElementById('loadStartIntensity').value);
        const endIntensity = parseFloat(document.getElementById('loadEndIntensity').value);
        
        if (isNaN(startPos) || isNaN(endPos) || isNaN(startIntensity) || isNaN(endIntensity) || startPos >= endPos) {
            alert('Invalid load parameters!');
            return;
        }
        
        addDistributedLoad(startPos, endPos, startIntensity, endIntensity);
    }
    
    updateDisplay();
}

function addConcentratedLoad(position, magnitude) {
    const x = position - beamLength/2;
    const arrowGroup = new THREE.Group();
    
    const arrowLength = Math.abs(magnitude) * 0.3;
    const arrowGeometry = new THREE.ConeGeometry(0.2, 0.5, 8);
    const arrowMaterial = new THREE.MeshPhongMaterial({ 
        color: magnitude > 0 ? 0x00ff00 : 0xff4444 
    });
    const arrowHead = new THREE.Mesh(arrowGeometry, arrowMaterial);
    
    const shaftGeometry = new THREE.CylinderGeometry(0.1, 0.1, arrowLength, 8);
    const shaft = new THREE.Mesh(shaftGeometry, arrowMaterial);
    
    if (magnitude > 0) {
        arrowHead.position.set(x, 1 + arrowLength, 0);
        arrowHead.rotation.x = Math.PI;
        shaft.position.set(x, 1.5 + arrowLength/2, 0);
    } else {
        arrowHead.position.set(x, -1 - arrowLength, 0);
        shaft.position.set(x, -1.5 - arrowLength/2, 0);
    }
    
    arrowGroup.add(arrowHead);
    arrowGroup.add(shaft);
    
    scene.add(arrowGroup);
    loads.push({
        type: 'concentrated',
        position,
        magnitude,
        mesh: arrowGroup
    });
}

function addDistributedLoad(startPos, endPos, startIntensity, endIntensity) {
    const startX = startPos - beamLength/2;
    const endX = endPos - beamLength/2;
    const length = endPos - startPos;
    
    const loadGroup = new THREE.Group();
    const numArrows = Math.max(5, Math.floor(length * 2));
    
    for (let i = 0; i <= numArrows; i++) {
        const ratio = i / numArrows;
        const x = startX + ratio * (endX - startX);
        const intensity = startIntensity + ratio * (endIntensity - startIntensity);
        
        const arrowLength = Math.abs(intensity) * 0.2;
        const arrowGeometry = new THREE.ConeGeometry(0.1, 0.3, 6);
        const arrowMaterial = new THREE.MeshPhongMaterial({ 
            color: intensity > 0 ? 0x00ff00 : 0xff4444 
        });
        const arrowHead = new THREE.Mesh(arrowGeometry, arrowMaterial);
        
        const shaftGeometry = new THREE.CylinderGeometry(0.05, 0.05, arrowLength, 6);
        const shaft = new THREE.Mesh(shaftGeometry, arrowMaterial);
        
        if (intensity > 0) {
            arrowHead.position.set(x, 1 + arrowLength, 0);
            arrowHead.rotation.x = Math.PI;
            shaft.position.set(x, 1.2 + arrowLength/2, 0);
        } else {
            arrowHead.position.set(x, -1 - arrowLength, 0);
            shaft.position.set(x, -1.2 - arrowLength/2, 0);
        }
        
        loadGroup.add(arrowHead);
        loadGroup.add(shaft);
    }
    
    scene.add(loadGroup);
    loads.push({
        type: 'distributed',
        startPos,
        endPos,
        startIntensity,
        endIntensity,
        mesh: loadGroup
    });
}

function analyzeBeam() {
    if (supports.length < 2) {
        alert('Please add at least 2 supports!');
        return;
    }
    
    if (loads.length === 0) {
        alert('Please add at least one load!');
        return;
    }
    
    performAnalysis().then(response => {
        if (response && response.results) {
            analysisResults = response.results; 
            displayResults();
            updateCharts();
        }
    });
}

async function performAnalysis() {
    const materialKey = document.getElementById('beamMaterial').value;
    const materialProps = materials[materialKey];

    const payload = {
        beamLength: beamLength,
        elastic_modulus: materialProps.E,
        supports: supports.map(s => ({ position: s.position, type: s.type })),
        loads: loads.map(l => {
            if (l.type === 'concentrated') {
                return {
                    type: 'concentrated',
                    position: l.position,
                    magnitude: l.magnitude
                };
            } else {
                return {
                    type: l.type,
                    startPos: l.startPos,
                    endPos: l.endPos,
                    startIntensity: l.startIntensity,
                    endIntensity: l.endIntensity
                };
            }
        })
    };

    try {
        const response = await fetch('http://127.0.0.1:5000/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const results = await response.json();
        return results;

    } catch (error) {
        console.error('Error during analysis:', error);
        alert('Failed to analyze beam. Make sure the Python backend server is running.');
        return null;
    }
}

function displayResults() {
    const results = document.getElementById('results');
    const content = document.getElementById('resultContent');
    
    results.style.display = 'block';
    content.innerHTML = `
        <div class="result-item">
            <span>Max Shear Force:</span>
            <span>${analysisResults.maxShear.toFixed(2)} kN</span>
        </div>
        <div class="result-item">
            <span>Max Bending Moment:</span>
            <span>${analysisResults.maxMoment.toFixed(2)} kN·m</span>
        </div>
        <div class="result-item">
            <span>Max Deflection:</span>
            <span>${(analysisResults.maxDeflection * 1000).toFixed(2)} mm</span>
        </div>
    `;
}

function updateDisplay() {
    const supportsList = document.getElementById('supports-list');
    const loadsList = document.getElementById('loads-list');
    
    supportsList.innerHTML = supports.map((s, i) => 
        `<div class="support-display">
            Support ${i+1}: ${s.type} at ${s.position}m
            <button onclick="removeSupport(${i})" style="float: right; background: #ff4444; border: none; color: white; padding: 2px 6px; border-radius: 3px;">×</button>
        </div>`
    ).join('');
    
    loadsList.innerHTML = loads.map((l, i) => 
        `<div class="load-display">
            Load ${i+1}: ${l.type} 
            ${l.type === 'concentrated' ? `${l.magnitude}kN at ${l.position}m` : 
              `${l.startIntensity}-${l.endIntensity}kN/m from ${l.startPos}m to ${l.endPos}m`}
            <button onclick="removeLoad(${i})" style="float: right; background: #ff4444; border: none; color: white; padding: 2px 6px; border-radius: 3px;">×</button>
        </div>`
    ).join('');
}

function removeSupport(index) {
    scene.remove(supports[index].mesh);
    supports.splice(index, 1);
    updateDisplay();
}

function removeLoad(index) {
    scene.remove(loads[index].mesh);
    loads.splice(index, 1);
    updateDisplay();
}

function clearAll() {
    supports.forEach(s => scene.remove(s.mesh));
    loads.forEach(l => scene.remove(l.mesh));
    supports = [];
    loads = [];
    analysisResults = null;
    document.getElementById('results').style.display = 'none';
    updateDisplay();
}

function resetView() {
    camera.position.set(15, 10, 15);
    camera.lookAt(0, 0, 0);
}

function toggleAnimation() {
    isAnimating = !isAnimating;
}

function exportImage() {
    const link = document.createElement('a');
    link.download = 'beam_analysis.png';
    link.href = renderer.domElement.toDataURL();
    link.click();
}

function toggleCharts() {
    const container = document.getElementById('chartContainer');
    container.style.display = container.style.display === 'none' ? 'block' : 'none';
    if (container.style.display === 'block' && analysisResults) {
        updateCharts();
    }
}

function switchChart(type) {
    currentChart = type;
    document.querySelectorAll('.chart-tab').forEach(tab => tab.classList.remove('active'));
    event.target.classList.add('active');
    updateCharts();
}

function updateCharts() {
    if (!analysisResults) return;
    
    const ctx = document.getElementById('chartCanvas').getContext('2d');
    
    if (chartInstance) {
        chartInstance.destroy();
    }
    
    let data, label, color;
    
    switch (currentChart) {
        case 'shear':
            data = analysisResults.shear;
            label = 'Shear Force (kN)';
            color = '#00ffaa';
            break;
        case 'moment':
            data = analysisResults.moment;
            label = 'Bending Moment (kN·m)';
            color = '#ff6600';
            break;
        case 'deflection':
            data = analysisResults.deflection.map(d => d * 1000);
            label = 'Deflection (mm)';
            color = '#6600ff';
            break;
    }
    
    chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: analysisResults.x.map(x => x.toFixed(1)),
            datasets: [{
                label: label,
                data: data,
                borderColor: color,
                backgroundColor: color + '20',
                borderWidth: 2,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: '#00ffaa'
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Position (m)',
                        color: '#00ffaa'
                    },
                    ticks: {
                        color: '#00ffaa'
                    },
                    grid: {
                        color: '#004455'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: label,
                        color: '#00ffaa'
                    },
                    ticks: {
                        color: '#00ffaa'
                    },
                    grid: {
                        color: '#004455'
                    }
                }
            }
        }
    });
}

function animateDeformation(time) {
    if (!beam || !analysisResults) return;
    
    const scale = Math.sin(time) * 0.1;
    beam.scale.y = 1 + scale;
}

function closeInfo() {
    document.getElementById('infoPanel').style.display = 'none';
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    initThreeJS();
    createBeam();
    updateLoadInputs();
});
