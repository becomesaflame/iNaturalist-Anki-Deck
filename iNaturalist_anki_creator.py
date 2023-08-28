import requests
import genanki
import os
import urllib.request
import json
import base64

# iNaturalist API endpoint for getting taxon and observations
TAXON_ENDPOINT = "https://api.inaturalist.org/v1/taxa/"
OBSERVATIONS_ENDPOINT = "https://api.inaturalist.org/v1/observations"

# Save the images to a local directory
os.makedirs('media', exist_ok=True)
media_files = []

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

while True:
    # Prompt user for taxon URL and extract taxon ID
    taxon_url = input("Enter the taxon URL (or 'D' or 'Done' to finish): ")
    if taxon_url.lower() in ['d', 'done']:
        break
    taxon_id = taxon_url.split("/")[-1].split("-")[0]

    # Get the taxon information
    response = requests.get(TAXON_ENDPOINT + taxon_id)
    taxon_data = response.json()["results"][0]

    # Get the Wikipedia summary from the API
    wikipedia_summary = taxon_data["wikipedia_summary"]

    # Create a card for the taxon
    taxon_common_name = taxon_data["preferred_common_name"]
    taxon_name = taxon_data["name"]

    answer = f"Common Name: {taxon_common_name}<br>"
    answer += f"Taxon Name: {taxon_name}<br>"
    answer += f"Wikipedia Summary: {wikipedia_summary}"

    taxon_photos = taxon_data["taxon_photos"]
    img_data = ""
    for taxon_photo in taxon_photos:
        img_url = taxon_photo["photo"]["medium_url"]
        img_name = "taxon_" + os.path.basename(img_url)
        img_path = os.path.join('media', img_name)
        urllib.request.urlretrieve(img_url, img_path)
        media_files.append(img_path)
        img_data += f'<img src="{img_name}" /><br>'

    question = img_data

    taxon_card = genanki.Note(
        model=model,
        fields=[question, answer],
    )
    deck.add_note(taxon_card)

    # Define the parameters for the API request
    params = {
        "taxon_id": taxon_id,
        "quality_grade": "research",
        "per_page": 10,
    }

    # Get the observations
    response = requests.get(OBSERVATIONS_ENDPOINT, params=params)
    data = response.json()

    # Dump the results into a text file for debugging
    with open("data_results.txt", "w") as f:
        json.dump(data["results"], f, indent=4)

    # Iterate through the observations and add cards to the deck
    for observation in data["results"]:
        img_data = ""
        for idx, photo in enumerate(observation["photos"]):
            # Modify the URL to get the medium-sized image
            img_url = photo["url"].replace("square", "medium")
            # Download the image
            img_name = f"{observation['id']}_{idx}.jpg"
            img_path = os.path.join('media', img_name)
            urllib.request.urlretrieve(img_url, img_path)
            media_files.append(img_path)
            img_data += f'<img src="{img_name}" /><br>'
            
        question = img_data
        
        card = genanki.Note(
            model=model,
            fields=[question, answer],
        )
        deck.add_note(card)
        
# Generate the Anki package and include the media files
output_file = "iNaturalistDeck.apkg"
genanki.Package(deck, media_files=media_files).write_to_file(output_file)

print(f"Anki deck created: {output_file}")
