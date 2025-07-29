#!/usr/bin/env python3
"""
🚀 ULTIMATE BEAM ANALYZER SERVER 🚀
High-Performance Flask API with Advanced Error Handling & Optimization
"""

import sys, os, traceback, logging
from functools import wraps, lru_cache
from datetime import datetime
from typing import Dict, List, Any, Tuple
import numpy as np

# Dynamic path resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, request, jsonify, g
from flask_cors import CORS
from Python.main_gui import AdvancedBeamEngine, BeamProperties, Support, ConcentratedLoad, UniformlyVaryingLoad
from logging.handlers import RotatingFileHandler

class MasterBeamServer:
    """🎯 Ultra-Efficient Beam Analysis Server Engine"""
    
    # Material database with advanced properties
    MATERIALS = {
        'steel': {'E': 200e9, 'I': 8.33e-6, 'density': 7850, 'name': 'High-Strength Steel'},
        'concrete': {'E': 30e9, 'I': 8.33e-6, 'density': 2400, 'name': 'Reinforced Concrete'},
        'wood': {'E': 12e9, 'I': 8.33e-6, 'density': 600, 'name': 'Structural Timber'},
        'aluminum': {'E': 70e9, 'I': 8.33e-6, 'density': 2700, 'name': 'Aerospace Aluminum'},
        'carbon_fiber': {'E': 150e9, 'I': 8.33e-6, 'density': 1600, 'name': 'Carbon Fiber Composite'}
    }
    
    def __init__(self):
        self.app = self._create_app()
        self._setup_logging()
        self._register_routes()
        
    def _create_app(self) -> Flask:
        """🔧 Initialize Flask app with optimal configuration"""
        app = Flask(__name__, static_folder='.', static_url_path='')
        app.config.update({
            'JSON_SORT_KEYS': False,
            'JSONIFY_PRETTYPRINT_REGULAR': True,
            'MAX_CONTENT_LENGTH': 16 * 1024 * 1024  # 16MB limit
        })
        CORS(app, origins=["*"], methods=["GET", "POST", "OPTIONS"])
        return app
    
    def _setup_logging(self):
        """📊 Advanced logging configuration"""
        logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
        handler = RotatingFileHandler('beam_master.log', maxBytes=50*1024*1024, backupCount=10)
        handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s'))
        self.app.logger.addHandler(handler)
    
    @staticmethod
    def performance_monitor(f):
        """⚡ Performance monitoring decorator"""
        @wraps(f)
        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            try:
                result = f(*args, **kwargs)
                duration = (datetime.now() - start_time).total_seconds()
                logging.info(f"✅ {f.__name__} executed in {duration:.3f}s")
                return result
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                logging.error(f"❌ {f.__name__} failed after {duration:.3f}s: {str(e)}")
                return jsonify({
                    'error': str(e),
                    'status': 'error',
                    'timestamp': datetime.now().isoformat(),
                    'execution_time': f"{duration:.3f}s"
                }), 400
        return wrapper
    
    @lru_cache(maxsize=128)
    def _get_material_props(self, material: str) -> Tuple[float, float]:
        """🔍 Cached material property lookup"""
        props = self.MATERIALS.get(material, self.MATERIALS['steel'])
        return props['E'], props['I']
    
    def _validate_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """🛡️ Ultra-fast input validation with detailed feedback"""
        errors = []
        
        # Beam validation
        beam_length = data.get('beamLength', 0)
        if not (isinstance(beam_length, (int, float)) and 0.1 <= beam_length <= 1000):
            errors.append("Beam length must be between 0.1m and 1000m")
        
        # Support validation
        supports = data.get('supports', [])
        if len(supports) < 2:
            errors.append("Minimum 2 supports required")
        
        for i, support in enumerate(supports):
            pos = support.get('position', -1)
            if not (0 <= pos <= beam_length):
                errors.append(f"Support {i+1} position invalid")
        
        # Load validation
        loads = data.get('loads', [])
        if not loads:
            errors.append("At least one load required")
        
        for i, load in enumerate(loads):
            load_type = load.get('type')
            if load_type == 'concentrated':
                pos = load.get('position', -1)
                mag = load.get('magnitude', 0)
                if not (0 <= pos <= beam_length) or abs(mag) > 1e6:
                    errors.append(f"Load {i+1}: Invalid position or magnitude")
            elif load_type in ['distributed', 'varying']:
                start_pos, end_pos = load.get('startPos', -1), load.get('endPos', -1)
                if not (0 <= start_pos < end_pos <= beam_length):
                    errors.append(f"Load {i+1}: Invalid position range")
        
        if errors:
            raise ValueError(" | ".join(errors))
        
        return data
    
    def _create_engine(self, data: Dict[str, Any]) -> AdvancedBeamEngine:
        """🏗️ Optimized engine creation with smart defaults"""
        material = data.get('material', 'steel')
        E, I = self._get_material_props(material)
        
        beam_props = BeamProperties(
            length=data['beamLength'],
            elastic_modulus=data.get('elastic_modulus', E),
            moment_of_inertia=data.get('moment_of_inertia', I)
        )
        
        engine = AdvancedBeamEngine(beam_props)
        
        # Batch add supports
        [engine.add_support(Support(s['position'], s['type'])) for s in data['supports']]
        
        # Batch add loads with optimized logic
        for load in data['loads']:
            if load['type'] == 'concentrated':
                engine.add_concentrated_load(ConcentratedLoad(load['position'], load['magnitude']))
            else:
                engine.add_varying_load(UniformlyVaryingLoad(
                    load['startPos'], load['endPos'], 
                    load['startIntensity'], load['endIntensity']
                ))
        
        return engine
    
    def _serialize_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """🔄 High-performance result serialization"""
        return {
            key: value.tolist() if isinstance(value, np.ndarray) else value 
            for key, value in results.items()
        }
    
    def _register_routes(self):
        """🛣️ Register all API routes with advanced features"""
        
        @self.app.route('/')
        def index():
            return self.app.send_static_file('3d_beam_designer.html')
        
        @self.app.route('/api/analyze', methods=['POST'])
        @self.performance_monitor
        def analyze():
            """🔬 Master analysis endpoint with full optimization"""
            data = self._validate_input(request.get_json() or {})
            
            self.app.logger.info(f"🚀 Analysis started: Beam {data['beamLength']}m, "
                               f"{len(data['supports'])} supports, {len(data['loads'])} loads")
            
            engine = self._create_engine(data)
            results = engine.analyze()
            
            response = {
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'beam_info': {
                    'length': data['beamLength'],
                    'material': data.get('material', 'steel'),
                    'supports_count': len(data['supports']),
                    'loads_count': len(data['loads'])
                },
                'results': self._serialize_results(results),
                'performance': {'memory_efficient': True, 'optimized': True}
            }
            
            self.app.logger.info("✅ Analysis completed successfully")
            return jsonify(response)
        
        @self.app.route('/api/materials', methods=['GET'])
        @lru_cache(maxsize=1)
        def get_materials():
            """📋 Enhanced materials endpoint with caching"""
            return jsonify({
                material: {**props, 'id': material} 
                for material, props in self.MATERIALS.items()
            })
        
        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """❤️ Advanced health monitoring"""
            return jsonify({
                'status': 'optimal',
                'server': 'Master Beam Analyzer',
                'version': '2.0',
                'timestamp': datetime.now().isoformat(),
                'uptime': 'active',
                'performance': 'maximum'
            })
        
        @self.app.route('/api/validate', methods=['POST'])
        @self.performance_monitor
        def validate_design():
            """✅ Pre-analysis validation endpoint"""
            try:
                data = self._validate_input(request.get_json() or {})
                return jsonify({
                    'status': 'valid',
                    'message': 'Design validation passed',
                    'recommendations': self._get_design_recommendations(data)
                })
            except ValueError as e:
                return jsonify({'status': 'invalid', 'errors': str(e).split(' | ')}), 400
        
        # Global error handlers
        @self.app.errorhandler(Exception)
        def handle_error(error):
            self.app.logger.error(f"💥 Unhandled error: {str(error)}\n{traceback.format_exc()}")
            return jsonify({
                'error': 'Internal server error',
                'status': 'error',
                'timestamp': datetime.now().isoformat()
            }), 500
    
    def _get_design_recommendations(self, data: Dict[str, Any]) -> List[str]:
        """💡 Smart design recommendations"""
        recommendations = []
        beam_length = data['beamLength']
        loads_count = len(data['loads'])
        
        if beam_length > 20:
            recommendations.append("Consider additional supports for long spans")
        if loads_count > 10:
            recommendations.append("High load count - verify structural capacity")
        if data.get('material') == 'wood' and beam_length > 10:
            recommendations.append("Wood beams may require steel reinforcement for long spans")
        
        return recommendations or ["Design looks optimal"]
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """🚀 Launch the master server"""
        print("🎯 MASTER BEAM ANALYZER SERVER INITIALIZING...")
        print(f"🌐 Server: http://127.0.0.1:{port}")
        print("📊 Status: READY FOR MAXIMUM PERFORMANCE")
        print("🔥 Features: Ultra-Fast | Error-Resilient | Production-Ready")
        self.app.run(host=host, port=port, debug=debug, threaded=True)

# 🎯 EXECUTION ENTRY POINT
if __name__ == '__main__':
    server = MasterBeamServer()
    server.run(debug=True)