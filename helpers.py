import json
import re
import requests
import os

def pretty_print_table(data):
    if not data:
        return "Nessun risultato trovato."
    headers = data[0].keys()
    rows = [list(d.values()) for d in data]
    return json.dumps(data, indent=2, ensure_ascii=False)

# Estrai query tra i tag <SQL>
def extract_sql_from_response(text):
    match = re.search(r"<SQL>(.*?)</SQL>", text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else ""

# Estrai commenti prima e dopo
def split_explanation_and_comment(text):
    parts = re.split(r"<SQL>.*?</SQL>", text, flags=re.DOTALL | re.IGNORECASE)
    top = parts[0].strip() if len(parts) > 0 else ""
    bottom = parts[1].strip() if len(parts) > 1 else ""
    return top, bottom

def extract_table_name(response_text):
    match = re.search(r"Tabella:\s*(\S+)", response_text)
    return match.group(1) if match else None

#def extract_tables_explanations(schema_description):

def extract_field_explanations(schema_description, table_used):
    table_info = schema_description.get("tables", {}).get(table_used)
    if not table_info:
        return f"⚠️ La tabella '{table_used}' non è presente nello schema fornito."
    explanations = [f"Tabella/Vista: {table_used}\nDescrizione: {table_info.get('descrizione', '')}"]
    field_descs = table_info.get("campi", {})
    for field_name, field_desc in field_descs.items():
        explanations.append(f"- **{field_name}**: {field_desc}")
    return "\n".join(explanations)

def stream_llm_response(prompt, model="llama3"):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": model, "prompt": prompt, "stream": True},
        stream=True
    )

    for line in response.iter_lines():
        if line:
            try:
                data = json.loads(line.decode("utf-8"))
                yield data.get("response", "")
            except Exception:
                continue

def get_next_plot_filename(directory="plots", prefix="plot", extension=".png"):
    os.makedirs(directory, exist_ok=True)
    existing = [
        int(f[len(prefix):-len(extension)])
        for f in os.listdir(directory)
        if f.startswith(prefix) and f.endswith(extension) and f[len(prefix):-len(extension)].isdigit()
    ]
    next_number = max(existing, default=-1) + 1
    print(os.path.join(directory, f"{prefix}{next_number}{extension}"))
    return os.path.join(directory, f"{prefix}{next_number}{extension}")
