from openai import OpenAI # Updated import
# Initialize the OpenAI client
client = OpenAI(api_key="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") # Replace with your actual API key
x = [
{"scientific_name": '"Eucymatoge" scotodes', "common_name": "Geometer Moth", "lat": -33.79, "lng": 151.2, "danger": "Not flagged as dangerous"},
{"scientific_name": '"Eucymatoge" scotodes', "common_name": "Geometer Moth", "lat": -33.78, "lng": 151.16, "danger": "Not flagged as dangerous"},
{"scientific_name": '"Eucymatoge" scotodes', "common_name": "Geometer Moth", "lat": -33.7, "lng": 151.1, "danger": "Not flagged as dangerous"},
{"scientific_name": '"Eucymatoge" scotodes', "common_name": "Geometer Moth", "lat": -33.8, "lng": 151.28, "danger": "Not flagged as dangerous"},
{"scientific_name": "'Ochlerotatus' ('Finlaya') quasirubithorax", "common_name": "No common name", "lat": -33.783329, "lng": 151.233307, "danger": "Not flagged as dangerous"},
{"scientific_name": "ACALYPTRATAE", "common_name": "No common name", "lat": -33.773195, "lng": 151.071118, "danger": "Not flagged as dangerous"},
{"scientific_name": "ACALYPTRATAE", "common_name": "No common name", "lat": -33.719533, "lng": 151.149078, "danger": "Not flagged as dangerous"},
{"scientific_name": "ACALYPTRATAE", "common_name": "No common name", "lat": -33.77195, "lng": 151.077689, "danger": "Not flagged as dangerous"},
{"scientific_name": "ACALYPTRATAE", "common_name": "No common name", "lat": -33.761929, "lng": 151.223709, "danger": "Not flagged as dangerous"},
{"scientific_name": "ACALYPTRATAE", "common_name": "No common name", "lat": -33.839906, "lng": 151.141086, "danger": "Not flagged as dangerous"},
{"scientific_name": "ACALYPTRATAE", "common_name": "No common name", "lat": -33.844045, "lng": 151.214737, "danger": "Not flagged as dangerous"},
{"scientific_name": "ACALYPTRATAE", "common_name": "No common name", "lat": -33.836303, "lng": 151.20618, "danger": "Not flagged as dangerous"},
{"scientific_name": "ACALYPTRATAE", "common_name": "No common name", "lat": -33.865375, "lng": 151.216308, "danger": "Not flagged as dangerous"},
{"scientific_name": "ACALYPTRATAE", "common_name": "No common name", "lat": -33.868016, "lng": 151.320663, "danger": "Not flagged as dangerous"},
{"scientific_name": "ACALYPTRATAE", "common_name": "No common name", "lat": -33.90352, "lng": 151.228302, "danger": "Not flagged as dangerous"},
{"scientific_name": "ACALYPTRATAE", "common_name": "No common name", "lat": -33.877772, "lng": 151.20212, "danger": "Not flagged as dangerous"},
{"scientific_name": "ACALYPTRATAE", "common_name": "No common name", "lat": -33.77173, "lng": 151.114063, "danger": "Not flagged as dangerous"},
{"scientific_name": "ACALYPTRATAE", "common_name": "No common name", "lat": -33.799191, "lng": 151.070482, "danger": "Not flagged as dangerous"},
{"scientific_name": "ACALYPTRATAE", "common_name": "No common name", "lat": -33.785517, "lng": 151.211916, "danger": "Not flagged as dangerous"},
{"scientific_name": "ACALYPTRATAE", "common_name": "No common name", "lat": -33.602488, "lng": 151.196517, "danger": "Not flagged as dangerous"},
{"scientific_name": "ACALYPTRATAE", "common_name": "No common name", "lat": -33.909088, "lng": 151.238997, "danger": "Not flagged as dangerous"},
{"scientific_name": "ACALYPTRATAE", "common_name": "No common name", "lat": -33.713326, "lng": 151.161357, "danger": "Not flagged as dangerous"},
{"scientific_name": "ACALYPTRATAE", "common_name": "No common name", "lat": -33.726575, "lng": 151.095227, "danger": "Not flagged as dangerous"},
{"scientific_name": "ACALYPTRATAE", "common_name": "No common name", "lat": -33.7645, "lng": 151.07689, "danger": "Not flagged as dangerous"},
{"scientific_name": "ACALYPTRATAE", "common_name": "No common name", "lat": -33.882261, "lng": 151.377826, "danger": "Not flagged as dangerous"},
{"scientific_name": "ACALYPTRATAE", "common_name": "No common name", "lat": -33.590056, "lng": 151.296842, "danger": "Not flagged as dangerous"},
{"scientific_name": "ACALYPTRATAE", "common_name": "No common name", "lat": -33.833219, "lng": 151.280426, "danger": "Not flagged as dangerous"},
{"scientific_name": "ACALYPTRATAE", "common_name": "No common name", "lat": -33.756802, "lng": 151.131266, "danger": "Not flagged as dangerous"},
{"scientific_name": "ACALYPTRATAE", "common_name": "No common name", "lat": -33.791438, "lng": 151.287549, "danger": "Not flagged as dangerous"},
{"scientific_name": "ACALYPTRATAE", "common_name": "No common name", "lat": -33.764593, "lng": 151.076848, "danger": "Not flagged as dangerous"},
{"scientific_name": "ACALYPTRATAE", "common_name": "No common name", "lat": -33.76285, "lng": 151.112729, "danger": "Not flagged as dangerous"},
{"scientific_name": "ACANTHIZIDAE", "common_name": "No common name", "lat": -33.694013, "lng": 151.292725, "danger": "Not flagged as dangerous"},
{"scientific_name": "ACANTHIZIDAE", "common_name": "No common name", "lat": -33.756979, "lng": 151.223426, "danger": "Not flagged as dangerous"},
{"scientific_name": "ACANTHIZIDAE", "common_name": "No common name", "lat": -33.781157, "lng": 151.089432, "danger": "Not flagged as dangerous"},
{"scientific_name": "ACANTHIZIDAE", "common_name": "No common name", "lat": -33.855782, "lng": 151.274441, "danger": "Not flagged as dangerous"},
{"scientific_name": "ACANTHOCEPHALA", "common_name": "Thorny-headed Worms", "lat": -33.65, "lng": 151.25, "danger": "Not flagged as dangerous"},
{"scientific_name": "ACANTHOCEPHALA", "common_name": "Thorny-headed Worms", "lat": -33.616, "lng": 151.266, "danger": "Not flagged as dangerous"},
{"scientific_name": "ACANTHOCHITONIDAE", "common_name": "No common name", "lat": -33.82832, "lng": 151.25027, "danger": "Not flagged as dangerous"},
{"scientific_name": "ACANTHOCHITONIDAE", "common_name": "No common name", "lat": -33.84833, "lng": 151.2686, "danger": "Not flagged as dangerous"},
{"scientific_name": "ACANTHOCHITONIDAE", "common_name": "No common name", "lat": -33.80166, "lng": 151.29666, "danger": "Not flagged as dangerous"},
{"scientific_name": "ACANTHOCHITONIDAE", "common_name": "No common name", "lat": -33.80833, "lng": 151.27304, "danger": "Not flagged as dangerous"},
{"scientific_name": "ACANTHOSOMATIDAE", "common_name": "No common name", "lat": -33.883335, "lng": 151.216705, "danger": "Not flagged as dangerous"},
{"scientific_name": "ACANTHOSOMATIDAE", "common_name": "No common name", "lat": -33.7986, "lng": 151.2846, "danger": "Not flagged as dangerous"},
{"scientific_name": "ACANTHURIDAE", "common_name": "Surgeonfish", "lat": -33.799048, "lng": 151.296435, "danger": "Not flagged as dangerous"},
{"scientific_name": "ACANTHURIDAE", "common_name": "Surgeonfish", "lat": -33.75, "lng": 151.433, "danger": "Not flagged as dangerous"}
]

response = client.chat.completions.create(
model="gpt-3.5-turbo", # You can replace with "gpt-4" or other models if needed
messages=[
{"role": "system", "content": "You are a helpful assistant."},
{"role": "user", "content": f"I will provide you with a python dictionary containing a bunch of species pulled from Atlas of Living Australia API. I would like you to loop through all of the speciies contained in the list, then make a call on whether it is dangerous or not. Here is the dictionary {x}. Your output should be a new dictioary, that gives the species english names and gives a danger rating 1/10. Strip the other data. Come up with top 10"}
],
max_tokens=150,
temperature=0.7
)
print("GPT Response:")
print(response.choices[0].message.content.strip())