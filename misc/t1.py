from pathlib import Path
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CONFIG_DIR = PROJECT_ROOT / "data-quality-firewall/config/"

yaml_file = CONFIG_DIR / "schema_contract.yaml"

print(yaml_file)

with yaml_file.open("r", encoding="utf-8") as file:
    config_dict = yaml.safe_load(file)


for k, v in config_dict.items():
    print(k, "->", v)


print(~True)