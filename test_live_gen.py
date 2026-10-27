import sys
import urllib.request
import json
import os

sys.stdout.reconfigure(encoding='utf-8')
key = os.environ.get('GROQ_API_KEY')
if not key and os.path.exists('.env'):
    with open('.env', 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('GROQ_API_KEY='):
                key = line.split('=', 1)[1].strip().strip('"').strip("'")

recipe = {
    'title': 'Crispy South Indian Fermented Dosa',
    'citation': '[recipe_dosa_batter#version=reformulated-2025]',
    'servings': 4,
    'ingredients': '- 300.0 g idli parboiled rice\n- 100.0 g whole white urad dal\n- 1.0 tsp fenugreek seeds (methi)\n- 1.0 tsp rock salt\n- 2.0 tbsp sesame oil for roasting',
    'method': 'Soak rice and urad dal with fenugreek for 4 hours. Grind to smooth, airy batter. Ferment for 8 to 12 hours in a warm place until risen. Pour ladleful on hot seasoned cast iron tawa, spread thin in spiral, drizzle oil, and roast until golden and crispy.',
    'cook_time_note': 'Cook time remains strictly 10 minutes (does not scale linearly).'
}

prompt = f"""You are an expert chef and culinary assistant. The user asked: "How to prepare crispy dosa".
Synthesize an authentic, step-by-step culinary response using the verified test-kitchen data below.

VERIFIED RECIPE DATA:
Recipe: {recipe['title']} (Citation: {recipe['citation']})
Yield: {recipe['servings']} servings
Scaled Ingredients:
{recipe['ingredients']}
Method: {recipe['method']}
Safety/Timing Note: {recipe['cook_time_note']}

MANDATORY RULES:
1. You MUST include the exact citation "{recipe['citation']}" in the response.
2. Present the scaled ingredients clearly.
3. Provide step-by-step cooking instructions and 2 pro chef tips for maximum crispiness.
4. Keep the tone warm, conversational, and encouraging."""

url = 'https://api.groq.com/openai/v1/chat/completions'
data = {'model': 'qwen/qwen3.8-27b', 'messages': [{'role': 'user', 'content': prompt}], 'temperature': 0.3}
req = urllib.request.Request(
    url, 
    data=json.dumps(data).encode('utf-8'), 
    headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
)
resp = urllib.request.urlopen(req)
res = json.loads(resp.read().decode('utf-8'))
print('--- LIVE QWEN CHEF RESPONSE ---')
print(res['choices'][0]['message']['content'])

