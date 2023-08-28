# iNaturalist to Anki Script
This script fetches observations from iNaturalist based on a given taxon and creates an Anki flashcard deck with images and details of each observation.  

# Features
Prompts the user for taxon URLs and creates flashcards for each taxon.  
Creates a taxon card with all the photos for the taxon.  
Finds 10 research-grade observations for the given taxon and creates a card for each observation.  
Each observation card includes all the medium-sized images from the observation.  
The back of each card includes the common name, taxon name, default photo, and Wikipedia summary of the taxon.  
# Requirements  
Python 3.x  
requests library  
genanki library  
You can install the required libraries by running:  
  
```bash  
pip install requests genanki  
```  
# Usage  
Clone the repository or download the script.  
Run the script in a terminal:  
```bash
python inaturalist_to_anki.py  
```
The script will prompt you for a taxon URL. Enter the URL of the taxon page on iNaturalist, e.g., `https://www.inaturalist.org/taxa/52391-Pinus-strobus`. You can enter as many taxon URLs as you want, one at a time. Enter `D` or `Done` when you are finished.  

The script will fetch the taxon and observation data from iNaturalist and create an Anki deck with the cards.  

The Anki deck will be saved as iNaturalistDeck.apkg in the current directory.  

Import the .apkg file into Anki.  

You can run the script as many times as you want, importing the .apkg file into Anki each time. Anki will append the newly generated cards into the existing deck.  

# Notes
The script fetches only research-grade observations.  
The script fetches a maximum of 10 observations for each taxon.  
The script creates one card for the taxon and one card for each observation.  
The taxon card includes all the photos for the taxon.  
Each observation card includes all the medium-sized images from the observation.  
The back of each card includes the common name, taxon name, default photo, and Wikipedia summary of the taxon.  

# AI Credit
This script was written with the help of chatGPT (GPT-4). To view the chat and make updates to the script using ChatGPT, visit the following URL:    
https://chat.openai.com/share/e028daf5-c147-43b3-80be-9b62ffae7a52
