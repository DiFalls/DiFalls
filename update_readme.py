import os
import json
import urllib.request

# --- Configurações ---
USERNAME = "Difalls"  # Usuário do GitHub
MAX_REPOS = 4         # Quantidade máxima de projetos para exibir
# ---------------------

def graphql_query(query):
    """Executa uma consulta na API GraphQL do GitHub."""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise Exception("GITHUB_TOKEN não encontrado nas variáveis de ambiente.")
        
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query}).encode(),
        headers={
            "Authorization": f"bearer {token}",
            "Content-Type": "application/json"
        }
    )
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())

def generate_cards(repos):
    """Gera o HTML dos cards para os repositórios."""
    cards_html = ""
    for i, repo in enumerate(repos):
        border_color = "00F0FF" if i % 2 == 0 else "00FF41"  # Alterna as cores das bordas
        card = f'''
  <a href="{repo['url']}">
    <img align="center" src="https://github-readme-stats-eight-theta.vercel.app/api/pin/?username={USERNAME}&repo={repo['name']}&theme=dark&bg_color=0D1117&title_color=00FF41&icon_color=00F0FF&text_color=C9D1D9&border_color={border_color}" />
  </a>'''
        cards_html += card
        # Quebra a linha a cada 2 cards para manter o layout lado a lado
        if (i + 1) % 2 == 0:
            cards_html += "<br/><br/>"
    return cards_html

def main():
    # Consulta GraphQL para buscar os repositórios mais recentes (excluindo o de perfil)
    query = f"""
    {{
      user(login: "{USERNAME}") {{
        repositories(first: {MAX_REPOS + 1}, orderBy: {{field: CREATED_AT, direction: DESC}}, privacy: PUBLIC, isFork: false) {{
          nodes {{
            name
            url
            description
          }}
        }}
      }}
    }}
    """
    
    result = graphql_query(query)
    repos = result["data"]["user"]["repositories"]["nodes"]
    
    # Filtra o repositório de perfil
    repos = [r for r in repos if r["name"].lower() != USERNAME.lower()]
    
    # Gera o HTML dos cards
    dynamic_cards = generate_cards(repos[:MAX_REPOS])
    
    # Lê o README atual
    with open("README.md", "r", encoding="utf-8") as f:
        readme_content = f.read()
    
    # Substitui o conteúdo entre os marcadores
    start_marker = "<!-- PROJECTS_START -->"
    end_marker = "<!-- PROJECTS_END -->"
    
    import re
    pattern = re.compile(f"{re.escape(start_marker)}.*?{re.escape(end_marker)}", re.DOTALL)
    new_content = f"{start_marker}\n{dynamic_cards}\n{end_marker}"
    
    if pattern.search(readme_content):
        readme_content = pattern.sub(new_content, readme_content)
    else:
        print("Marcadores não encontrados. Adicione <!-- PROJECTS_START --> e <!-- PROJECTS_END --> ao README.")
        return
    
    # Salva o README atualizado
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("README atualizado com sucesso!")

if __name__ == "__main__":
    main()
