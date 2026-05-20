"""
MCP Server — Alexa Skills Kit (ASK CLI)
Expose les commandes ASK CLI comme outils MCP pour Kiro.
"""

import subprocess
import json
import os
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("alexa-ask")


def run_ask_command(args: list[str], cwd: str | None = None) -> str:
    """Exécute une commande ASK CLI et retourne le résultat."""
    try:
        result = subprocess.run(
            ["ask"] + args,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=cwd,
        )
        if result.returncode != 0:
            return f"❌ Erreur ASK CLI:\n{result.stderr.strip() or result.stdout.strip()}"
        return result.stdout.strip()
    except FileNotFoundError:
        return "❌ ASK CLI non trouvé. Installez-le avec: npm install -g ask-cli"
    except subprocess.TimeoutExpired:
        return "❌ Timeout: la commande a pris plus de 60 secondes."
    except Exception as e:
        return f"❌ Erreur inattendue: {str(e)}"


@mcp.tool()
def list_skills() -> str:
    """
    Liste toutes les skills Alexa du compte développeur.
    Retourne l'ID, le nom et le statut de chaque skill.
    """
    output = run_ask_command(["smapi", "list-skills"])
    if output.startswith("❌"):
        return output

    try:
        data = json.loads(output)
        skills = data.get("skills", [])
        if not skills:
            return "📋 Aucune skill trouvée sur ce compte."

        lines = ["📋 **Skills Alexa du compte :**\n"]
        for skill in skills:
            name_info = skill.get("nameByLocale", {})
            name = next(iter(name_info.values()), "Sans nom") if name_info else "Sans nom"
            skill_id = skill.get("skillId", "N/A")
            stage = skill.get("stage", "N/A")
            status = skill.get("publicationStatus", "N/A")
            lines.append(f"- **{name}**")
            lines.append(f"  - ID: `{skill_id}`")
            lines.append(f"  - Stage: {stage} | Status: {status}")
            lines.append("")

        return "\n".join(lines)
    except json.JSONDecodeError:
        return f"📋 Résultat brut:\n\n{output}"


@mcp.tool()
def create_skill(
    skill_name: str,
    runtime: str = "python",
    template: str = "hello-world",
    locale: str = "fr-FR",
    directory: str = ".",
) -> str:
    """
    Crée une nouvelle skill Alexa depuis un template.

    Args:
        skill_name: Nom de la skill à créer
        runtime: Runtime du backend (python, nodejs, java). Défaut: python
        template: Template à utiliser (hello-world, fact-skill, quiz-game). Défaut: hello-world
        locale: Locale de la skill (fr-FR, en-US, etc.). Défaut: fr-FR
        directory: Répertoire où créer le projet. Défaut: répertoire courant
    """
    # Construire la commande ask new avec les options
    args = [
        "new",
        "--skill-name", skill_name,
        "--template-url", f"https://github.com/alexa/skill-sample-{runtime}-{template}.git",
    ]

    output = run_ask_command(args, cwd=directory)
    if output.startswith("❌"):
        # Fallback: essayer la commande interactive avec des valeurs par défaut
        return (
            f"⚠️ La création automatique a échoué.\n\n"
            f"**Créez manuellement avec :**\n"
            f"```bash\ncd {directory}\n"
            f"ask new --skill-name \"{skill_name}\"\n```\n\n"
            f"Choisissez :\n"
            f"1. Runtime: {runtime}\n"
            f"2. Template: {template}\n"
            f"3. Locale: {locale}\n\n"
            f"Détail de l'erreur: {output}"
        )

    return (
        f"✅ **Skill créée avec succès !**\n\n"
        f"- Nom: {skill_name}\n"
        f"- Runtime: {runtime}\n"
        f"- Template: {template}\n"
        f"- Locale: {locale}\n"
        f"- Répertoire: {directory}/{skill_name}\n\n"
        f"**Prochaines étapes :**\n"
        f"1. `cd {skill_name}`\n"
        f"2. Modifier le modèle d'interaction dans `skill-package/interactionModels/`\n"
        f"3. Développer le handler dans `lambda/`\n"
        f"4. `ask deploy` pour déployer"
    )


