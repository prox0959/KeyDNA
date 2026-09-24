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
        Robust to slight length differences across attempts due to typos or timing variations.
        TR: Birden fazla yazma örneğinin ortalamasını alarak güvenli bir kullanıcı profili oluşturur.
        Yazım hataları veya zamanlama farklılıklarından kaynaklanan uzunluk değişimlerini otomatik dengeler.
        """
        all_dwells = []
        all_flights = []
        
        for timings in multiple_timings:
            features = self.calculate_features(timings)
            if features['dwell']:
                all_dwells.append(features['dwell'])
            if features['flight']:
                all_flights.append(features['flight'])
            
        if not all_dwells:
            return {'mean_dwell': [], 'mean_flight': []}

        # TR: Heterojen liste uzunluklarını önlemek için güvenli sütun bazlı ortalama hesaplanır
        target_dwell_len = int(np.median([len(d) for d in all_dwells]))
        target_flight_len = int(np.median([len(f) for f in all_flights])) if all_flights else 0

        avg_dwell = []
        for col in range(target_dwell_len):
            vals = [d[col] for d in all_dwells if col < len(d)]
            if vals:
                avg_dwell.append(float(np.mean(vals)))

        avg_flight = []
        for col in range(target_flight_len):
            vals = [f[col] for f in all_flights if col < len(f)]
            if vals:
                avg_flight.append(float(np.mean(vals)))
        
        return {
            'mean_dwell': avg_dwell,
            'mean_flight': avg_flight
        }

    def verify(self, profile, current_timings):
        """
        Compare current typing against the saved profile using Manhattan distance.
        Returns match boolean and confidence percentage.
        TR: Mevcut yazma şeklini kaydedilmiş profil ile Manhattan mesafesi kullanarak karşılaştırır.
        """
        current_features = self.calculate_features(current_timings)
        
        c_dwell = current_features['dwell']
        c_flight = current_features['flight']
        
        p_dwell = profile.get('mean_dwell', [])
        p_flight = profile.get('mean_flight', [])
        
        if not p_dwell or not c_dwell:
            return False, 0.0

        min_dwell = min(len(c_dwell), len(p_dwell))
        min_flight = min(len(c_flight), len(p_flight))

        # Check if the length differs wildly (e.g. completely wrong phrase)
        len_diff = abs(len(c_dwell) - len(p_dwell))
        if len_diff > 4:
            return False, 0.0
            
        # Calculate Manhattan distance (absolute differences) for common positions
        # TR: Ortak tuş pozisyonları için Manhattan mesafesini hesaplıyoruz
        dwell_diff = sum(abs(c_dwell[i] - p_dwell[i]) for i in range(min_dwell))
        flight_diff = sum(abs(c_flight[i] - p_flight[i]) for i in range(min_flight))
        
        # Penalize slight length mismatch
        length_penalty = len_diff * 40.0
        total_distance = dwell_diff + flight_diff + length_penalty
        
        # Calculate confidence score (0 to 100)
        # TR: Güven skorunu hesapla (0 - 100 arası)
        confidence = max(0.0, 100.0 - (total_distance / self.threshold * 50.0))
        is_match = total_distance < self.threshold
        
        return is_match, round(confidence, 2)
