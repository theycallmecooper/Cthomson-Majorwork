import requests
import time
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from openai import OpenAI

# Initialize OpenAI client
openai_client = OpenAI(api_key="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")

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

def analyze_species_danger(species_list):
    """
    Use OpenAI's API to analyze danger levels, categorize species and provide missing common names
    
    Args:
        species_list (list): List of species dictionaries
    
    Returns:
        list: Updated list with danger assessments and categorization
    """
    try:
        # Only send necessary data to OpenAI to reduce token usage
        simplified_species = []
        for species in species_list:
            simplified_species.append({
                "scientific_name": species["scientific_name"],
                "common_name": species["common_name"]
            })
        
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant specialized in Australian wildlife taxonomy and risk assessment."},
                {"role": "user", "content": f"""I will provide you with a list of species. For each species, please provide the following information in a structured format:
                1. Scientific name (as provided)
                2. Common name (if "No common name" is listed, please suggest an appropriate common name)
                3. Danger type: categorize as "VENOMOUS/POISONOUS", "AGGRESSIVE", or "HARMLESS"
                4. Danger rating: On a scale of 1-10, where 10 is extremely dangerous
                5. Brief explanation of any hazards (max 15 words)
                
                Only respond with entries that have a danger rating of 3 or higher.
                Format your response as:
                Scientific name | Common name | DANGER_TYPE | Rating: X/10 | Brief explanation
                
                Here's the list: {simplified_species}"""}
            ],
            max_tokens=800,
            temperature=0.5
        )
        
        # Extract danger information from OpenAI's response
        danger_info = response.choices[0].message.content.strip()
        
        # We'll update our species list with danger ratings and categories
        for species in species_list:
            # Check if this species is in the danger info
            if species["scientific_name"] in danger_info:
                # Find the line containing this species
                for line in danger_info.split('\n'):
                    if species["scientific_name"] in line:
                        parts = line.split('|')
                        if len(parts) >= 5:
                            # Check if we need to update the common name
                            if species["common_name"] == "No common name" and len(parts) > 1:
                                species["common_name"] = parts[1].strip()
                            
                            # Determine danger category
                            danger_type = parts[2].strip().upper() if len(parts) > 2 else ""
                            if "VENOMOUS" in danger_type or "POISONOUS" in danger_type:
                                species["category"] = "venomous"
                                species["color"] = "purple"
                            elif "AGGRESSIVE" in danger_type:
                                species["category"] = "aggressive"
                                species["color"] = "red"
                            else:
                                species["category"] = "harmless"
                                species["color"] = "orange" # Default for any other dangerous species
                            
                            # Set the danger description
                            danger_rating = parts[3].strip() if len(parts) > 3 else ""
                            danger_explanation = parts[4].strip() if len(parts) > 4 else ""
                            species["danger"] = f"{danger_rating}. {danger_explanation}"
        
        return species_list
    except Exception as e:
        print(f"Error analyzing species danger: {e}")
        # If OpenAI analysis fails, return the original list unchanged
        return species_list

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
                "danger": "Not flagged as dangerous",
                "source": "ALA"  # Mark source for deduplication
            }
            
            # Add to our species list if not already present
            if species_info not in species_list:
                species_list.append(species_info)
        
        # Use OpenAI to analyze species danger levels
        if species_list:
            species_list = analyze_species_danger(species_list)

        print(species_list)    
        return {"species": species_list, "total_records": total_records}
        
    except Exception as e:
        print(f"Error searching for species: {e}")
        return {"species": [], "total_records": 0}

