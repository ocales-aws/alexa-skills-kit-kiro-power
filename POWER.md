---
name: "alexa-skills-kit"
displayName: "Alexa Skills Kit (ASK)"
description: "Créer, déployer et gérer des skills Alexa via l'ASK CLI. Inclut un serveur MCP pour automatiser le développement de skills et une documentation complète du workflow ASK."
keywords: ["alexa", "ask", "skill", "voice", "amazon", "echo", "lambda", "smapi"]
author: "Olivier Calès"
---

# Alexa Skills Kit (ASK)

## Overview

Ce power permet de développer des skills Alexa directement depuis Kiro. Il expose les commandes de l'ASK CLI via un serveur MCP pour automatiser la création, le déploiement et le test de skills vocales.

L'Alexa Skills Kit (ASK) est un ensemble d'APIs, d'outils et de documentation qui permet de créer des expériences vocales pour les appareils Alexa (Echo, Fire TV, etc.). Ce power couvre le cycle complet : création du projet, définition du modèle d'interaction, développement du backend Lambda, déploiement et test.

## Onboarding

### Prérequis

1. **Compte développeur Amazon** — Gratuit, créer sur [developer.amazon.com](https://developer.amazon.com)
2. **Node.js 14+** — Recommandé : version LTS courante. Vérifier avec `node --version`
3. **Git** — Nécessaire pour cloner les templates de skills
4. **Compte AWS** (optionnel) — Requis uniquement si tu héberges le backend sur Lambda (sinon Alexa-hosted)
5. **npm** — Inclus avec Node.js

### Installation de l'ASK CLI

```bash
# Installer l'ASK CLI globalement
npm install -g ask-cli

# Vérifier l'installation
ask --version

# Configurer les credentials (ouvre un navigateur pour l'auth Amazon)
ask configure

# Si pas de navigateur disponible :
ask configure --no-browser
```

### Configuration AWS (optionnel)

Si tu utilises AWS Lambda pour le backend :

```bash
# Configurer les credentials AWS
aws configure

# Ou utiliser un profil existant lors de `ask configure`
```

L'ASK CLI a besoin d'un utilisateur IAM avec les permissions suivantes :
- `AWSLambdaFullAccess`
- `IAMFullAccess` (pour créer les rôles Lambda)
- `CloudFormation` (si déploiement via CFN)

### Vérification

```bash
# Vérifier que tout est configuré
ask configure list

# Créer une skill de test
ask new
```

## Architecture d'une Skill Alexa

```
Utilisateur vocal → Appareil Alexa → Service Alexa (ASR/NLU/TTS)
    → Alexa Skills Kit → AWS Lambda (ou HTTPS endpoint)
    → DynamoDB / S3 / APIs externes
```

### Types de skills

| Type | Description | Complexité |
|------|-------------|------------|
| **Custom Skill** | Modèle d'interaction personnalisé | Élevée |
| **Smart Home Skill** | Contrôle d'appareils IoT | Moyenne |
| **Flash Briefing** | Contenu d'actualités | Faible |
| **Music Skill** | Streaming audio | Élevée |
| **Video Skill** | Contrôle vidéo | Élevée |

### Structure d'un projet skill

```
my-skill/
├── skill-package/
│   ├── skill.json              # Manifest de la skill
│   └── interactionModels/
│       └── custom/
│           └── fr-FR.json      # Modèle d'interaction français
├── lambda/
│   ├── index.js                # Handler Lambda (Node.js)
│   ├── package.json
│   └── util.js
├── ask-resources.json          # Config de déploiement ASK CLI
└── infrastructure/
    └── cfn-deployer/
        └── skill-stack.yaml    # Template CloudFormation
```

## Common Workflows

### Workflow 1 : Créer une nouvelle skill

```bash
# Créer un projet depuis un template
ask new

# Choisir :
# 1. Le runtime (Node.js, Python, Java)
# 2. Le template (Hello World, Fact Skill, etc.)
# 3. Le nom du projet
# 4. Le dossier de destination
```

**Templates disponibles :**
- Hello World — Skill minimale pour démarrer
- Fact Skill — Skill qui donne des faits aléatoires
- Quiz Game — Jeu de quiz interactif
- High Low Game — Jeu de devinettes
- Pet Match — Skill avec dialog management

### Workflow 2 : Développer le modèle d'interaction

Le modèle d'interaction définit comment l'utilisateur parle à ta skill.

**Concepts clés :**
- **Invocation Name** — Le mot-clé pour lancer la skill ("Alexa, ouvre ma skill")
- **Intents** — Les actions que l'utilisateur peut demander
- **Slots** — Les paramètres variables dans les phrases
- **Utterances** — Les phrases exemples pour chaque intent

**Exemple de modèle (fr-FR.json) :**
```json
{
  "interactionModel": {
    "languageModel": {
      "invocationName": "mon assistant",
      "intents": [
        {
          "name": "HelloIntent",
          "slots": [],
          "samples": [
            "bonjour",
            "salut",
            "dis bonjour"
          ]
        },
        {
          "name": "GetWeatherIntent",
          "slots": [
            {
              "name": "city",
              "type": "AMAZON.City"
            }
          ],
          "samples": [
            "quel temps fait-il à {city}",
            "la météo à {city}",
            "donne moi la météo de {city}"
          ]
        }
      ]
    }
  }
}
```

### Workflow 3 : Développer le backend Lambda

**Exemple Python (ask-sdk) :**
```python
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_request_type, is_intent_name

class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        speech = "Bonjour ! Comment puis-je vous aider ?"
        return handler_input.response_builder.speak(speech).ask(speech).response

class HelloIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("HelloIntent")(handler_input)

    def handle(self, handler_input):
        speech = "Salut ! Ravi de vous parler."
        return handler_input.response_builder.speak(speech).response

sb = SkillBuilder()
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(HelloIntentHandler())
lambda_handler = sb.lambda_handler()
```

**Exemple Node.js :**
```javascript
const Alexa = require('ask-sdk-core');

const LaunchRequestHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'LaunchRequest';
    },
    handle(handlerInput) {
        const speakOutput = 'Bonjour ! Comment puis-je vous aider ?';
        return handlerInput.responseBuilder
            .speak(speakOutput)
            .reprompt(speakOutput)
            .getResponse();
    }
};

exports.handler = Alexa.SkillBuilders.custom()
    .addRequestHandlers(LaunchRequestHandler)
    .lambda();
```

### Workflow 4 : Déployer la skill

```bash
# Déployer la skill (modèle + Lambda)
ask deploy

# Déployer uniquement le modèle d'interaction
ask deploy --target skill-metadata

# Déployer uniquement le code Lambda
ask deploy --target skill-infrastructure
```

### Workflow 5 : Tester la skill

```bash
# Tester en mode dialogue interactif
ask dialog --locale fr-FR

# Simuler une invocation
ask smapi simulate-skill --skill-id amzn1.ask.skill.xxx --locale fr-FR --input-content "ouvre mon assistant"

# Tester localement (debug)
ask run
```

### Workflow 6 : Publier la skill

```bash
# Soumettre pour certification
ask smapi submit-skill-for-certification --skill-id amzn1.ask.skill.xxx

# Vérifier le statut de certification
ask smapi get-certification-review --skill-id amzn1.ask.skill.xxx
```

## Commandes ASK CLI — Référence rapide

| Commande | Description |
|----------|-------------|
| `ask new` | Créer un nouveau projet skill |
| `ask deploy` | Déployer skill + infrastructure |
| `ask dialog` | Tester en mode conversation |
| `ask run` | Lancer le debug local |
| `ask smapi list-skills` | Lister toutes les skills |
| `ask smapi get-skill-status` | Statut d'une skill |
| `ask smapi simulate-skill` | Simuler une invocation |
| `ask smapi submit-skill-for-certification` | Soumettre pour publication |
| `ask configure` | Configurer les credentials |
| `ask util generate-lwa-tokens` | Générer des tokens LWA |

## Contraintes techniques

- **Timeout Lambda** : max 8 secondes (timeout du service Alexa)
- **Taille de réponse** : max 24 KB pour la réponse JSON
- **SSML** : max 8000 caractères par réponse vocale
- **Sessions** : persistent via DynamoDB (attributs de session)
- **Langues supportées** : fr-FR, en-US, en-GB, de-DE, ja-JP, etc.
- **Régions Lambda** : us-east-1 (NA), eu-west-1 (EU), ap-northeast-1 (FE)

## Troubleshooting

### Erreur : "Cannot find the environment variable: AWS_ACCESS_KEY_ID"

**Cause :** Credentials AWS non configurés pour le profil ASK.
**Solution :**
1. Relancer `ask configure` et sélectionner le bon profil AWS
2. Ou configurer manuellement : `aws configure --profile ask_cli_default`

### Erreur : "Can't find the vendor ID"

**Cause :** Informations du compte développeur incomplètes.
**Solution :**
1. Aller sur [developer.amazon.com/settings](https://developer.amazon.com/settings/console/myaccount.html)
2. Compléter le numéro de téléphone et les infos de paiement

### Erreur : "Lambda function can't be created"

**Cause :** Permissions IAM insuffisantes.
**Solution :**
1. Vérifier les policies IAM de l'utilisateur AWS
2. Ajouter `AWSLambdaFullAccess` et `IAMFullAccess`

### Erreur : Skill ne répond pas en test

**Cause possible :** Timeout Lambda > 8 secondes.
**Solution :**
1. Vérifier le timeout dans la config Lambda (< 8s)
2. Optimiser les appels API dans le handler
3. Utiliser DynamoDB DAX pour les lectures fréquentes

### Erreur : "Skill is not enabled for testing"

**Solution :**
```bash
ask smapi set-skill-enablement --skill-id amzn1.ask.skill.xxx --stage development
```

## Best Practices

- **Concevoir la voix d'abord** — Écrire les scripts de conversation avant de coder
- **Gérer les cas inattendus** — Toujours implémenter un FallbackIntent et un ErrorHandler
- **Réponses courtes** — Les utilisateurs préfèrent des réponses concises (< 30 secondes)
- **Reprompt** — Toujours inclure un reprompt pour garder la session ouverte
- **Persistance** — Utiliser DynamoDB pour sauvegarder l'état entre les sessions
- **Multi-locale** — Supporter plusieurs langues dès le début
- **Account Linking** — Utiliser OAuth 2.0 pour connecter des comptes tiers
- **Beta Testing** — Utiliser l'outil de beta test avant la soumission

## MCP Server — Outils disponibles

Le serveur MCP `alexa-ask` expose les commandes ASK CLI comme outils :

| Outil | Description |
|-------|-------------|
| `list_skills` | Lister toutes les skills du compte |
| `create_skill` | Créer une nouvelle skill depuis un template |
| `deploy_skill` | Déployer une skill (modèle + code) |
| `test_skill` | Simuler une invocation de skill |
| `get_skill_status` | Obtenir le statut d'une skill |
| `dialog_skill` | Envoyer un message en mode dialogue |
| `get_skill_manifest` | Récupérer le manifest d'une skill |
| `update_interaction_model` | Mettre à jour le modèle d'interaction |

## Ressources

- [Documentation officielle ASK](https://developer.amazon.com/en-US/docs/alexa/ask-overviews/what-is-the-alexa-skills-kit.html)
- [ASK CLI Reference](https://developer.amazon.com/en-US/docs/alexa/smapi/ask-cli-command-reference.html)
- [SMAPI Overview](https://developer.amazon.com/en-US/docs/alexa/smapi/smapi-overview.html)
- [ASK SDK Python](https://github.com/alexa/alexa-skills-kit-sdk-for-python)
- [ASK SDK Node.js](https://github.com/alexa/alexa-skills-kit-sdk-for-nodejs)
- [Alexa Developer Console](https://developer.amazon.com/alexa/console/ask)

## MCP Config Placeholders

- **`PLACEHOLDER_SERVER_PATH`** : Chemin vers le répertoire contenant `server.py` sur votre machine.
  - **Comment l'obtenir :**
    1. Clonez ce dépôt ou copiez le dossier `alexa-skills-kit` quelque part sur votre machine
    2. Notez le chemin absolu vers ce dossier (ex: `/Users/votrenom/powers/alexa-skills-kit`)
    3. Remplacez `PLACEHOLDER_SERVER_PATH` par ce chemin dans `mcp.json`

**Prérequis supplémentaire :** L'ASK CLI doit être installé et configuré (`npm install -g ask-cli && ask configure`).

---

**CLI Tool:** `ask-cli`
**Installation:** `npm install -g ask-cli`
**MCP Server:** `alexa-ask`
