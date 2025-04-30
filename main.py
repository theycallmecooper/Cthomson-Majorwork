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
    """Returns species data as JSON (used by frontend JavaScript or Leaflet)."""
    lat = request.args.get("lat", type=float)
    lng = request.args.get("lng", type=float)

    if lat is None or lng is None:
        return jsonify({"error": "Missing lat/lng"}), 400

    ala_url = "https://biocache.ala.org.au/ws/occurrences/search"
    params = {
        "lat": lat,
        "lon": lng,
        "radius": 10,  # radius in km
        "pageSize": 10,
        "fq": "country:Australia",
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
                "danger": "Unknown – sourced from ALA.",
                "lat": record.get("decimalLatitude"),
                "lng": record.get("decimalLongitude")
            })

        return jsonify(species_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/species.html")
def species_page():
    """Renders the species.html template with species near the user."""
    lat = request.args.get("lat", type=float)
    lng = request.args.get("lng", type=float)

    if lat is None or lng is None:
        return "Missing coordinates", 400

    ala_url = "https://biocache.ala.org.au/ws/occurrences/search"
    params = {
        "lat": lat,
        "lon": lng,
        "radius": 10,  # radius in km
        "pageSize": 10,
        "fq": "country:Australia",
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
                "danger": "Unknown – sourced from ALA.",
            })

        return render_template("species.html", species=species_data)
    except Exception as e:
        return f"Error fetching data: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=True)
