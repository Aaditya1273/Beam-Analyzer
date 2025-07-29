from flask import Flask, request, jsonify
from flask_cors import CORS
from main_gui import AdvancedBeamEngine, BeamProperties, Support, ConcentratedLoad, UniformlyVaryingLoad
import numpy as np

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from the web frontend

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()

    # Extract beam properties from the request
    beam_props = BeamProperties(
        length=data['beamLength'],
        elastic_modulus=data.get('elastic_modulus', 200e9), # Default to steel
        moment_of_inertia=data.get('moment_of_inertia', 8.33e-6)
    )
    engine = AdvancedBeamEngine(beam_props)

    # Add supports
    for s in data['supports']:
        engine.add_support(Support(position=s['position'], type=s['type']))

    # Add loads
    for l in data['loads']:
        if l['type'] == 'concentrated':
            engine.add_concentrated_load(ConcentratedLoad(
                position=l['position'],
                magnitude=l['magnitude']
            ))
        elif l['type'] == 'distributed' or l['type'] == 'varying':
            engine.add_varying_load(UniformlyVaryingLoad(
                start_pos=l['startPos'],
                end_pos=l['endPos'],
                start_magnitude=l['startIntensity'],
                end_magnitude=l['endIntensity']
            ))

    # Perform analysis
    results = engine.analyze()

    # Convert numpy arrays to lists for JSON serialization
    for key, value in results.items():
        if isinstance(value, np.ndarray):
            results[key] = value.tolist()

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
