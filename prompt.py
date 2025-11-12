import requests
import json
from helpers import extract_field_explanations, stream_llm_response

## SQL Query lanciata a DB: 
# {sql_query}

def interpret_results(user_question, schema_description, sql_query, query_result):
    #field_explanation = extract_field_explanations(schema_description, table_used)
    prompt = f"""L'utente ha chiesto: "{user_question}"
            
## Ecco i dati ottenuti in JSON:
{json.dumps(query_result, indent=2)}

## Descrizione dei campi per interpretare gli acronimi nei dati:
{schema_description}

## Istruzioni:
Fornisci un'analisi dei dati concisa in italiano per rispondere alla domanda dell'utente, tenendo in considerazione la descrizione dei campi. \
Concludi ponendo all'utente due domande proattive su possibili prossime analisi o integrazioni dati. Metti queste domande sempre in **bold**\
es: Vuoi che ti generi anche...? o Vuoi confrontare anche...?
Non menzionare che stai rispondendo all'utente o ponendo le domande con un titole di sezione.
"""

    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    })
    return response.json().get("response", "").strip()

def interpret_results_stream(user_question, schema_description, table_used, query_result):

    prompt = f"""L'utente ha chiesto: "{user_question}"
            
## Ecco i dati ottenuti in JSON:
{json.dumps(query_result, indent=2)}

## Descrizione dei campi per interpretare gli acronimi nei dati:
{schema_description}

## Istruzioni:
Fornisci un'analisi dei dati concisa in italiano per rispondere alla domanda dell'utente, tenendo in considerazione la descrizione dei campi. \
Concludi ponendo all'utente due domande proattive su possibili prossime analisi o integrazioni dati. \
es: Vuoi che ti generi anche...? o Vuoi confrontare anche...?
Non menzionare che stai rispondendo all'utente o ponendo le domande con un titole di sezione.
"""

    for chunk in stream_llm_response(prompt):
        yield chunk
