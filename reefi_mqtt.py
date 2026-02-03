#!/usr/bin/env python3
"""
ReeFi MQTT Bridge
Publishes ReeFi Uno Pro 2.1 data to MQTT with Home Assistant MQTT Discovery

License: MIT
"""

import requests
import json
import time
import logging
import signal
import sys
import yaml
import os
from typing import Dict, Optional
import paho.mqtt.client as mqtt

# Load configuration
def load_config(config_path='config.yaml'):
    """Load and validate configuration from YAML file"""
    if not os.path.exists(config_path):
        print(f"ERROR: {config_path} not found!")
        print(f"Copy config.example.yaml to {config_path} and update with your settings")
        sys.exit(1)
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except yaml.YAMLError as e:
        print(f"ERROR: Invalid YAML in {config_path}")
        print(e)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to load {config_path}")
        print(e)
        sys.exit(1)

# Load configuration
config = load_config()

# ============================================================
# LOGGING SETUP
# ============================================================

handlers = []
if config.get('logging', {}).get('console', True):
    handlers.append(logging.StreamHandler(sys.stdout))

log_file = config.get('logging', {}).get('file')
if log_file:
    try:
        handlers.append(logging.FileHandler(log_file))
    except PermissionError:
        print(f"WARNING: Cannot write to {log_file}, using console only")

