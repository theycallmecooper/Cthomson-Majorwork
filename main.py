import requests
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/species", methods=["GET"])
def get_species_json():
    lat = request.args.get("lat", type=float)
    lng = request.args.get("lng", type=float)

    if lat is None or lng is None:
        return jsonify({"error": "Missing lat/lng"}), 400

    # ALA API URL and parameters
    ala_url = "https://biocache-ws.ala.org.au/ws/occurrences/search"
    params = {
        "lat": lat,
        "lon": lng,
        "radius": 20,  # Radius in km
        "fq": "kingdom:Animalia",  # Only animals
        "pageSize": 50,  # Fetch more results
    }

    try:
        response = requests.get(ala_url, params=params)
        response.raise_for_status()
        data = response.json()

        species_data = []
        for record in data.get("results", []):
            species_data.append({
                "name": record.get("commonName", "Unknown"),
                "scientificName": record.get("scientificName", "Unknown"),
                "lat": record.get("decimalLatitude"),
                "lng": record.get("decimalLongitude"),
                "danger": "Not flagged as dangerous"  # Placeholder for future use
            })

        return jsonify(species_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)