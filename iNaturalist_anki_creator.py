import requests
import genanki
import os
import urllib.request

# Function to get taxon data from iNaturalist
def get_taxon_data(taxon_id):
    response = requests.get(f"https://api.inaturalist.org/v1/taxa/{taxon_id}")
    data = response.json()
    return data['results'][0]

# Function to download taxon photos and get local file paths
def download_taxon_photos(taxon_photos):
    photo_paths = []
    for i, photo in enumerate(taxon_photos):
        url = photo['photo']['medium_url']
        photo_path = f'taxon_{i}.jpg'
        urllib.request.urlretrieve(url, photo_path)
        photo_paths.append(photo_path)
    return photo_paths

# Function to get observation data from iNaturalist
def get_observations(taxon_id, num_observations):
    response = requests.get(f"https://api.inaturalist.org/v1/observations?taxon_id={taxon_id}&quality_grade=research&per_page={num_observations}")
    data = response.json()
    return data['results']

# Function to download observation photos and get local file paths
def download_observation_photos(observation_photos):
    photo_paths = []
    for i, photo in enumerate(observation_photos):
        url = photo['url']
        photo_path = f'observation_{i}.jpg'
        urllib.request.urlretrieve(url, photo_path)
        photo_paths.append(photo_path)
    return photo_paths

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

# Create media files list
media_files = []

# Process each taxon URL
for taxon_url in taxon_urls:
    # Extract the taxon ID from the URL
    taxon_id = taxon_url.split('/')[-1].split('-')[0]

    # Fetch taxon data from iNaturalist
    taxon_data = get_taxon_data(taxon_id)

    common_name = taxon_data['preferred_common_name']
    scientific_name = taxon_data['name']
    wikipedia_summary = taxon_data['wikipedia_summary']
    custom_description = ''
    inaturalist_id = taxon_data['id']
    taxon_photo_paths = download_taxon_photos(taxon_data['taxon_photos'])
    media_files.extend(taxon_photo_paths)

    # Create HTML for taxon photos
    taxon_photos_html = '<br>'.join([f'<img src="{path}">' for path in taxon_photo_paths])

    # Fetch observation data from iNaturalist
    observations = get_observations(taxon_id, num_observations)

    # Create HTML for observation photos
    observation_photos_html = []
    for observation in observations:
        observation_photo_paths = download_observation_photos(observation['photos'])
        media_files.extend(observation_photo_paths)
        observation_photos_html.append('<br>'.join([f'<img src="{path}">' for path in observation_photo_paths]))

    # Create the Anki note
    model = create_model(num_observations)
    fields = [
        common_name,
        scientific_name,
        wikipedia_summary,
        custom_description,
        str(inaturalist_id),
        taxon_photos_html,
    ]
    for obs_photos_html in observation_photos_html:
        fields.append(obs_photos_html)

    note = genanki.Note(
        model=model,
        fields=fields,
    )

    # Add the note to the deck
    deck.add_note(note)

# Save the deck to a file
package = genanki.Package(deck)
package.media_files = media_files
package.write_to_file('iNaturalistDeck.apkg')

print("Anki deck created successfully!")