def search_inaturalist_species(latitude, longitude, radius=5000, max_results=20):
    """
    Search for species near a location using the iNaturalist API, focused on NSW
    """
    # Define the API endpoint
    url = "https://api.inaturalist.org/v1/observations"
    
    # Convert radius to kilometers
    radius_km = radius / 1000
    
    # Define the query parameters - NSW has place_id 8170 in iNaturalist
    params = {
        "lat": latitude,
        "lng": longitude,
        "radius": radius_km,
        "per_page": max_results,
        "order_by": "observed_on",
        "place_id": 8170,  # ID for NSW, Australia
        "quality_grade": "research",  # More reliable observations
        "verifiable": "true"
    }
    
    try:
        # Make the API request
        response = requests.get(url, params=params)
        
        # Check if request was successful
        if not response.ok:
            print(f"iNaturalist API Error {response.status_code}: {response.text[:200]}...")
            return []
            
        # Parse the JSON response
        data = response.json()
        
        # Extract species information 
        species_list = []
        for result in data.get("results", []):
            if not result.get("taxon"):
                continue
                
            taxon = result["taxon"]
            species_info = {
                "scientific_name": taxon.get("name", "Unknown species"),
                "common_name": taxon.get("preferred_common_name", "No common name"),
                "lat": result.get("latitude"),
                "lng": result.get("longitude"),
                "danger": "Not flagged as dangerous",
                "source": "iNaturalist"  # Mark source for deduplication
            }
            
            # Add to species list
            species_list.append(species_info)
            
        return species_list
        
    except Exception as e:
        print(f"Error searching iNaturalist: {e}")
        return []

def combine_and_deduplicate_species(ala_species, inaturalist_species):
    """
    Combine species lists from multiple sources and remove duplicates
    """
    # Combine the lists
    combined_species = ala_species + inaturalist_species
    
    # Use a dictionary to track unique species by scientific name
    unique_species = {}
    
    for species in combined_species:
        # Create a normalized key for comparison
        sci_name = species["scientific_name"].lower()
        
        # Keep track of unique species, prioritizing ALA data when available
        if sci_name not in unique_species:
            unique_species[sci_name] = species
        elif species["source"] == "ALA" and unique_species[sci_name]["source"] == "iNaturalist":
            # Prefer ALA records over iNaturalist for the same species
            unique_species[sci_name] = species
    
    # Convert back to list
    return list(unique_species.values())

@app.route("/")
def index():
    return render_template("home.html")

@app.route("/species-finder")
def species_finder():
    return render_template("index.html")

@app.route("/toxicology")
def toxicology():
    return render_template("toxicology.html")

@app.route("/species", methods=["GET"])
def get_species_json():
    lat = request.args.get("lat", type=float)
    lng = request.args.get("lng", type=float)
    radius = request.args.get("radius", default=20000, type=int)
    max_results = request.args.get("max", default=50, type=int)
    kingdom = request.args.get("kingdom", default="Animalia")

    if lat is None or lng is None:
        return jsonify({"error": "Missing lat/lng parameters"}), 400

    try:
        # Get data from ALA
        ala_result = search_ala_species(lat, lng, radius, max_results, kingdom)
        ala_species = ala_result["species"]
        
        # Get data from iNaturalist (NSW-focused)
        inaturalist_species = search_inaturalist_species(lat, lng, radius, max_results)
        
        # Combine and deduplicate species lists
        combined_species = combine_and_deduplicate_species(ala_species, inaturalist_species)
        
        # Analyze danger levels for all species
        if combined_species:
            combined_species = analyze_species_danger(combined_species)
        
        # Transform data for frontend
        species_data = []
        for species in combined_species:
            species_data.append({
                "name": species["common_name"],
                "scientificName": species["scientific_name"],
                "lat": species["lat"],
                "lng": species["lng"],
                "danger": species["danger"],
                "category": species.get("category", "unknown"),
                "color": species.get("color", "gray"),
                "source": species.get("source", "unknown")
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
        # Get data from ALA
        ala_result = search_ala_species(lat, lng, radius, max_results, kingdom)
        ala_species = ala_result["species"]
        
        # Get data from iNaturalist
        inaturalist_species = search_inaturalist_species(lat, lng, radius, max_results)
        
        # Combine and deduplicate
        combined_species = combine_and_deduplicate_species(ala_species, inaturalist_species)
        
        # Analyze danger
        if combined_species:
            combined_species = analyze_species_danger(combined_species)
        
        # Transform data for template
        species_data = []
        for species in combined_species:
            species_data.append({
                "name": species["common_name"],
                "scientificName": species["scientific_name"],
                "lat": species["lat"],
                "lng": species["lng"],
                "danger": species["danger"],
                "category": species.get("category", "unknown"),
                "color": species.get("color", "gray"),
                "source": species.get("source", "unknown")
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
            print(f"{i}. {sp['scientific_name']} - {sp['common_name']} - {sp['danger']}")
    else:
        print(f"No species found at this location or an error occurred.")

if __name__ == "__main__":
    app.run(debug=True)