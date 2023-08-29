import requests
import genanki
import re
import os

# Function to get taxon data from iNaturalist
def get_taxon_data(taxon_id):
    response = requests.get(f"https://api.inaturalist.org/v1/taxa/{taxon_id}")
    data = response.json()
    return data['results'][0]

# Function to get taxon photos from iNaturalist
def get_taxon_photos(taxon_photos):
    photos = ''
    for photo in taxon_photos:
        url = photo['photo']['medium_url']
        photos += f'<img src="{url}"><br>'
    return photos

# Function to get observation data from iNaturalist
def get_observations(taxon_id, num_observations):
    response = requests.get(f"https://api.inaturalist.org/v1/observations?taxon_id={taxon_id}&quality_grade=research&per_page={num_observations}")
    data = response.json()
    return data['results']

# Function to get observation photos from iNaturalist
def get_observation_photos(observation_photos):
    photos = ''
    for photo in observation_photos:
        url = photo['url']
        photos += f'<img src="{url}"><br>'
    return photos

# Define the Anki model
def create_model(num_observations):
    fields = [
        {'name': 'CommonName'},
        {'name': 'ScientificName'},
        {'name': 'WikipediaSummary'},
        {'name': 'CustomDescription'},
        {'name': 'iNaturalistID'},
        {'name': 'TaxonPhotos'},
    ]
    for i in range(1, num_observations + 1):
        fields.append({'name': f'Observation{i}Photos'})

    templates = [
        {
            'name': 'Taxon Card',
            'qfmt': '{{TaxonPhotos}}',
            'afmt': '{{FrontSide}}<hr id="answer">{{CommonName}}<br>{{ScientificName}}<br>{{WikipediaSummary}}<br>{{CustomDescription}}',
        },
    ]
    for i in range(1, num_observations + 1):
        templates.append({
            'name': f'Observation{i} Card',
            'qfmt': f'{{{{Observation{i}Photos}}}}',
            'afmt': '{{FrontSide}}<hr id="answer">{{CommonName}}<br>{{ScientificName}}<br>{{WikipediaSummary}}<br>{{CustomDescription}}',
        })

    model = genanki.Model(
        1607392319,
        'iNaturalist Model',
        fields=fields,
        templates=templates)

    return model

# Create the Anki deck
deck = genanki.Deck(2059400110, "iNaturalist Deck")

# Prompt the user for taxon URLs
num_observations = 10
taxon_urls = []
while True:
    taxon_url = input("Enter taxon URL (or 'D' or 'Done' to finish): ")
    if taxon_url.lower() in ['d', 'done']:
        break
    taxon_urls.append(taxon_url)

# Process each taxon URL
for taxon_url in taxon_urls:
    # Extract the taxon ID from the URL
    taxon_id = taxon_url.split('/')[-1].split('-')[0]

    # Fetch taxon data from iNaturalist
    taxon_data = get_taxon_data(taxon_id)

    common_name = taxon_data['common_name']['name']
    scientific_name = taxon_data['name']
    wikipedia_summary = taxon_data['wikipedia_summary']
    custom_description = ''
    inaturalist_id = taxon_data['id']
    taxon_photos = get_taxon_photos(taxon_data['taxon_photos'])

    # Fetch observation data from iNaturalist
    observations = get_observations(taxon_id, num_observations)

    observation_photos = []
    for observation in observations:
        observation_photos.append(get_observation_photos(observation['photos']))

    # Create the Anki note
    model = create_model(num_observations)
    fields = [
        common_name,
        scientific_name,
        wikipedia_summary,
        custom_description,
        str(inaturalist_id),
        taxon_photos,
    ]
    for observation_photo in observation_photos:
        fields.append(observation_photo)

    note = genanki.Note(
        model=model,
        fields=fields,
    )

    # Add the note to the deck
    deck.add_note(note)

# Save the deck to a file
genanki.Package(deck).write_to_file('iNaturalistDeck.apkg')

print("Anki deck created successfully!")
