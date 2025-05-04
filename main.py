import requests
import time
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

def search_ala_species(latitude, longitude, radius=5000, max_results=20, kingdom=None):
    """
    Search for species near a location using the Atlas of Living Australia API
    
    Args:
        latitude (float): Latitude of the search location
        longitude (float): Longitude of the search location
        radius (int): Search radius in meters
        max_results (int): Maximum number of results to return
        kingdom (str, optional): Filter by kingdom (e.g., "Animalia")
        
    Returns:
        dict: Dictionary containing species data and total records count
    """
    # Convert radius to kilometers
    radius_km = radius / 1000
    
    # Define the API endpoint
    url = "https://biocache.ala.org.au/ws/occurrences/search"
    
    # Define the query parameters
    params = {
        "q": "*:*",                  # Match all records
        "lat": latitude,             # Latitude coordinate
        "lon": longitude,            # Longitude coordinate
        "radius": radius_km,         # Search radius in kilometers
        "pageSize": max_results,     # Number of results per page
        "sort": "taxon_name"         # Sort by scientific name
    }
    
    # Add kingdom filter if specified
    if kingdom:
        params["fq"] = f"kingdom:{kingdom}"
    
    try:
        # Make the API request
        response = requests.get(url, params=params)
        
        # Check if request was successful
        if not response.ok:
            print(f"Error {response.status_code}: {response.text[:200]}...")
            return {"species": [], "total_records": 0}
            
        # Parse the JSON response
        data = response.json()
        
        # Get total count
        total_records = data.get("totalRecords", 0)
        
        # Extract species information from the response
        species_list = []
        for record in data.get("occurrences", []):
            species_info = {
                "scientific_name": record.get("scientificName", "Unknown species"),
                "common_name": record.get("vernacularName", "No common name"),
                "lat": record.get("decimalLatitude"),
                "lng": record.get("decimalLongitude"),
                "danger": "Not flagged as dangerous"  # Placeholder for future use
            }
            
            # Add to our species list if not already present
            if species_info not in species_list:
                species_list.append(species_info)
                
        return {"species": species_list, "total_records": total_records}
        
    except Exception as e:
        print(f"Error searching for species: {e}")
        return {"species": [], "total_records": 0}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/species", methods=["GET"])
def get_species_json():
    lat = request.args.get("lat", type=float)
    lng = request.args.get("lng", type=float)
    radius = request.args.get("radius", default=20000, type=int)  # Default 20km in meters
    max_results = request.args.get("max", default=50, type=int)
    kingdom = request.args.get("kingdom", default="Animalia")  # Default to animals

    if lat is None or lng is None:
        return jsonify({"error": "Missing lat/lng parameters"}), 400

    try:
        result = search_ala_species(lat, lng, radius, max_results, kingdom)
        
        # Transform the data to match the expected format in your frontend
        species_data = []
        for species in result["species"]:
            species_data.append({
                "name": species["common_name"],
                "scientificName": species["scientific_name"],
                "lat": species["lat"],
                "lng": species["lng"],
                "danger": species["danger"]
            })
        
        return jsonify(species_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/view-species")
def view_species_page():
    lat = request.args.get("lat", type=float)
    lng = request.args.get("lng", type=float)
    radius = request.args.get("radius", default=20000, type=int)
    max_results = request.args.get("max", default=50, type=int)
    kingdom = request.args.get("kingdom", default="Animalia")

    if lat is None or lng is None:
        return render_template("species.html", species=[])

    try:
        result = search_ala_species(lat, lng, radius, max_results, kingdom)
        
        # Transform the data to match the expected format in your template
        species_data = []
        for species in result["species"]:
            species_data.append({
                "name": species["common_name"],
                "scientificName": species["scientific_name"],
                "lat": species["lat"],
                "lng": species["lng"],
                "danger": species["danger"]
            })
        
        return render_template("species.html", species=species_data)
    except Exception as e:
        return render_template("species.html", species=[], error=str(e))

# Testing function - can be used for debugging
def test_location(name, latitude, longitude, radius=10000):
    """Run a test search for a specific location and print the results"""
    print(f"\n--- Testing: {name} ({latitude}, {longitude}) ---")
    
    result = search_ala_species(latitude, longitude, radius)
    
    if result["total_records"] > 0:
        print(f"Found {result['total_records']} total records")
        print(f"Sample of {len(result['species'])} species:")
        for i, sp in enumerate(result['species'], 1):
            print(f"{i}. {sp['scientific_name']} - {sp['common_name']}")
    else:
        print(f"No species found at this location or an error occurred.")

if __name__ == "__main__":
    app.run(debug=True)