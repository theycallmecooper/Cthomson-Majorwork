<img alt="License" src="https://img.shields.io/badge/license-MIT-blue.svg">
<img alt="Python" src="https://img.shields.io/badge/python-3.6+-green.svg">
<img alt="Flask" src="https://img.shields.io/badge/flask-2.0+-yellow.svg">

<img alt="BushBuddy Banner" src="https://via.placeholder.com/1200x300?text=BushBuddy+-+Australian+Wildlife+Safety">
A comprehensive Australian wildlife safety application that helps identify potentially dangerous species in your vicinity and provides essential safety information.

🌟 Features
🔍 Species Finder - Identify wildlife in your area using geolocation
🧪 Toxicology Handbook - Detailed information about venomous creatures
📚 Scientific Dictionary - Learn about Australian wildlife terminology
🦘 Wildlife Spotlight - Discover random Australian species with detailed profiles
🎮 Wildlife Safety Game - Interactive matching game teaching safety tips
📷 Screenshots
<div align="center"> <img src="https://via.placeholder.com/400x225?text=Species+Finder" width="45%" alt="Species Finder"/> <img src="https://via.placeholder.com/400x225?text=Wildlife+Spotlight" width="45%" alt="Wildlife Spotlight"/> </div>
<div align="center"> <img src="https://via.placeholder.com/400x225?text=Toxicology+Guide" width="45%" alt="Toxicology Guide"/> <img src="https://via.placeholder.com/400x225?text=Wildlife+Game" width="45%" alt="Wildlife Game"/> </div>

# Clone the repository
git clone https://github.com/yourusername/bushbuddy.git
cd bushbuddy

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up your OpenAI API key
# Create a .env file and add: OPENAI_API_KEY=your_api_key_here

# Run the application
python main.py

⚙️ Technologies Used
Backend: Python, Flask
Frontend: HTML, CSS, JavaScript, Bootstrap
APIs:
Atlas of Living Australia
iNaturalist
OpenAI
