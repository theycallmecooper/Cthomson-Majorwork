from openai import OpenAI # Updated import
# Initialize the OpenAI client
client = OpenAI(api_key="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") # Replace with your actual API key

# Sample species data
x = [
{"scientific_name": '"Eucymatoge" scotodes', "common_name": "Geometer Moth", "lat": -33.79, "lng": 151.2, "danger": "Not flagged as dangerous"},
{"scientific_name": '"Eucymatoge" scotodes', "common_name": "Geometer Moth", "lat": -33.78, "lng": 151.16, "danger": "Not flagged as dangerous"},
{"scientific_name": '"Eucymatoge" scotodes', "common_name": "Geometer Moth", "lat": -33.7, "lng": 151.1, "danger": "Not flagged as dangerous"},
{"scientific_name": '"Eucymatoge" scotodes', "common_name": "Geometer Moth", "lat": -33.8, "lng": 151.28, "danger": "Not flagged as dangerous"},
{"scientific_name": "'Ochlerotatus' ('Finlaya') quasirubithorax", "common_name": "No common name", "lat": -33.783329, "lng": 151.233307, "danger": "Not flagged as dangerous"},
{"scientific_name": "ACALYPTRATAE", "common_name": "No common name", "lat": -33.773195, "lng": 151.071118, "danger": "Not flagged as dangerous"},
{"scientific_name": "ACANTHOCEPHALA", "common_name": "Thorny-headed Worms", "lat": -33.65, "lng": 151.25, "danger": "Not flagged as dangerous"},
{"scientific_name": "ACANTHOSOMATIDAE", "common_name": "No common name", "lat": -33.883335, "lng": 151.216705, "danger": "Not flagged as dangerous"},
{"scientific_name": "ACANTHURIDAE", "common_name": "Surgeonfish", "lat": -33.799048, "lng": 151.296435, "danger": "Not flagged as dangerous"},
{"scientific_name": "ACANTHURIDAE", "common_name": "Surgeonfish", "lat": -33.75, "lng": 151.433, "danger": "Not flagged as dangerous"}
]

# Create simplified list for OpenAI
simplified_species = []
for species in x:
    simplified_species.append({
        "scientific_name": species["scientific_name"],
        "common_name": species["common_name"]
    })

# Call OpenAI API
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant specialized in Australian wildlife."},
        {"role": "user", "content": f"I will provide you with a list of species. Please assess each species and determine if it's dangerous to humans on a scale of 1-10, where 10 is extremely dangerous. For each species, provide: common name, scientific name, danger rating, and a brief explanation of any hazards. Only list species with a danger rating of 3 or higher. Here's the list: {simplified_species}"}
    ],
    max_tokens=500,
    temperature=0.7
)

print("GPT Response:")
print(response.choices[0].message.content.strip())

# Update original data with danger information
danger_info = response.choices[0].message.content.strip()
for species in x:
    if species["scientific_name"] in danger_info:
        species_info = danger_info.split(species["scientific_name"])[1].split("\n")[0]
        if "dangerous" in species_info.lower() or "venomous" in species_info.lower() or "toxic" in species_info.lower():
            species["danger"] = species_info.strip()

print("\nUpdated species data:")
for species in x:
    if species["danger"] != "Not flagged as dangerous":
        print(f"{species['common_name']} - {species['scientific_name']} - {species['danger']}")