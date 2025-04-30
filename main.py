import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/species", methods=["GET"])
def get_species():
    lat = request.args.get("lat", type=float)
    lng = request.args.get("lng", type=float)

    # ALA API URL for occurrence search
    url = f"https://api.ala.org.au/occurrences/search?lat={lat}&lon={lng}&radius=50&limit=10&fq=taxonConceptId:4481752"  # Example filter for dangerous species
    response = requests.get(url)
    data = response.json()

    # Extract relevant information from ALA API response
    species_data = []
    for occurrence in data['response']['docs']:
        species_data.append({
            "name": occurrence['scientificName'],
            "common_name": occurrence.get('commonName', 'Unknown'),
            "danger": "⚠️ Danger info needs to be added",  # You can add danger tags based on the species
            "lat": occurrence['decimalLatitude'],
            "lng": occurrence['decimalLongitude'],
            "image": occurrence.get('imageURL', None)
        })

    return jsonify(species_data)

if __name__ == "__main__":
    app.run(debug=True)