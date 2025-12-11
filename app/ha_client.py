import os
import requests
import logging

class HAClient:
    def __init__(self):
        self.supervisor_token = os.environ.get("SUPERVISOR_TOKEN")
        self.base_url = "http://supervisor/core/api"
        self.headers = {
            "Authorization": f"Bearer {self.supervisor_token}",
            "Content-Type": "application/json",
        }

    def get_state(self, entity_id):
        if not self.supervisor_token:
            logging.warning("Warning: SUPERVISOR_TOKEN not found. Cannot fetch entity state.")
            return None
            
        try:
            url = f"{self.base_url}/states/{entity_id}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Error fetching state for {entity_id}: {e}")
            return None

    def update_state(self, entity_id, state, attributes=None):
        if not self.supervisor_token:
            logging.warning("Warning: SUPERVISOR_TOKEN not found. Cannot update entity state.")
            return
            
        try:
            url = f"{self.base_url}/states/{entity_id}"
            data = {"state": state}
            if attributes:
                data["attributes"] = attributes
                
            response = requests.post(url, headers=self.headers, json=data)
            logging.info(f"HA API Response: {response.status_code} - {response.text}")
            response.raise_for_status()
            logging.info(f"Successfully updated {entity_id}")
        except Exception as e:
            logging.error(f"Error updating state for {entity_id}: {e}")

    def get_avg_temperature(self, sensor_ids):
        if not sensor_ids:
            return None
            
        total = 0
        count = 0
        
        for sensor in sensor_ids:
            state_data = self.get_state(sensor)
            if state_data and state_data.get("state") not in ["unknown", "unavailable"]:
                try:
                    val = float(state_data["state"])
                    logging.debug(f"DEBUG: Sensor {sensor} value: {val}")
                    total += val
                    count += 1
                except ValueError:
                    logging.debug(f"DEBUG: Sensor {sensor} has non-numeric state: {state_data['state']}")
                    pass
            else:
                 logging.debug(f"DEBUG: Sensor {sensor} state unavailable or None: {state_data}")
                    
        if count == 0:
            return None
            
        return total / count
