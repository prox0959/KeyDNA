from flask import Flask, render_template, request, jsonify
import json
import os
from model import KeystrokeModel

# Initialize Flask application
# TR: Flask uygulamasını başlatıyoruz.
app = Flask(__name__)
model = KeystrokeModel()

PROFILES_FILE = 'profiles.json'

def load_profiles():
    """
    Load user profiles from the JSON file.
    TR: JSON dosyasından kullanıcı profillerini yükler.
    """
    if os.path.exists(PROFILES_FILE):
        with open(PROFILES_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_profiles(profiles):
    """
    Save user profiles to the JSON file.
    TR: Kullanıcı profillerini JSON dosyasına kaydeder.
    """
    with open(PROFILES_FILE, 'w') as f:
        json.dump(profiles, f)

@app.route('/')
def index():
    """
    Serve the main index.html page.
    TR: Ana sayfayı sunar.
    """
    return render_template('index.html')

@app.route('/enroll', methods=['POST'])
def enroll():
    """
    Endpoint to enroll a new user by calculating their typing profile.
    TR: Kullanıcının yazma profilini hesaplayarak yeni bir kullanıcı kaydetme uç noktası.
    """
    data = request.json
    username = data.get('username')
    timings_list = data.get('timings_list') # Expected to be a list of 5 timing lists
    
    if not username or not timings_list or len(timings_list) < 5:
        return jsonify({'error': 'Invalid data. Need username and 5 timing samples.'}), 400
        
    # Create the user profile using the ML model
    # TR: ML modelini kullanarak kullanıcı profilini oluşturuyoruz.
    profile = model.train_profile(timings_list)
    
    # Save the profile
    profiles = load_profiles()
    profiles[username] = profile
    save_profiles(profiles)
    
    return jsonify({'message': f'Profile for {username} enrolled successfully!', 'status': 'success'})

@app.route('/verify', methods=['POST'])
def verify():
    """
    Endpoint to verify a user based on their current typing timings.
    TR: Mevcut yazma zamanlamalarına göre bir kullanıcıyı doğrulama uç noktası.
    """
    data = request.json
    username = data.get('username')
    timings = data.get('timings') # A single timing list
    
    profiles = load_profiles()
    
    if username not in profiles:
        return jsonify({'error': 'User not found.'}), 404
        
    user_profile = profiles[username]
    
    # Verify using the ML model
    # TR: ML modelini kullanarak doğrulama yapıyoruz.
    is_match, confidence = model.verify(user_profile, timings)
    
    return jsonify({
        'match': is_match,
        'confidence': confidence,
        'message': 'Authentication successful!' if is_match else 'Imposter detected!'
    })

if __name__ == '__main__':
    # Start the Flask development server on port 5000
    # TR: Flask geliştirme sunucusunu 5000 portunda başlatır.
    app.run(debug=True, port=5000)
