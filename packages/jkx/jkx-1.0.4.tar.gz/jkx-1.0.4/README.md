# json-key-explorer

CLI tool to explore the keys in a JSON file.

## Use Case

Useful for discovering the various key paths inside a large JSON file. Ignore the unwanted clutter inside the JSON and focus on the path that is important to you.

## Installation

```
pip install jkx
```

## Usage

```
jkx -f file.json
```

To print the JSON path in different formats, pass the following flags:

### JavaScript -js

```
jkx -f file.json -js

Example Output:
---------------
Path = data.servers[1].variables.region.enum[4]
```

### Python -py

```
jkx -f file.json -py

Example Output:
---------------
Path = data['servers'][1]['variables']['region']['enum'][4]
```