@mcp.tool()
def deploy_skill(
    project_dir: str,
    target: str = "all",
) -> str:
    """
    Déploie une skill Alexa (modèle d'interaction + code Lambda).

    Args:
        project_dir: Chemin vers le répertoire du projet skill
        target: Cible du déploiement (all, skill-metadata, skill-infrastructure). Défaut: all
    """
    args = ["deploy"]
    if target != "all":
        args.extend(["--target", target])

    output = run_ask_command(args, cwd=project_dir)
    if output.startswith("❌"):
        return output

    target_desc = {
        "all": "modèle + infrastructure",
        "skill-metadata": "modèle d'interaction uniquement",
        "skill-infrastructure": "code Lambda uniquement",
    }

    return (
        f"✅ **Déploiement réussi !**\n\n"
        f"- Cible: {target_desc.get(target, target)}\n"
        f"- Projet: {project_dir}\n\n"
        f"**Résultat :**\n```\n{output}\n```\n\n"
        f"La skill est maintenant disponible en test. "
        f"Utilisez `test_skill` ou `dialog_skill` pour la tester."
    )


@mcp.tool()
def test_skill(
    skill_id: str,
    utterance: str,
    locale: str = "fr-FR",
) -> str:
    """
    Simule une invocation de skill Alexa avec une phrase utilisateur.

    Args:
        skill_id: ID de la skill (format: amzn1.ask.skill.xxx)
        utterance: Phrase à envoyer à la skill (ex: "ouvre mon assistant")
        locale: Locale pour le test (fr-FR, en-US, etc.). Défaut: fr-FR
    """
    args = [
        "smapi", "simulate-skill",
        "--skill-id", skill_id,
        "--locale", locale,
        "--input-content", utterance,
    ]

    output = run_ask_command(args)
    if output.startswith("❌"):
        return output

    try:
        data = json.loads(output)
        # Extraire la réponse vocale
        result = data.get("result", {})
        invocations = result.get("skillExecutionInfo", {}).get("invocations", [])

        if invocations:
            response = invocations[0].get("invocationResponse", {}).get("body", {})
            speech = response.get("response", {}).get("outputSpeech", {}).get("ssml", "Pas de réponse")
            reprompt = response.get("response", {}).get("reprompt", {}).get("outputSpeech", {}).get("ssml", "")

            lines = [
                f"🎤 **Test de skill**\n",
                f"- Utterance: \"{utterance}\"",
                f"- Locale: {locale}",
                f"- Skill: `{skill_id}`\n",
                f"**Réponse Alexa :**",
                f"> {speech}",
            ]
            if reprompt:
                lines.append(f"\n**Reprompt :** {reprompt}")

            return "\n".join(lines)

        return f"🎤 Résultat brut:\n```json\n{json.dumps(data, indent=2)}\n```"
    except json.JSONDecodeError:
        return f"🎤 Résultat:\n\n{output}"


@mcp.tool()
def get_skill_status(skill_id: str) -> str:
    """
    Récupère le statut détaillé d'une skill Alexa.

    Args:
        skill_id: ID de la skill (format: amzn1.ask.skill.xxx)
    """
    args = ["smapi", "get-skill-status", "--skill-id", skill_id]
    output = run_ask_command(args)
    if output.startswith("❌"):
        return output

    try:
        data = json.loads(output)
        manifest_status = data.get("manifest", {}).get("lastUpdateRequest", {}).get("status", "N/A")
        model_status = data.get("interactionModel", {})

        lines = [
            f"📊 **Statut de la skill**\n",
            f"- ID: `{skill_id}`",
            f"- Manifest: {manifest_status}",
        ]

        for locale, info in model_status.items():
            status = info.get("lastUpdateRequest", {}).get("status", "N/A")
            lines.append(f"- Modèle ({locale}): {status}")

        return "\n".join(lines)
    except json.JSONDecodeError:
        return f"📊 Résultat:\n\n{output}"


