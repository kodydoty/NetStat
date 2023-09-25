import csv
import configparser
import logging
import requests
import speedtest
import time
from datetime import datetime
from pathlib import Path

# Load Configuration
config = configparser.ConfigParser()
config.read('config.ini')
server_url = config.get('Settings', 'ServerURL')
csv_file_path = Path(config.get('Settings', 'CSVFilePath'))
interval = config.getint('Settings', 'Interval')

# Set up Logging
logging.basicConfig(filename='speedtest.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def run_speedtest():
    st = speedtest.Speedtest()
    st.get_best_server()
    st.download()
    st.upload()
    return {
        "download_speed": st.results.download / (10**6),  # Convert to Mbps
        "upload_speed": st.results.upload / (10**6),  # Convert to Mbps
        "ping": st.results.ping,
        "server": st.results.server['host'],
        "timestamp": datetime.now().isoformat(),
        "additional_info": {"isp": st.results.client['isp']}
    }

def save_to_csv(result):
    file_exists = csv_file_path.exists()
    with open(csv_file_path, mode='a', newline='') as file:
        fieldnames = ['download_speed', 'upload_speed', 'ping', 'server', 'timestamp', 'additional_info']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()  # Write header if file does not exist
        writer.writerow(result)

def main():
    while True:
        try:
            speedtest_result = run_speedtest()
            save_to_csv(speedtest_result)
            response = requests.post(server_url, json=speedtest_result)
            response.raise_for_status()
            logging.info('Speedtest result successfully uploaded.')
        except requests.RequestException as e:
            logging.error(f'Could not send speedtest result: {e}')
        except Exception as e:
            logging.error(f'An unexpected error occurred: {e}')
        time.sleep(interval)

if __name__ == "__main__":
    main()