logging.basicConfig(
    level=getattr(logging, config.get('logging', {}).get('level', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=handlers if handlers else [logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger('reefi-mqtt')

# ============================================================
# REEFI MQTT BRIDGE
# ============================================================

class ReefiBridge:
    """Bridge between ReeFi HTTP API and MQTT"""
    
    def __init__(self):
        self.mqtt_client = None
        self.running = False
        self.last_values = {}
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    def _on_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            logger.info("Connected to MQTT broker successfully")
            self._publish_discovery()
        else:
            logger.error(f"Failed to connect to MQTT broker with code {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """MQTT disconnection callback"""
        if rc != 0:
            logger.warning(f"Unexpected MQTT disconnection (code {rc}), will auto-reconnect")
    
    def _setup_mqtt(self):
        """Initialize MQTT client"""
        mqtt_config = config.get('mqtt', {})
        
        self.mqtt_client = mqtt.Client(client_id=mqtt_config.get('client_id', 'reefi-mqtt-bridge'))
        
        # Set callbacks
        self.mqtt_client.on_connect = self._on_connect
        self.mqtt_client.on_disconnect = self._on_disconnect
        
        # Set authentication if configured
        username = mqtt_config.get('username')
        password = mqtt_config.get('password')
        if username and password:
            self.mqtt_client.username_pw_set(username, password)
        
        # Set TLS if configured
        if mqtt_config.get('use_tls', False):
            ca_certs = mqtt_config.get('ca_certs')
            if ca_certs:
                self.mqtt_client.tls_set(ca_certs=ca_certs)
        
        # Get topic prefix
        topics_config = config.get('topics', {})
        topic_prefix = topics_config.get('prefix', 'homeassistant/sensor')
        
        # Set last will (availability)
        qos = mqtt_config.get('qos', 1)
        retain = mqtt_config.get('retain', True)
        
        self.mqtt_client.will_set(
            f"{topic_prefix}/reefi_bridge/availability",
            "offline",
            qos=qos,
            retain=retain
        )
        
        # Connect to broker
        broker = mqtt_config.get('broker', 'localhost')
        port = mqtt_config.get('port', 1883)
        
        logger.info(f"Connecting to MQTT broker at {broker}:{port}")
        self.mqtt_client.connect(broker, port, 60)
        
        self.mqtt_client.loop_start()
        
        # Publish online status
        time.sleep(1)
        self.mqtt_client.publish(
            f"{topic_prefix}/reefi_bridge/availability",
            "online",
            qos=qos,
            retain=retain
        )
    
    def _publish_discovery(self):
        """Publish MQTT discovery messages for Home Assistant"""
        logger.info("Publishing MQTT discovery messages")
        
        devices = config.get('devices', [])
        topics_config = config.get('topics', {})
        settings = config.get('settings', {})
        mqtt_config = config.get('mqtt', {})
        
        for device in devices:
            if not device.get('enabled', True):
                continue
            
            device_id = device['id']
            device_name = device['name']
            
            # Device info for grouping in HA
            device_info = {
                "identifiers": [device_id],
                "name": device_name,
                "manufacturer": "ReeFi",
                "model": "Uno Pro 2.1",
                "via_device": "reefi-mqtt-bridge"
            }
            
            # Define sensors
            temp_unit = settings.get('temperature_unit', 'C')
            sensors = [
                {
                    'id': 'temperature',
                    'name': 'Temperature',
                    'unit': '°C' if temp_unit == 'C' else '°F',
                    'device_class': 'temperature',
                    'state_class': 'measurement',
                    'icon': 'mdi:thermometer'
                },
                {
                    'id': 'power',
                    'name': 'Power',
                    'unit': 'W',
                    'device_class': 'power',
                    'state_class': 'measurement',
                    'icon': 'mdi:lightning-bolt'
                },
                {
                    'id': 'fan_rpm',
                    'name': 'Fan Speed',
                    'unit': 'RPM',
                    'icon': 'mdi:fan'
                },
                {
                    'id': 'mode',
                    'name': 'Mode',
                    'icon': 'mdi:lightbulb-on'
                },
                {
                    'id': 'moon_phase',
                    'name': 'Moon Phase',
                    'unit': '%',
                    'icon': 'mdi:moon-waning-crescent'
                }
            ]
            
            # Add channel sensors
            channels = [
                ('ch0', 'CH0 UV (400nm)', 'mdi:lightning-bolt'),
                ('ch1', 'CH1 Deep Violet (420nm)', 'mdi:flower'),
                ('ch2', 'CH2 Violet (435nm)', 'mdi:flower-outline'),
                ('ch3', 'CH3 Royal Blue (450nm)', 'mdi:water'),
                ('ch4', 'CH4 Blue (470nm)', 'mdi:water-outline'),
                ('ch5', 'CH5 Lime', 'mdi:circle'),
                ('ch6', 'CH6 Amber', 'mdi:circle-outline'),
                ('ch7', 'CH7 Warm White', 'mdi:white-balance-sunny'),
                ('ch8', 'CH8 Cool White', 'mdi:white-balance-incandescent')
            ]
            
            for ch_id, ch_name, icon in channels:
                sensors.append({
                    'id': ch_id,
                    'name': ch_name,
                    'unit': 'value',
                    'icon': icon
                })
            
            # Publish discovery for each sensor
            for sensor in sensors:
                self._publish_sensor_discovery(
                    device_id, 
                    device_name, 
                    sensor, 
                    device_info,
                    topics_config,
                    mqtt_config
                )
    
    def _publish_sensor_discovery(self, device_id, device_name, sensor, device_info, topics_config, mqtt_config):
        """Publish discovery for a single sensor"""
        sensor_id = sensor['id']
        unique_id = f"{device_id}_{sensor_id}"
        
        discovery_prefix = topics_config.get('discovery', 'homeassistant')
        topic_prefix = topics_config.get('prefix', 'homeassistant/sensor')
        
        config_topic = f"{discovery_prefix}/sensor/{device_id}/{sensor_id}/config"
        state_topic = f"{topic_prefix}/{device_id}/{sensor_id}/state"
        
        config_payload = {
            "name": f"{device_name} {sensor['name']}",
            "unique_id": unique_id,
            "state_topic": state_topic,
            "availability_topic": f"{topic_prefix}/reefi_bridge/availability",
            "icon": sensor['icon'],
            "device": device_info
        }
        
        # Add optional fields if present
        if 'unit' in sensor:
            config_payload['unit_of_measurement'] = sensor['unit']
        if 'device_class' in sensor:
            config_payload['device_class'] = sensor['device_class']
        if 'state_class' in sensor:
            config_payload['state_class'] = sensor['state_class']
        
        qos = mqtt_config.get('qos', 1)
        retain = mqtt_config.get('retain', True)
        
        self.mqtt_client.publish(
            config_topic,
            json.dumps(config_payload),
            qos=qos,
            retain=retain
        )
        
        logger.debug(f"Published discovery for {unique_id}")
    
    def _fetch_reefi_data(self, ip: str) -> Optional[Dict]:
        """Fetch data from ReeFi device"""
        polling_config = config.get('polling', {})
        timeout = polling_config.get('timeout', 5)
        
        try:
            # Fetch system info
            info_response = requests.get(
                f"http://{ip}/info4",
                timeout=timeout
            )
            info_response.raise_for_status()
            info_data = info_response.text
            
            # Fetch current state
            state_response = requests.get(
                f"http://{ip}/now.cfg",
                timeout=timeout
            )
            state_response.raise_for_status()
            state_data = state_response.text
            
            return self._parse_reefi_data(info_data, state_data)
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout fetching data from {ip}")
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error to {ip}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data from {ip}: {e}")
            return None
    
    def _parse_reefi_data(self, info_data: str, state_data: str) -> Dict:
        """Parse ReeFi data strings into structured dict"""
        data = {}
        settings = config.get('settings', {})
        
        # Parse system info (info4 endpoint)
        if 'gT=' in info_data:
            temp_f = float(info_data.split('gT=')[1].split(',')[0])
            temp_unit = settings.get('temperature_unit', 'C')
            if temp_unit == 'C':
                data['temperature'] = round((temp_f - 32) * 5/9, 1)
            else:
                data['temperature'] = round(temp_f, 1)
        
        if 'gW=' in info_data:
            data['power'] = round(float(info_data.split('gW=')[1].split(',')[0]), 1)
        
        if 'gRPM=' in info_data:
            data['fan_rpm'] = int(info_data.split('gRPM=')[1].split(',')[0])
        
        # Parse state info (now.cfg endpoint)
        if 'cMode=' in state_data:
            data['mode'] = state_data.split('cMode=')[1].split(',')[0]
        
        if 'cMoon=' in state_data:
            data['moon_phase'] = int(state_data.split('cMoon=')[1].split(',')[0])
        
        # Parse channel values
        for i in range(9):
            ch_key = f'nowch{i}='
            if ch_key in state_data:
                data[f'ch{i}'] = int(state_data.split(ch_key)[1].split(',')[0])
        
        return data
    
    def _publish_device_data(self, device_id: str, data: Dict):
        """Publish device data to MQTT (only if changed)"""
        if not data:
            return
        
        # Initialize last values for this device
        if device_id not in self.last_values:
            self.last_values[device_id] = {}
        
        published_count = 0
        
        topics_config = config.get('topics', {})
        mqtt_config = config.get('mqtt', {})
        polling_config = config.get('polling', {})
        
        topic_prefix = topics_config.get('prefix', 'homeassistant/sensor')
        publish_on_change = polling_config.get('publish_on_change', True)
        retain = mqtt_config.get('retain', True)
        
        for key, value in data.items():
            state_topic = f"{topic_prefix}/{device_id}/{key}/state"
            
            # Check if we should publish
            should_publish = True
            if publish_on_change:
                should_publish = self.last_values[device_id].get(key) != value
            
            if should_publish:
                self.mqtt_client.publish(
                    state_topic,
                    str(value),
                    qos=0,
                    retain=retain
                )
                self.last_values[device_id][key] = value
                published_count += 1
                logger.debug(f"{device_id}/{key} = {value}")
        
        if published_count > 0:
            logger.info(f"Published {published_count} updates for {device_id}")
    
    def _poll_devices(self):
        """Poll all enabled ReeFi devices"""
        devices = config.get('devices', [])
        
        for device in devices:
            if not device.get('enabled', True):
                continue
            
            logger.debug(f"Polling {device['name']} at {device['ip']}")
            
            data = self._fetch_reefi_data(device['ip'])
            if data:
                self._publish_device_data(device['id'], data)
            else:
                logger.warning(f"Failed to fetch data from {device['name']}")
    
    def run(self):
        """Main loop"""
        logger.info("Starting ReeFi MQTT Bridge")
        
        devices = config.get('devices', [])
        enabled_devices = [d['name'] for d in devices if d.get('enabled', True)]
        logger.info(f"Enabled devices: {enabled_devices}")
        
        # Setup MQTT
        self._setup_mqtt()
        
        # Wait for MQTT connection
        time.sleep(2)
        
        # Main polling loop
        self.running = True
        polling_config = config.get('polling', {})
        poll_interval = polling_config.get('interval', 10)
        
        logger.info(f"Starting polling loop (interval: {poll_interval}s)")
        
        try:
            while self.running:
                start_time = time.time()
                
                self._poll_devices()
                
                # Sleep for remainder of interval
                elapsed = time.time() - start_time
                sleep_time = max(0, poll_interval - elapsed)
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
        
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}", exc_info=True)
        
        finally:
            logger.info("Shutting down")
            
            # Publish offline status
            if self.mqtt_client:
                topics_config = config.get('topics', {})
                mqtt_config = config.get('mqtt', {})
                topic_prefix = topics_config.get('prefix', 'homeassistant/sensor')
                qos = mqtt_config.get('qos', 1)
                retain = mqtt_config.get('retain', True)
                
                self.mqtt_client.publish(
                    f"{topic_prefix}/reefi_bridge/availability",
                    "offline",
                    qos=qos,
                    retain=retain
                )
                
                self.mqtt_client.loop_stop()
                self.mqtt_client.disconnect()
            
            logger.info("Shutdown complete")

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    bridge = ReefiBridge()
    bridge.run()
