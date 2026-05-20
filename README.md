# 🎤 Alexa Skills Kit — Kiro Power

Un **Kiro Power** pour développer, déployer et tester des skills Alexa directement depuis votre IDE.

## Fonctionnalités

| Outil MCP | Description |
|-----------|-------------|
| `list_skills` | Lister toutes les skills du compte |
| `create_skill` | Créer une skill depuis un template |
| `deploy_skill` | Déployer (modèle + code Lambda) |
| `test_skill` | Simuler une invocation vocale |
| `dialog_skill` | Conversation multi-tours |
| `get_skill_status` | Statut détaillé d'une skill |
| `get_skill_manifest` | Récupérer le manifest |
| `update_interaction_model` | Mettre à jour le modèle d'interaction |

## Prérequis

- **Python 3.10+**
- **Node.js 14+** (pour l'ASK CLI)
- **ASK CLI** installé et configuré :
  ```bash
  npm install -g ask-cli
  ask configure
  ```
- **Compte développeur Amazon** — [developer.amazon.com](https://developer.amazon.com)

## Installation dans Kiro

### Méthode 1 : Depuis un dépôt Git (recommandé)

1. Ouvrir le panneau **Powers** dans Kiro
2. Cliquer sur **"Add Custom Power"**
3. Sélectionner **"Git Repository"**
4. Coller l'URL de ce dépôt

### Méthode 2 : Depuis un dossier local

1. Cloner ce dépôt :
   ```bash
   git clone https://github.com/VOTRE_USERNAME/alexa-skills-kit-power.git
   ```
2. Installer les dépendances Python :
   ```bash
   pip install -r requirements.txt
   ```
3. Ouvrir le panneau **Powers** dans Kiro
4. Cliquer sur **"Add Custom Power"**
5. Sélectionner **"Local Directory"**
6. Indiquer le chemin absolu vers le dossier cloné

### Configuration MCP

Après installation, mettre à jour le chemin dans `mcp.json` :

```json
{
  "mcpServers": {
    "alexa-ask": {
      "command": "python3",
      "args": ["/chemin/vers/votre/dossier/server.py"],
      "env": {},
      "disabled": false
    }
  }
}
```

## Utilisation rapide

Une fois installé, demandez simplement à Kiro :

- *"Liste mes skills Alexa"*
- *"Crée une nouvelle skill Hello World en français"*
- *"Teste ma skill avec la phrase 'ouvre mon assistant'"*
- *"Déploie ma skill"*

## Structure du Power

```
alexa-skills-kit/
├── POWER.md            # Documentation complète (onboarding, workflows, troubleshooting)
├── mcp.json            # Configuration du serveur MCP
├── server.py           # Serveur MCP FastMCP (expose l'ASK CLI)
├── requirements.txt    # Dépendances Python
└── README.md           # Ce fichier
```

## Contribuer

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une PR pour :
- Ajouter de nouveaux outils MCP (ex: `submit_for_certification`, `get_metrics`)
- Améliorer la documentation
- Corriger des bugs

## Licence

MIT

---

**Auteur :** Olivier Calès  
**Compatible avec :** Kiro (IDE avec support Powers/MCP)
