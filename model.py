import numpy as np

# TR: Bu sınıf klavye yazma dinamiklerini analiz eder ve profiller oluşturur.
# This class analyzes keystroke dynamics and creates profiles.
class KeystrokeModel:
    def __init__(self):
        # We define a threshold for authentication.
        # If the distance is lower than this threshold, we accept the user.
        # TR: Mesafe bu eşiğin altındaysa kullanıcıyı kabul ediyoruz.
        self.threshold = 150.0 

    def calculate_features(self, timings):
        """
        Calculate features (dwell and flight times) from a list of key events.
        TR: Tuş vuruşu zamanlamalarından özellikleri (basılı tutma ve uçuş süreleri) hesaplar.
        """
        dwell_times = []
        flight_times = []
        
        # We need a dictionary to keep track of when a key was pressed down
        press_times = {}
        last_release_time = None
        
        for event in timings:
            key = event['key']
            time = event['time']
            type = event['type']
            
            if type == 'keydown':
                # Record when the key was pressed
                press_times[key] = time
                
                # If we have a previous release time, we can calculate flight time
                # Flight time = time between previous key release and current key press
                # TR: Uçuş süresi = önceki tuşun bırakılması ile mevcut tuşun basılması arasındaki süre
                if last_release_time is not None:
                    flight_times.append(time - last_release_time)
                    
            elif type == 'keyup':
                if key in press_times:
                    # Dwell time = how long the key was held down
                    # TR: Basılı tutma süresi = tuşun ne kadar süre basılı tutulduğu
                    dwell_times.append(time - press_times[key])
                    del press_times[key]
                    
                last_release_time = time
                
        return {'dwell': dwell_times, 'flight': flight_times}

    def train_profile(self, multiple_timings):
        """
        Create a user profile by averaging features from multiple typing samples.
        TR: Birden fazla yazma örneğinin ortalamasını alarak bir kullanıcı profili oluşturur.
        """
        all_dwells = []
        all_flights = []
        
        for timings in multiple_timings:
            features = self.calculate_features(timings)
            all_dwells.append(features['dwell'])
            all_flights.append(features['flight'])
            
        # Calculate the mean (average) for each position in the lists
        # We use numpy to easily calculate the average across all attempts
        # TR: Tüm denemelerdeki ortalama değerleri hesaplıyoruz.
        avg_dwell = np.mean(all_dwells, axis=0).tolist() if all_dwells and len(all_dwells[0]) > 0 else []
        avg_flight = np.mean(all_flights, axis=0).tolist() if all_flights and len(all_flights[0]) > 0 else []
        
        return {
            'mean_dwell': avg_dwell,
            'mean_flight': avg_flight
        }

    def verify(self, profile, current_timings):
        """
        Compare current typing against the saved profile using Euclidean distance.
        Returns match boolean and confidence percentage.
        TR: Mevcut yazma şeklini kaydedilmiş profil ile karşılaştırır.
        """
        current_features = self.calculate_features(current_timings)
        
        c_dwell = current_features['dwell']
        c_flight = current_features['flight']
        
        p_dwell = profile['mean_dwell']
        p_flight = profile['mean_flight']
        
        # Check if the lengths match. If the user typed a different phrase, it won't match.
        if len(c_dwell) != len(p_dwell) or len(c_flight) != len(p_flight):
            return False, 0.0
            
        # Calculate Manhattan distance (absolute differences) for simplicity and robustness
        # TR: Basitlik ve sağlamlık için Manhattan mesafesini (mutlak farklar) hesaplıyoruz.
        dwell_diff = sum(abs(a - b) for a, b in zip(c_dwell, p_dwell))
        flight_diff = sum(abs(a - b) for a, b in zip(c_flight, p_flight))
        
        total_distance = dwell_diff + flight_diff
        
        # Calculate confidence score (0 to 100)
        # If distance is 0, confidence is 100%. As distance increases, confidence drops.
        confidence = max(0.0, 100.0 - (total_distance / self.threshold * 50.0))
        
        # The user is verified if the distance is below the threshold
        # TR: Eğer mesafe eşiğin altındaysa kullanıcı doğrulanmış olur.
        is_match = total_distance < self.threshold
        
        return is_match, round(confidence, 2)
