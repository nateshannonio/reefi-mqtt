# Migration from Python to YAML Configuration

The ReeFi MQTT Bridge now uses YAML configuration instead of Python files.

## What Changed

### Before (Python)
```python
# config.py
MQTT_BROKER = 'localhost'
MQTT_PORT = 1883

REEFI_DEVICES = [
    {
        'id': 'reefi_uno_pro_1',
        'name': 'Reefi Uno Pro 1',
        'ip': '192.168.1.100',
        'enabled': True
    }
]
```

### After (YAML)
```yaml
# config.yaml
mqtt:
  broker: localhost
  port: 1883

devices:
  - id: reefi_uno_pro_1
    name: Reefi Uno Pro 1
    ip: 192.168.1.100
    enabled: true
```

## Why YAML?

✅ **Easier to edit** - No Python syntax knowledge required  
✅ **Industry standard** - Used by Home Assistant, Docker, Kubernetes  
✅ **Better validation** - Clear error messages for syntax issues  
✅ **No code execution** - Safer than Python config files  
✅ **Comments supported** - Same as before  

## Migration Steps

If you were using the old Python config:

1. **Backup your old config**
   ```bash
   cp config.py config.py.backup
   ```

2. **Copy the YAML example**
   ```bash
   cp config.example.yaml config.yaml
   ```

3. **Transfer your settings**
   
   Open both `config.py.backup` and `config.yaml` and transfer your values.
   
   **Python → YAML mapping:**
   
   | Python | YAML |
   |--------|------|
   | `MQTT_BROKER = 'localhost'` | `mqtt:`<br>`  broker: localhost` |
   | `MQTT_PORT = 1883` | `mqtt:`<br>`  port: 1883` |
   | `MQTT_USERNAME = 'user'` | `mqtt:`<br>`  username: user` |
   | `REEFI_DEVICES = [...]` | `devices:`<br>`  - id: ...` |
   | `POLL_INTERVAL = 10` | `polling:`<br>`  interval: 10` |
   | `TEMPERATURE_UNIT = 'C'` | `settings:`<br>`  temperature_unit: C` |

4. **Test the new config**
   ```bash
   python3 reefi_mqtt.py
   ```

5. **Restart the service** (if installed)
   ```bash
   sudo systemctl restart reefi-mqtt
   ```

## File Locations

- Old: `config.py` (ignored by git)
- New: `config.yaml` (ignored by git)
- Example: `config.example.yaml` (committed to git)

## Breaking Changes

None! The functionality is identical, only the configuration format changed.

## Need Help?

If you encounter issues:
1. Check YAML syntax: https://yaml-online-parser.appspot.com/
2. Validate config: `python3 -c "import yaml; yaml.safe_load(open('config.yaml'))"`
3. Check logs: `sudo journalctl -u reefi-mqtt -n 50`

