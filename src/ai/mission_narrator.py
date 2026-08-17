"""
Mission Narrator - Generates contextual mission briefings using Gemini AI.
Falls back to templates if API is unavailable.
"""

import random
from config import GEMINI_API_KEY, LLM_ENABLED


def generate_briefing_with_gemini(
    role_name, source, destination, steps, danger_zones_count
):
    """Generate briefing using Gemini API."""
    try:
        import google.generativeai as genai

        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.0-flash")

        prompt = f"""Generate a tactical mission briefing (2-3 sentences max) for a simulation game.

Role: {role_name}
From: {source}
To: {destination}
Route Steps: {steps}
Danger Zones in Area: {danger_zones_count}

Write in a {role_name.lower()} commanding officer's voice. Be dramatic but concise.
Army = military tactical tone
Rescuer = emergency medical responder tone  
Volunteer = humanitarian aid worker tone

Do not use markdown formatting. Plain text only."""

        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini API error: {e}")
        return None


def generate_briefing_template(
    role_name, source, destination, steps, danger_zones_count
):
    """Generate briefing using templates (fallback)."""
    templates = {
        "Army": [
            f"Attention, Alpha Team. Your objective is to move from {source} to {destination}. "
            f"Intel reports {danger_zones_count} hostile zones in the operational area. "
            f"Your route has been optimized for maximum safety, covering {steps} waypoints. "
            f"Maintain radio silence. Move out.",
            f"Command to Ground Unit. Proceed from {source} to {destination} via the secured corridor. "
            f"Avoid all {danger_zones_count} marked danger zones. Route consists of {steps} checkpoints. "
            f"Mission priority: SAFETY. Good luck, soldier.",
        ],
        "Rescuer": [
            f"Emergency Response Team, we have a situation. Navigate from {source} to {destination} immediately. "
            f"Time is critical. Your balanced route of {steps} segments accounts for both speed and safety. "
            f"Be aware of {danger_zones_count} hazardous areas. Lives depend on you. Go!",
            f"Rescue Unit deployed. Target location: {destination} from staging area {source}. "
            f"Route optimized for rapid response: {steps} waypoints. "
            f"Caution: {danger_zones_count} risk zones detected. Balance speed with safety.",
        ],
        "Volunteer": [
            f"Volunteer Team, thank you for your service. "
            f"Please deliver supplies from {source} to {destination}. "
            f"Your efficient route covers {steps} stops. "
            f"Note: {danger_zones_count} areas require extra caution. Stay safe and help others.",
            f"Aid Distribution Mission. Route from {source} to {destination} confirmed. "
            f"Balanced path with {steps} waypoints selected for efficiency. "
            f"Awareness: {danger_zones_count} zones marked as unstable. Proceed with care.",
        ],
    }

    role_templates = templates.get(role_name, templates["Volunteer"])
    return random.choice(role_templates)


def generate_briefing(role_name, source, destination, steps, danger_zones_count=0):
    """
    Generate a mission briefing. Uses Gemini AI if available, otherwise templates.
    """
    # Try Gemini API first if enabled
    if LLM_ENABLED:
        briefing = generate_briefing_with_gemini(
            role_name, source, destination, steps, danger_zones_count
        )
        if briefing:
            return briefing

    # Fallback to templates
    return generate_briefing_template(
        role_name, source, destination, steps, danger_zones_count
    )
