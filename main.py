import requests
import time
import json
import os
import random
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from openai import OpenAI

# Initialize OpenAI client
openai_client = OpenAI(api_key="")

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

class Species:
    """Class representing a wildlife species with its properties"""
    def __init__(self, scientific_name, common_name, lat=None, lng=None, source=None):
        self.scientific_name = scientific_name
        self.common_name = common_name or "No common name"
        self.lat = lat
        self.lng = lng
        self.danger = "Not flagged as dangerous"
        self.category = "unknown"
        self.color = "gray"
        self.source = source
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "name": self.common_name,
            "scientificName": self.scientific_name,
            "lat": self.lat,
            "lng": self.lng,
            "danger": self.danger,
            "category": self.category,
            "color": self.color,
            "source": self.source
        }
        
    def __eq__(self, other):
        """Allow comparison between species objects"""
        if not isinstance(other, Species):
            return False
        return self.scientific_name.lower() == other.scientific_name.lower()

# Load the common name lookup table
def load_common_name_lookup():
    """Load the common name lookup JSON file"""
    try:
        file_path = os.path.join(os.path.dirname(__file__), 'common_name_lookup.json')
        with open(file_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading common name lookup: {e}")
        return {"taxonomic_common_names": {}}

# Global variable to store the lookup table
common_name_lookup = load_common_name_lookup()

def get_common_name_from_taxonomy(scientific_name, taxonomy=None):
    """
    Try to find a common name based on taxonomic information
    
    Args:
        scientific_name (str): Scientific name of the species
        taxonomy (dict): Dictionary with class, order, family, genus keys (if available)
        
    Returns:
        str: Common name if found, otherwise None
    """
    if not scientific_name:
        return None
    
    lookup_data = common_name_lookup.get("taxonomic_common_names", {})
    
    # First check for a direct species match (most specific)
    species_lookup = lookup_data.get("species", {})
    if scientific_name in species_lookup:
        return species_lookup[scientific_name]
    
    # If we have taxonomy information from API
    if taxonomy:
        taxonomic_levels = ["genus", "family", "order", "class"]
        
        for level in taxonomic_levels:
            if taxonomy.get(level) and taxonomy.get(level) in lookup_data.get(level, {}):
                return lookup_data[level][taxonomy[level]]
    
    # If we don't have taxonomy info, try to extract genus from scientific name
    parts = scientific_name.split()
    if len(parts) > 0:
        genus = parts[0]
        if genus in lookup_data.get("genus", {}):
            return lookup_data["genus"][genus]
    
    return None

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
            # Prepare taxonomy data if available
            taxonomy = {
                "class": record.get("class"),
                "order": record.get("order"),
                "family": record.get("family"),
                "genus": record.get("genus")
            }
            
            # Get scientific name
            scientific_name = record.get("scientificName", "Unknown species")
            
            # Get common name, use lookup if not available
            common_name = record.get("vernacularName")
            if not common_name:
                common_name = get_common_name_from_taxonomy(scientific_name, taxonomy)
            
            # Fallback to "No common name" if still not found
            if not common_name:
                common_name = "No common name"
            
            species_info = {
                "scientific_name": scientific_name,
                "common_name": common_name,
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
            scientific_name = taxon.get("name", "Unknown species")
            
            # Get common name, use lookup if not available
            common_name = taxon.get("preferred_common_name")
            
            # Extract taxonomy if available
            taxonomy = {
                "class": taxon.get("ancestor_ids", {}).get("class"),
                "order": taxon.get("ancestor_ids", {}).get("order"),
                "family": taxon.get("ancestor_ids", {}).get("family"),
                "genus": taxon.get("ancestor_ids", {}).get("genus")
            }
            
            # Use lookup if no common name
            if not common_name:
                common_name = get_common_name_from_taxonomy(scientific_name, taxonomy)
            
            # Fallback if still not found
            if not common_name:
                common_name = "No common name"
            
            species_info = {
                "scientific_name": scientific_name,
                "common_name": common_name,
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

def combine_duplicate_species(ala_species, inaturalist_species):
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
        combined_species = combine_duplicate_species(ala_species, inaturalist_species)
        
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
        combined_species = combine_duplicate_species(ala_species, inaturalist_species)
        
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

@app.route("/dictionary")
def dictionary():
    return render_template("dictionary.html")

@app.route("/wildlife-spotlight")
def wildlife_spotlight():
    """Show a random wildlife species from the API data"""
    try:
        # Get a random species from our API-based search
        species = get_random_species_for_spotlight()
        
        if not species:
            # Fallback if no species found
            return render_template("spotlight.html", species=None)
            
        return render_template("spotlight.html", species=species)
    except Exception as e:
        print(f"Error in wildlife spotlight: {e}")
        return render_template("spotlight.html", species=None)

def get_random_species_for_spotlight():
    """Get a random Australian species with detailed information for spotlight feature"""
    # Australian coordinates to search in - major cities and landmarks
    australia_locations = [
        {"name": "Sydney", "lat": -33.8688, "lng": 151.2093},
        {"name": "Melbourne", "lat": -37.8136, "lng": 144.9631},
        {"name": "Brisbane", "lat": -27.4698, "lng": 153.0251},
        {"name": "Perth", "lat": -31.9505, "lng": 115.8605},
        {"name": "Uluru", "lat": -25.3444, "lng": 131.0369},
        {"name": "Great Barrier Reef", "lat": -18.2871, "lng": 147.6992},
        {"name": "Kakadu", "lat": -12.6981, "lng": 132.8064},
        {"name": "Tasmanian Wilderness", "lat": -42.8826, "lng": 146.3358}
    ]
    
    # Pick a random location
    location = random.choice(australia_locations)
    
    # Search for species at this location - using a larger radius for more results
    ala_results = search_ala_species(location["lat"], location["lng"], radius=50000, max_results=50)
    
    # Extract species list
    species_list = ala_results["species"]
    
    # Add iNaturalist results
    inaturalist_species = search_inaturalist_species(location["lat"], location["lng"], radius=50000, max_results=50)
    
    # Combine results
    all_species = combine_duplicate_species(species_list, inaturalist_species)
    
    # Filter to only include species with danger info (more interesting for spotlight)
    interesting_species = [s for s in all_species if s.get("danger") != "Not flagged as dangerous"]
    
    # If we don't have any interesting species, use the full list
    if not interesting_species and all_species:
        candidates = all_species
    else:
        candidates = interesting_species
    
    # If we still don't have any species, return None
    if not candidates:
        return None
    
    # Pick a random species
    selected_species = random.choice(candidates)
    
    # Format it for the spotlight template
    return enhance_species_for_spotlight(selected_species, location["name"])

def enhance_species_for_spotlight(species, location_name):
    """Add detailed information to a species object for display in the spotlight"""
    # Get the danger level based on the category
    danger_level = "low"
    if species.get("category") == "venomous":
        danger_level = "high"
    elif species.get("category") == "aggressive":
        danger_level = "medium"
    
    # Check if venomous based on category or danger info
    venomous = False
    if species.get("category") == "venomous" or "venom" in species.get("danger", "").lower():
        venomous = True
    
    # Generate badges based on available info
    badges = []
    if "Australia" in species.get("common_name", ""):
        badges.append("Endemic")
    
    # Try to determine if it's a reptile, mammal, etc. from the scientific name or common name
    animal_types = {
        "snake": "Reptile", "lizard": "Reptile", "turtle": "Reptile", 
        "spider": "Arachnid", "scorpion": "Arachnid",
        "fish": "Fish", "shark": "Fish", "ray": "Fish",
        "bird": "Bird", "eagle": "Bird", "hawk": "Bird", "parrot": "Bird",
        "mammal": "Mammal", "kangaroo": "Mammal", "wallaby": "Mammal", "possum": "Mammal",
        "jellyfish": "Marine", "octopus": "Marine", "crab": "Marine"
    }
    
    common_name_lower = species.get("common_name", "").lower()
    for key, animal_type in animal_types.items():
        if key in common_name_lower and animal_type not in badges:
            badges.append(animal_type)
            break
    
    # Get detailed species information using OpenAI
    detailed_info = get_detailed_species_info(species, badges, location_name)
    
    # Merge our basic info with the detailed info
    spotlight_species = {
        "name": species.get("common_name", "Unknown Species"),
        "scientific_name": species.get("scientific_name", "Unknown"),
        "danger_level": danger_level,
        "venomous": venomous,
        "badges": badges,
        "description": detailed_info.get("description", f"{species.get('common_name')} is an Australian native species found in various regions of Australia."),
        "size": detailed_info.get("size", "Variable depending on age and gender"),
        "habitat": detailed_info.get("habitat", f"Found in the {location_name} region of Australia"),
        "distribution": detailed_info.get("distribution", "Found in parts of Australia"),
        "diet": detailed_info.get("diet", "Varies based on available food sources"),
        "lifespan": detailed_info.get("lifespan", "Varies in wild and captivity"),
        "danger_info": species.get("danger", "") if danger_level != "low" else "",
        "fun_facts": detailed_info.get("fun_facts", [
            f"This specimen was recorded near {location_name}, Australia",
            f"Scientific classification: {species.get('scientific_name', '')}"
        ])
    }
    
    return spotlight_species

def get_detailed_species_info(species, badges, location_name):
    """Use OpenAI to get detailed information about a species"""
    try:
        animal_type = "animal"
        for badge in badges:
            if badge in ["Reptile", "Arachnid", "Fish", "Bird", "Mammal", "Marine"]:
                animal_type = badge.lower()
                break
        
        scientific_name = species.get("scientific_name", "")
        common_name = species.get("common_name", "")
        
        # Prepare the prompt for OpenAI
        prompt = f"""
        Please provide detailed factual information about {common_name} (Scientific name: {scientific_name}), 
        an Australian {animal_type}. Format your response as a JSON object with these fields:
        
        1. description: A 2-3 sentence description of the species
        2. size: Specific size information (length, weight, etc.)
        3. habitat: Detailed habitat preferences
        4. distribution: Where in Australia it can be found
        5. diet: What it eats
        6. lifespan: Typical lifespan in the wild and/or captivity
        7. fun_facts: An array of 3-4 interesting facts about this species
        
        Be accurate, specific, and concise. Include measurements where appropriate.
        If you don't have specific information for this species, provide plausible information based on related species.
        Do not include any disclaimers or explanations in your response - only the JSON object.
        """
        
        # Call OpenAI API
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant specialized in Australian wildlife biology."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,
            temperature=0.7
        )
        
        # Extract and parse the JSON response
        content = response.choices[0].message.content.strip()
        
        # Sometimes the model might include markdown code blocks or other formatting, so clean it up
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].strip()
            
        detailed_info = json.loads(content)
        return detailed_info
        
    except Exception as e:
        print(f"Error getting detailed species info: {e}")
        # Provide fallback data if API call fails
        return {
            "description": f"{common_name} ({scientific_name}) is a native Australian species found in the {location_name} region.",
            "size": "Size varies by individual",
            "habitat": f"Native to {location_name} and surrounding areas",
            "distribution": "Found in parts of Australia",
            "diet": "Consumes food typical for its species",
            "lifespan": "Several years in suitable conditions",
            "fun_facts": [
                f"This {animal_type} is adapted to the Australian environment",
                f"It was documented in biodiversity records near {location_name}",
                "Australia has many unique native species found nowhere else on Earth"
            ]
        }

@app.route("/wildlife-game")
def wildlife_game():
    """Interactive wildlife matching game"""
    return render_template("wildlife_game.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)