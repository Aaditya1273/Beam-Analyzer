import React, { useState, useEffect, useRef, useMemo } from 'react';
import * as THREE from 'three';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, AreaChart } from 'recharts';
import { Plus, Trash2, Settings, Eye, EyeOff, RotateCcw, Download, Calculator } from 'lucide-react';

const BeamAnalyzer = () => {
  const mountRef = useRef(null);
  const sceneRef = useRef(null);
  const rendererRef = useRef(null);
  const cameraRef = useRef(null);
  const beamRef = useRef(null);
  const animationRef = useRef(null);

  // Beam properties
  const [beamLength, setBeamLength] = useState(10);
  const [supports, setSupports] = useState([
    { id: 1, position: 2, type: 'pin' },
    { id: 2, position: 8, type: 'roller' }
  ]);
  const [loads, setLoads] = useState([
    { id: 1, type: 'concentrated', position: 5, magnitude: 50 }
  ]);
  const [varyingLoads, setVaryingLoads] = useState([]);

  // Visualization controls
  const [showShear, setShowShear] = useState(true);
  const [showMoment, setShowMoment] = useState(true);
  const [show3D, setShow3D] = useState(true);
  const [animateDeflection, setAnimateDeflection] = useState(false);
  const [viewMode, setViewMode] = useState('3d'); // '3d', 'side', 'graphs'

  // Analysis results
  const [reactions, setReactions] = useState({});
  const [analysisData, setAnalysisData] = useState([]);
  const [maxDeflection, setMaxDeflection] = useState(0);

  // Initialize 3D scene
  useEffect(() => {
    if (!mountRef.current || !show3D) return;

    // Scene setup
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0a0f);
    
    // Camera
    const camera = new THREE.PerspectiveCamera(75, 800 / 600, 0.1, 1000);
    camera.position.set(15, 10, 15);
    
    // Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(800, 600);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.2;
    
    mountRef.current.appendChild(renderer.domElement);

    // Lighting
    const ambientLight = new THREE.AmbientLight(0x404040, 0.3);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
    directionalLight.position.set(20, 20, 20);
    directionalLight.castShadow = true;
    directionalLight.shadow.mapSize.width = 2048;
    directionalLight.shadow.mapSize.height = 2048;
    scene.add(directionalLight);

    // Add gradient environment
    const sphereGeometry = new THREE.SphereGeometry(100, 32, 32);
    const sphereMaterial = new THREE.MeshBasicMaterial({
      color: 0x1a1a2e,
      side: THREE.BackSide,
      transparent: true,
      opacity: 0.8
    });
    const sphere = new THREE.Mesh(sphereGeometry, sphereMaterial);
    scene.add(sphere);

    sceneRef.current = scene;
    rendererRef.current = renderer;
    cameraRef.current = camera;

    // Simple orbit controls simulation
    let mouseDown = false;
    let mouseX = 0;
    let mouseY = 0;
    
    const handleMouseDown = (event) => {
      mouseDown = true;
      mouseX = event.clientX;
      mouseY = event.clientY;
    };
    
    const handleMouseUp = () => {
      mouseDown = false;
    };
    
    const handleMouseMove = (event) => {
      if (!mouseDown) return;
      
      const deltaX = event.clientX - mouseX;
      const deltaY = event.clientY - mouseY;
      
      const spherical = new THREE.Spherical();
      spherical.setFromVector3(camera.position);
      spherical.theta -= deltaX * 0.01;
      spherical.phi += deltaY * 0.01;
      spherical.phi = Math.max(0.1, Math.min(Math.PI - 0.1, spherical.phi));
      
      camera.position.setFromSpherical(spherical);
      camera.lookAt(0, 0, 0);
      
      mouseX = event.clientX;
      mouseY = event.clientY;
    };
    
    renderer.domElement.addEventListener('mousedown', handleMouseDown);
    renderer.domElement.addEventListener('mouseup', handleMouseUp);
    renderer.domElement.addEventListener('mousemove', handleMouseMove);

    return () => {
      if (mountRef.current && renderer.domElement) {
        mountRef.current.removeChild(renderer.domElement);
      }
      renderer.domElement.removeEventListener('mousedown', handleMouseDown);
      renderer.domElement.removeEventListener('mouseup', handleMouseUp);
      renderer.domElement.removeEventListener('mousemove', handleMouseMove);
      renderer.dispose();
    };
  }, [show3D]);

  // Create 3D beam visualization
  useEffect(() => {
    if (!sceneRef.current || !show3D) return;

    // Clear previous beam
    if (beamRef.current) {
      sceneRef.current.remove(beamRef.current);
    }

    const beamGroup = new THREE.Group();

    // Main beam
    const beamGeometry = new THREE.BoxGeometry(beamLength, 0.5, 1);
    const beamMaterial = new THREE.MeshPhongMaterial({
      color: 0x4a90e2,
      transparent: true,
      opacity: 0.9,
      shininess: 100
    });
    const beam = new THREE.Mesh(beamGeometry, beamMaterial);
    beam.position.set(beamLength / 2, 0, 0);
    beam.castShadow = true;
    beam.receiveShadow = true;
    beamGroup.add(beam);

    // Add supports
    supports.forEach(support => {
      const supportGroup = new THREE.Group();
      
      if (support.type === 'pin') {
        // Pin support (triangle)
        const geometry = new THREE.ConeGeometry(0.3, 1, 3);
        const material = new THREE.MeshPhongMaterial({ color: 0xff6b6b });
        const cone = new THREE.Mesh(geometry, material);
        cone.position.set(support.position, -0.75, 0);
        cone.rotation.z = Math.PI;
        supportGroup.add(cone);
      } else if (support.type === 'roller') {
        // Roller support (cylinder)
        const geometry = new THREE.CylinderGeometry(0.2, 0.2, 0.8, 8);
        const material = new THREE.MeshPhongMaterial({ color: 0x4ecdc4 });
        const cylinder = new THREE.Mesh(geometry, material);
        cylinder.position.set(support.position, -0.6, 0);
        cylinder.rotation.z = Math.PI / 2;
        supportGroup.add(cylinder);
      }
      
      beamGroup.add(supportGroup);
    });

    // Add loads
    loads.forEach((load, index) => {
      if (load.type === 'concentrated') {
        // Load arrow
        const arrowGroup = new THREE.Group();
        
        // Arrow shaft
        const shaftGeometry = new THREE.CylinderGeometry(0.05, 0.05, Math.abs(load.magnitude) / 20);
        const shaftMaterial = new THREE.MeshPhongMaterial({ color: 0xff4757 });
        const shaft = new THREE.Mesh(shaftGeometry, shaftMaterial);
        shaft.position.set(load.position, 1 + Math.abs(load.magnitude) / 40, 0);
        
        // Arrow head
        const headGeometry = new THREE.ConeGeometry(0.15, 0.3, 6);
        const head = new THREE.Mesh(headGeometry, shaftMaterial);
        head.position.set(load.position, 0.35, 0);
        
        arrowGroup.add(shaft);
        arrowGroup.add(head);
        beamGroup.add(arrowGroup);

        // Load label
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        canvas.width = 128;
        canvas.height = 64;
        context.font = '20px Arial';
        context.fillStyle = '#ffffff';
        context.textAlign = 'center';
        context.fillText(`${load.magnitude}N`, 64, 35);
        
        const texture = new THREE.CanvasTexture(canvas);
        const spriteMaterial = new THREE.SpriteMaterial({ map: texture });
        const sprite = new THREE.Sprite(spriteMaterial);
        sprite.position.set(load.position, 2, 0);
        sprite.scale.set(1, 0.5, 1);
        beamGroup.add(sprite);
      }
    });

    beamRef.current = beamGroup;
    sceneRef.current.add(beamGroup);

  }, [beamLength, supports, loads, show3D]);

  // Animation loop
  useEffect(() => {
    if (!rendererRef.current || !sceneRef.current || !cameraRef.current) return;

    const animate = () => {
      animationRef.current = requestAnimationFrame(animate);
      
      if (animateDeflection && beamRef.current) {
        const time = Date.now() * 0.001;
        beamRef.current.rotation.y = Math.sin(time) * 0.1;
      }
      
      rendererRef.current.render(sceneRef.current, cameraRef.current);
    };

    animate();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [animateDeflection, show3D]);

  // Beam analysis calculations
  const analyzeBeam = useMemo(() => {
    const numPoints = 100;
    const dx = beamLength / (numPoints - 1);
    const data = [];
    
    // Calculate reactions (simplified for 2 supports)
    if (supports.length >= 2) {
      const support1 = supports[0];
      const support2 = supports[1];
      const L = support2.position - support1.position;
      
      let totalLoad = 0;
      let momentAboutSupport1 = 0;
      
      loads.forEach(load => {
        if (load.type === 'concentrated') {
          totalLoad += load.magnitude;
          momentAboutSupport1 += load.magnitude * (load.position - support1.position);
        }
      });
      
      const R2 = momentAboutSupport1 / L;
      const R1 = totalLoad - R2;
      
      setReactions({
        [support1.position]: R1,
        [support2.position]: R2
      });
      
      // Calculate shear force and bending moment
      for (let i = 0; i < numPoints; i++) {
        const x = i * dx;
        let shear = 0;
        let moment = 0;
        
        // Add reaction at support 1
        if (x >= support1.position) {
          shear += R1;
        }
        
        // Subtract loads
        loads.forEach(load => {
          if (load.type === 'concentrated' && x >= load.position) {
            shear -= load.magnitude;
          }
        });
        
        // Add reaction at support 2
        if (x >= support2.position) {
          shear += R2;
        }
        
        // Calculate moment by integration
        if (i > 0) {
          const prevShear = data[i-1]?.shear || 0;
          moment = (data[i-1]?.moment || 0) + (prevShear + shear) * dx / 2;
        }
        
        data.push({
          x: x.toFixed(2),
          shear: shear.toFixed(2),
          moment: moment.toFixed(2),
          deflection: (Math.sin(Math.PI * x / beamLength) * Math.abs(moment) / 1000).toFixed(4)
        });
      }
    }
    
    setAnalysisData(data);
    setMaxDeflection(Math.max(...data.map(d => Math.abs(parseFloat(d.deflection)))));
    
    return data;
  }, [beamLength, supports, loads]);

  const addSupport = () => {
    const newSupport = {
      id: Date.now(),
      position: beamLength / 2,
      type: 'pin'
    };
    setSupports([...supports, newSupport]);
  };

  const addLoad = () => {
    const newLoad = {
      id: Date.now(),
      type: 'concentrated',
      position: beamLength / 2,
      magnitude: 50
    };
    setLoads([...loads, newLoad]);
  };

  const removeSupport = (id) => {
    setSupports(supports.filter(s => s.id !== id));
  };

  const removeLoad = (id) => {
    setLoads(loads.filter(l => l.id !== id));
  };

  const updateSupport = (id, field, value) => {
    setSupports(supports.map(s => 
      s.id === id ? { ...s, [field]: value } : s
    ));
  };

  const updateLoad = (id, field, value) => {
    setLoads(loads.map(l => 
      l.id === id ? { ...l, [field]: value } : l
    ));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 text-white">
      {/* Header */}
      <div className="bg-black/20 backdrop-blur-lg border-b border-white/10">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              Advanced Beam Analyzer 3D
            </h1>
            <div className="flex space-x-4">
              <button
                onClick={() => setViewMode(viewMode === '3d' ? 'graphs' : '3d')}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
              >
                {viewMode === '3d' ? 'Show Graphs' : 'Show 3D'}
              </button>
              <button
                onClick={() => setShow3D(!show3D)}
                className={`px-4 py-2 rounded-lg transition-colors ${show3D ? 'bg-green-600 hover:bg-green-700' : 'bg-gray-600 hover:bg-gray-700'}`}
              >
                {show3D ? <Eye size={16} /> : <EyeOff size={16} />}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-6 py-6">
        <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
          
          {/* Control Panel */}
          <div className="xl:col-span-1 space-y-6">
            
            {/* Beam Properties */}
            <div className="bg-black/30 backdrop-blur-lg rounded-xl p-6 border border-white/10">
              <h3 className="text-xl font-semibold mb-4 text-blue-300">Beam Properties</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Length (m)</label>
                  <input
                    type="number"
                    value={beamLength}
                    onChange={(e) => setBeamLength(parseFloat(e.target.value) || 10)}
                    className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    step="0.1"
                    min="1"
                  />
                </div>
                <div className="text-sm text-gray-300">
                  Max Deflection: {maxDeflection.toFixed(4)} m
                </div>
              </div>
            </div>

            {/* Supports */}
            <div className="bg-black/30 backdrop-blur-lg rounded-xl p-6 border border-white/10">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-semibold text-green-300">Supports</h3>
                <button
                  onClick={addSupport}
                  className="p-2 bg-green-600 hover:bg-green-700 rounded-lg transition-colors"
                >
                  <Plus size={16} />
                </button>
              </div>
              <div className="space-y-3">
                {supports.map(support => (
                  <div key={support.id} className="bg-white/5 rounded-lg p-3 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Support {support.id}</span>
                      <button
                        onClick={() => removeSupport(support.id)}
                        className="p-1 text-red-400 hover:text-red-300"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <label className="block text-xs text-gray-300 mb-1">Position</label>
                        <input
                          type="number"
                          value={support.position}
                          onChange={(e) => updateSupport(support.id, 'position', parseFloat(e.target.value) || 0)}
                          className="w-full px-2 py-1 text-xs bg-white/10 border border-white/20 rounded"
                          step="0.1"
                        />
                      </div>
                      <div>
                        <label className="block text-xs text-gray-300 mb-1">Type</label>
                        <select
                          value={support.type}
                          onChange={(e) => updateSupport(support.id, 'type', e.target.value)}
                          className="w-full px-2 py-1 text-xs bg-white/10 border border-white/20 rounded"
                        >
                          <option value="pin">Pin</option>
                          <option value="roller">Roller</option>
                          <option value="fixed">Fixed</option>
                        </select>
                      </div>
                    </div>
                    {reactions[support.position] && (
                      <div className="text-xs text-yellow-300">
                        Reaction: {reactions[support.position].toFixed(2)} N
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Loads */}
            <div className="bg-black/30 backdrop-blur-lg rounded-xl p-6 border border-white/10">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-semibold text-red-300">Loads</h3>
                <button
                  onClick={addLoad}
                  className="p-2 bg-red-600 hover:bg-red-700 rounded-lg transition-colors"
                >
                  <Plus size={16} />
                </button>
              </div>
              <div className="space-y-3">
                {loads.map(load => (
                  <div key={load.id} className="bg-white/5 rounded-lg p-3 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Load {load.id}</span>
                      <button
                        onClick={() => removeLoad(load.id)}
                        className="p-1 text-red-400 hover:text-red-300"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <label className="block text-xs text-gray-300 mb-1">Position</label>
                        <input
                          type="number"
                          value={load.position}
                          onChange={(e) => updateLoad(load.id, 'position', parseFloat(e.target.value) || 0)}
                          className="w-full px-2 py-1 text-xs bg-white/10 border border-white/20 rounded"
                          step="0.1"
                        />
                      </div>
                      <div>
                        <label className="block text-xs text-gray-300 mb-1">Magnitude (N)</label>
                        <input
                          type="number"
                          value={load.magnitude}
                          onChange={(e) => updateLoad(load.id, 'magnitude', parseFloat(e.target.value) || 0)}
                          className="w-full px-2 py-1 text-xs bg-white/10 border border-white/20 rounded"
                          step="1"
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Visualization Controls */}
            <div className="bg-black/30 backdrop-blur-lg rounded-xl p-6 border border-white/10">
              <h3 className="text-xl font-semibold mb-4 text-purple-300">Controls</h3>
              <div className="space-y-3">
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={showShear}
                    onChange={(e) => setShowShear(e.target.checked)}
                    className="rounded"
                  />
                  <span className="text-sm">Show Shear Force</span>
                </label>
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={showMoment}
                    onChange={(e) => setShowMoment(e.target.checked)}
                    className="rounded"
                  />
                  <span className="text-sm">Show Bending Moment</span>
                </label>
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={animateDeflection}
                    onChange={(e) => setAnimateDeflection(e.target.checked)}
                    className="rounded"
                  />
                  <span className="text-sm">Animate Deflection</span>
                </label>
              </div>
            </div>
          </div>

          {/* Main Visualization Area */}
          <div className="xl:col-span-3 space-y-6">
            
            {/* 3D Visualization */}
            {show3D && (
              <div className="bg-black/30 backdrop-blur-lg rounded-xl p-6 border border-white/10">
                <h3 className="text-xl font-semibold mb-4 text-cyan-300">3D Beam Visualization</h3>
                <div 
                  ref={mountRef} 
                  className="w-full h-96 rounded-lg overflow-hidden border border-white/20"
                  style={{ background: 'linear-gradient(45deg, #0a0a0f, #1a1a2e)' }}
                />
                <div className="mt-4 text-sm text-gray-300">
                  <p>• Drag to rotate view</p>
                  <p>• Blue beam with red loads and colored supports</p>
                  <p>• Pin supports (red triangles), Roller supports (cyan cylinders)</p>
                </div>
              </div>
            )}

            {/* Analysis Graphs */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              
              {/* Shear Force Diagram */}
              {showShear && (
                <div className="bg-black/30 backdrop-blur-lg rounded-xl p-6 border border-white/10">
                  <h3 className="text-xl font-semibold mb-4 text-orange-300">Shear Force Diagram</h3>
                  <ResponsiveContainer width="100%" height={250}>
                    <AreaChart data={analysisData}>
                      <defs>
                        <linearGradient id="shearGradient" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#ff6b6b" stopOpacity={0.8}/>
                          <stop offset="95%" stopColor="#ff6b6b" stopOpacity={0.1}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                      <XAxis dataKey="x" stroke="#9ca3af" />
                      <YAxis stroke="#9ca3af" />
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: 'rgba(0,0,0,0.8)', 
                          border: '1px solid #374151',
                          borderRadius: '8px'
                        }} 
                      />
                      <Area 
                        type="monotone" 
                        dataKey="shear" 
                        stroke="#ff6b6b" 
                        fillOpacity={1} 
                        fill="url(#shearGradient)" 
                        strokeWidth={2}
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              )}

              {/* Bending Moment Diagram */}
              {showMoment && (
                <div className="bg-black/30 backdrop-blur-lg rounded-xl p-6 border border-white/10">
                  <h3 className="text-xl font-semibold mb-4 text-green-300">Bending Moment Diagram</h3>
                  <ResponsiveContainer width="100%" height={250}>
                    <AreaChart data={analysisData}>
                      <defs>
                        <linearGradient id="momentGradient" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#4ecdc4" stopOpacity={0.8}/>
                          <stop offset="95%" stopColor="#4ecdc4" stopOpacity={0.1}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                      <XAxis dataKey="x" stroke="#9ca3af" />
                      <YAxis stroke="#9ca3af" />
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: 'rgba(0,0,0,0.8)', 
                          border: '1px solid #374151',
                          borderRadius: '8px'
                        }} 
                      />
                      <Area 
                        type="monotone" 
                        dataKey="moment" 
                        stroke="#4ecdc4" 
                        fillOpacity={1} 
                        fill="url(#momentGradient)" 
                        strokeWidth={2}
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              )}
            </div>

            {/* Deflection Curve */}
            <div className="bg-black/30 backdrop-blur-lg rounded-xl p-6 border border-white/10">
              <h3 className="text-xl font-semibold mb-4 text-purple-300">Deflection Curve</h3>
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={analysisData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="x" stroke="#9ca3af" />
                  <YAxis stroke="#9ca3af" />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'rgba(0,0,0,0.8)', 
                      border: '1px solid #374151',
                      borderRadius: '8px'
                    }} 
                  />
                  <Line 
                    type="monotone" 
                    dataKey="deflection" 
                    stroke="#a855f7" 
                    strokeWidth={3}
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
};

export default BeamAnalyzer;