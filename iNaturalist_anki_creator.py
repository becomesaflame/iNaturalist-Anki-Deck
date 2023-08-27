import requests
import genanki
import os
import urllib.request
import json
import base64

# Prompt user for species name and number of observations
species_name = input("Enter the species name: ")
num_observations = int(input("Enter the number of observations: "))

# iNaturalist API endpoint for getting observations
API_ENDPOINT = "https://api.inaturalist.org/v1/observations"

# Define the parameters for the API request
params = {
    "taxon_name": species_name,
    "quality_grade": "research",
    "per_page": num_observations,
}

# Make the API request
response = requests.get(API_ENDPOINT, params=params)
data = response.json()

# Dump the results into a text file for debugging
with open("data_results.txt", "w") as f:
    json.dump(data["results"], f, indent=4)

# Define the Anki Model
model = genanki.Model(
    1607392319,
    "Simple Model",
    fields=[
        {"name": "Question"},
        {"name": "Answer"},
    ],
    templates=[
        {
            "name": "Card 1",
            "qfmt": "{{Question}}",
            "afmt": "{{FrontSide}}<hr id='answer'>{{Answer}}",
        },
    ],
)

# Create a deck
deck = genanki.Deck(2059400110, "iNaturalist Deck")

# Iterate through the observations and add cards to the deck
for observation in data["results"]:
    img_data = ""
    for idx, photo in enumerate(observation["photos"]):
        # Modify the URL to get the medium-sized image
        img_url = photo["url"].replace("square", "medium")
        # Download the image
        img_name = f"{observation['id']}_{idx}.jpg"
        img_path = os.path.join(os.getcwd(), img_name)
        urllib.request.urlretrieve(img_url, img_path)
        
        # Convert image to base64
        with open(img_path, "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode("utf-8")
        img_data += f'<img src="data:image/jpeg;base64,{img_base64}" /><br>'
        
    question = img_data
    answer = species_name
    card = genanki.Note(
        model=model,
        fields=[question, answer],
    )
    deck.add_note(card)

# Generate the Anki package
output_file = "iNaturalistDeck.apkg"
genanki.Package(deck).write_to_file(output_file)

print(f"Anki deck created: {output_file}")
