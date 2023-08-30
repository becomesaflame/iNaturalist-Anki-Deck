import os
import requests
import genanki
import re
import sys
import json
import urllib

# Function to write data to JSON file
def write_json_data(file_name, data):
    with open(file_name, 'w') as f:
        json.dump(data, f)

def anki_note_to_json(anki_note):
    return {
        'fields': anki_note.fields,
    }

def json_to_anki_note(model, note_data):
    return genanki.Note(
        model=model,
        fields=note_data['fields'],
    )
def read_json_file_to_anki_notes(file_name, model):
    anki_notes = []
    try:
        with open(file_name, 'r') as json_file:
            json_data = json.load(json_file)
            for note_data in json_data:
                anki_note = json_to_anki_note(model, note_data)
                anki_notes.append(anki_note)
    except FileNotFoundError:
        pass
    return anki_notes

def write_anki_notes_to_json_file(anki_notes, file_name):
    notes_json = [anki_note_to_json(note) for note in anki_notes]
    with open(file_name, 'w') as f:
        json.dump(notes_json, f, indent=4)

# Function to get the taxon_id from the URL
def get_taxon_id_from_url(taxon_url):
    return int(re.search(r'\d+', taxon_url).group())

# Function to get the taxon data from iNaturalist
def scrape_taxon_data(taxon_id):
    response = requests.get(f'https://api.inaturalist.org/v1/taxa/{taxon_id}')
    taxon_data = response.json()['results'][0]
    with open("taxon_data.json", 'w') as f:
        json.dump(taxon_data, f, indent=4)
    return taxon_data

# Function to get the observations data from iNaturalist
def scrape_observations_data(taxon_id, num_observations):
    response = requests.get(f'https://api.inaturalist.org/v1/observations?taxon_id={taxon_id}&quality_grade=research&per_page={num_observations}')
    observations_data = response.json()['results']
    with open("observation_data.json", 'w') as f:
        json.dump(observations_data, f, indent=4)
    return observations_data

# Function to download taxon photos and get local file paths
def download_taxon_photos(common_name, taxon_photos):
    sanitized_common_name = common_name.replace(' ', '_')
    photo_paths = []
    for i, photo in enumerate(taxon_photos):
        img_url = photo['photo']['medium_url']
        print(img_url)
        img_name = f"taxon_{sanitized_common_name}_{i}_{os.path.basename(img_url)}"
        img_path = os.path.join('media', img_name)
        urllib.request.urlretrieve(img_url, img_path)
        photo_paths.append(img_path)
    return photo_paths

# Function to download observation photos and get local file paths
def download_observation_photos(common_name, observation_photos):
    sanitized_common_name = common_name.replace(' ', '_')
    photo_paths = []
    for i, photo in enumerate(observation_photos):
        square_img_url = photo['url']
        img_url = square_img_url.replace('square', 'medium')
        img_name = f"observation_{sanitized_common_name}_{i}_{os.path.basename(img_url)}"
        img_path = os.path.join('media', img_name)
        urllib.request.urlretrieve(img_url, img_path)
        photo_paths.append(img_path)
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

# Function to create an Anki note
def create_anki_note(model, taxon_id, num_observations, media_files):
    
    # Fetch taxon data from iNaturalist
    taxon_data = scrape_taxon_data(taxon_id)

    common_name = taxon_data['preferred_common_name']
    scientific_name = taxon_data['name']
    wikipedia_summary = taxon_data['wikipedia_summary']
    custom_description = ''
    inaturalist_id = taxon_data['id']
    taxon_photo_paths = download_taxon_photos(common_name, taxon_data['taxon_photos'])
    media_files.extend(taxon_photo_paths)

    # Create HTML for taxon photos
    taxon_photos_html = '<br>'.join([f'<img src="{os.path.basename(path)}">' for path in taxon_photo_paths])

    # Fetch observation data from iNaturalist
    observations = scrape_observations_data(taxon_id, num_observations)

    # Create HTML for observation photos
    observation_photos_html = []
    for observation in observations:
        observation_photo_paths = download_observation_photos(common_name, observation['photos'])
        media_files.extend(observation_photo_paths)
        observation_photos_html.append('<br>'.join([f'<img src="{os.path.basename(path)}">' for path in observation_photo_paths]))
        
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

    return genanki.Note(
        model=model,
        fields=fields,
    )

# Main function
def main():
    file_name = sys.argv[1] if len(sys.argv) > 1 else 'deck_data.json'
    num_observations = 10

    # Save the images to a local directory
    os.makedirs('media', exist_ok=True)

    model = create_model(num_observations)
    deck = genanki.Deck(2059400110, "iNaturalist Deck")

    anki_notes = read_json_file_to_anki_notes(file_name, model)

    media_files = []
    # Prompt the user for taxon URLs
    while True:
        taxon_url = input("Enter the URL of a taxon, or enter 'D' or 'Done' to finish: ")
        if taxon_url.lower() in ['d', 'done', '']:
            break

        taxon_id = get_taxon_id_from_url(taxon_url)
        
        note = create_anki_note(model, taxon_id, num_observations, media_files)

        deck.add_note(note)

        anki_notes.append(note)

    write_anki_notes_to_json_file(anki_notes, file_name)

    # Save the deck to a file
    package = genanki.Package(deck)
    package.media_files = media_files
    package.write_to_file('iNaturalistDeck.apkg')

    print("Anki deck created successfully!")

if __name__ == "__main__":
    main()
