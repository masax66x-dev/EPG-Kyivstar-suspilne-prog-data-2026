import json
import re

content_view_path = '/Users/MS-MBP14/Antigravity/APPM005/ProgramTable/ProgramTable/ContentView.swift'

with open(content_view_path, 'r', encoding='utf-8') as f:
    swift_code = f.read()

# Extract the translation dictionary
pattern = re.compile(r'let translationDict: \[String: String\] = \[\n(.*?)\]', re.DOTALL)
match = pattern.search(swift_code)

translations = {}
if match:
    dict_content = match.group(1)
    
    # Simple parsing of Swift dict entries
    # e.g., "Key": "Value",
    entry_pattern = re.compile(r'"((?:[^"\\]|\\.)*)":\s*"((?:[^"\\]|\\.)*)"')
    
    for entry_match in entry_pattern.finditer(dict_content):
        key = entry_match.group(1).replace('\\"', '"').replace('\\\\', '\\')
        val = entry_match.group(2).replace('\\"', '"').replace('\\\\', '\\')
        translations[key] = val

with open('/Users/MS-MBP14/Antigravity/APPM005/ProgramTableWeb/translations.json', 'w', encoding='utf-8') as f:
    json.dump(translations, f, ensure_ascii=False, indent=2)

print(f"Exported {len(translations)} translations to translations.json")
