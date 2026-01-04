import requests
import json
from typing import Dict, Any
from utils.logger import setup_logger

logger = setup_logger("groc_client")


class GrocClient:
    """
    Client for Groc AI story generation
    """

    def __init__(self, config: Dict[str, Any]):
        self.api_key = config['groc']['api_key']
        self.api_url = config['groc']['api_url']
        self.model = config['groc']['model']

    def generate_story_script(self, genre: str, previous_themes: list = None) -> Dict[str, Any]:
        """
        Generate a Pocket-FM style story script

        Args:
            genre: Story genre
            previous_themes: List of recently used themes to avoid repetition

        Returns:
            Dict containing script, title, and visual_prompt
        """
        try:
            # Build the prompt
            exclusion = ""
            if previous_themes:
                exclusion = f"\n\nDO NOT use these themes: {', '.join(previous_themes)}"

            prompt = f"""You are an expert Pocket-FM story writer. Create a 30-second dramatic story reel script in the {genre} genre.

REQUIREMENTS:
- Hook the viewer in the first 2 seconds with an emotional punch
- Use dramatic, engaging narration
- End with a cliffhanger
- Keep it to exactly 30 seconds of narration (about 70-80 words)
- Make it highly emotional and visual
- Use present tense for immediacy{exclusion}

Return ONLY valid JSON in this exact format:
{{
  "title": "Catchy title (5-8 words)",
  "script": "The full narration script",
  "visual_prompt": "Detailed cinematic scene description for Sora AI (focus on emotions, lighting, camera angles, character appearances)",
  "theme": "One-line theme description"
}}

Example for Romance:
{{
  "title": "He Left Her At The Altar",
  "script": "She stands alone in her white dress, flowers scattered on the ground. Everyone's staring. He texted her... three words that shattered everything. 'I can't, sorry.' Five years together. Gone. But what he doesn't know? She's carrying his child... and his billionaire brother just walked through those church doors.",
  "visual_prompt": "Cinematic shot of a devastated bride in an empty church, sunlight streaming through stained glass, tears rolling down her face, scattered rose petals on marble floor, shallow depth of field, emotional lighting, a mysterious well-dressed man entering in the background, dramatic shadows, film grain",
  "theme": "Abandoned bride discovers shocking pregnancy"
}}

Now create a unique {genre} story:"""

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are a Pocket-FM story expert. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.9,
                "max_tokens": 500
            }

            logger.info(f"Generating {genre} story script...")
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()

            result = response.json()
            content = result['choices'][0]['message']['content']

            # Extract JSON from response
            content = content.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            story_data = json.loads(content)

            logger.info(f"✓ Story generated: {story_data['title']}")
            return story_data

        except Exception as e:
            logger.error(f"Error generating story: {str(e)}")
            raise
        