@mcp.tool()
def dialog_skill(
    skill_id: str,
    message: str,
    locale: str = "fr-FR",
) -> str:
    """
    Envoie un message en mode dialogue à une skill (simule une conversation).

    Args:
        skill_id: ID de la skill (format: amzn1.ask.skill.xxx)
        message: Message à envoyer dans le dialogue
        locale: Locale pour le dialogue (fr-FR, en-US, etc.). Défaut: fr-FR
    """
    # Utiliser simulate-skill pour le dialogue
    args = [
        "smapi", "simulate-skill",
        "--skill-id", skill_id,
        "--locale", locale,
        "--input-content", message,
    ]

    output = run_ask_command(args)
    if output.startswith("❌"):
        return output

    try:
        data = json.loads(output)
        sim_id = data.get("id", "")
        status = data.get("status", "")

        if status == "IN_PROGRESS":
            # Récupérer le résultat
            get_args = [
                "smapi", "get-skill-simulation",
                "--skill-id", skill_id,
                "--simulation-id", sim_id,
            ]
            output2 = run_ask_command(get_args)
            try:
                data = json.loads(output2)
            except json.JSONDecodeError:
                pass

        result = data.get("result", {})
        speech = "Pas de réponse"
        invocations = result.get("skillExecutionInfo", {}).get("invocations", [])
        if invocations:
            response_body = invocations[0].get("invocationResponse", {}).get("body", {})
            speech = response_body.get("response", {}).get("outputSpeech", {}).get("ssml", speech)

        return f"💬 **Dialogue**\n\n👤 Vous: \"{message}\"\n\n🔊 Alexa: {speech}"
    except json.JSONDecodeError:
        return f"💬 Résultat:\n\n{output}"


@mcp.tool()
def get_skill_manifest(skill_id: str, stage: str = "development") -> str:
    """
    Récupère le manifest complet d'une skill Alexa.

    Args:
        skill_id: ID de la skill (format: amzn1.ask.skill.xxx)
        stage: Stage de la skill (development, live). Défaut: development
    """
    args = [
        "smapi", "get-skill-manifest",
        "--skill-id", skill_id,
        "--stage", stage,
    ]

    output = run_ask_command(args)
    if output.startswith("❌"):
        return output

    try:
        data = json.loads(output)
        manifest = data.get("manifest", data)

        # Extraire les infos clés
        publishing = manifest.get("publishingInformation", {})
        locales = publishing.get("locales", {})
        apis = manifest.get("apis", {})

        lines = [f"📄 **Manifest de la skill** (`{skill_id}`)\n"]

        for locale, info in locales.items():
            lines.append(f"### {locale}")
            lines.append(f"- Nom: {info.get('name', 'N/A')}")
            lines.append(f"- Description: {info.get('summary', 'N/A')}")
            lines.append(f"- Invocation: {info.get('examplePhrases', ['N/A'])}")
            lines.append("")

        if apis:
            lines.append("### APIs")
            for api_type, api_info in apis.items():
                lines.append(f"- Type: {api_type}")
                endpoint = api_info.get("endpoint", {})
                if endpoint:
                    lines.append(f"  - Endpoint: {endpoint.get('uri', 'N/A')}")

        return "\n".join(lines)
    except json.JSONDecodeError:
        return f"📄 Manifest brut:\n\n{output}"


@mcp.tool()
def update_interaction_model(
    skill_id: str,
    model_path: str,
    locale: str = "fr-FR",
    stage: str = "development",
) -> str:
    """
    Met à jour le modèle d'interaction d'une skill depuis un fichier JSON.

    Args:
        skill_id: ID de la skill (format: amzn1.ask.skill.xxx)
        model_path: Chemin vers le fichier JSON du modèle d'interaction
        locale: Locale du modèle (fr-FR, en-US, etc.). Défaut: fr-FR
        stage: Stage de la skill (development, live). Défaut: development
    """
    # Vérifier que le fichier existe
    if not os.path.exists(model_path):
        return f"❌ Fichier non trouvé: {model_path}"

    args = [
        "smapi", "set-interaction-model",
        "--skill-id", skill_id,
        "--locale", locale,
        "--stage", stage,
        "--interaction-model", f"file:{model_path}",
    ]

    output = run_ask_command(args)
    if output.startswith("❌"):
        return output

    return (
        f"✅ **Modèle d'interaction mis à jour !**\n\n"
        f"- Skill: `{skill_id}`\n"
        f"- Locale: {locale}\n"
        f"- Fichier: {model_path}\n"
        f"- Stage: {stage}\n\n"
        f"Le modèle est en cours de build. "
        f"Utilisez `get_skill_status` pour vérifier la progression."
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
