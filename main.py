import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/species", methods=["GET"])
def get_species():
    lat = request.args.get("lat", type=float)
    lng = request.args.get("lng", type=float)

    if lat is None or lng is None:
        return jsonify({"error": "Missing lat/lng"}), 400

    ala_url = "https://biocache.ala.org.au/ws/occurrences/search"
    params = {
        "lat": lat,
        "lon": lng,
        "radius": 5,  # radius in km
        "pageSize": 10,  # how many results to fetch
        "fq": "country:Australia",  # filter query
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
                "danger": "Unknown – sourced from ALA.",  # You can enhance this later
                "lat": record.get("decimalLatitude"),
                "lng": record.get("decimalLongitude")
            })

        return jsonify(species_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == "__main__":
    app.run(debug=True)