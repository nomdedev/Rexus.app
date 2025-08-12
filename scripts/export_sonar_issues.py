import requests
import os

# NOTA: No subas tu token de SonarCloud a GitHub. Usa variables de entorno locales o un archivo .env que esté en .gitignore.
# Ejemplo: crea un archivo .env con SONAR_TOKEN=tu_token y usa python-dotenv para cargarlo si lo prefieres.

SONAR_TOKEN = os.getenv("SONAR_TOKEN") or "51846f984da5a1c7c65b2e459eda2f474d2e3611"
SONAR_ORG = "nomdedev"
SONAR_PROJECT = "RexusApp"
SONAR_URL = "https://sonarcloud.io/api/issues/search"

# Puedes cambiar el formato de salida a 'csv' o 'md' según prefieras
def fetch_issues(token, org, project, output_file="sonar_issues.md"):
    headers = {"Authorization": f"Basic {token}"}
    params = {
        "componentKeys": project,
        "organization": org,
        "types": "BUG,VULNERABILITY,CODE_SMELL,SECURITY_HOTSPOT",
        "ps": 500,  # page size
        "p": 1
    }
    all_issues = []
    while True:
        resp = requests.get(SONAR_URL, headers=headers, params=params)
        resp.raise_for_status()
        data = resp.json()
        all_issues.extend(data.get("issues", []))
        if params["p"] * params["ps"] >= data.get("total", 0):
            break
        params["p"] += 1

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"# Issues SonarCloud para {project}\n\n")
        for issue in all_issues:
            f.write(f"- [{issue['type']}] {issue['severity']} | {issue['component'].split(':')[-1]}:{issue['line']} | {issue['message']}\n")
    print(f"Exportados {len(all_issues)} issues a {output_file}")

if __name__ == "__main__":
    fetch_issues(SONAR_TOKEN, SONAR_ORG, SONAR_PROJECT)
