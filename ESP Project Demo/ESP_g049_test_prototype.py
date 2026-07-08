import deepl
from openai import OpenAI

'''
DeepL API: https://github.com/DeepLcom/deepl-python?tab=readme-ov-file
    - model-type (ModelType.PREFER_QUALITY_OPTIMIZED) for translation accuracy
OpenAI API: https://platform.openai.com/docs/overview
'''

def show(step):
    "To print colored text in the terminal to show the program working."
    return '\033[94m' + step + '\033[0m'

def show_2(step):
    "To print a second color of colored text in the terminal to show the final output."
    return '\033[92m' + step + '\033[0m'

deepl_key = ""
gpt_key = ""

# prompt = input(show("Enter a prompt: "))
prompt = "¿Dispone la Biblioteca de SF de un servicio de impresión y, en caso afirmativo, cuál es su precio?"

# DeepL Translation
tl = True # For testing
if tl == True:
    deepl_client = deepl.DeepLClient(deepl_key)
    prompt_tl = deepl_client.translate_text(prompt, target_lang="EN-US", model_type='prefer_quality_optimized')
    print(show(f"The detected language is: {prompt_tl.detected_source_lang}"))
    print(show(f"The translation is: {prompt_tl.text}"))
    prompt = str(prompt_tl)

# GPT Web Search
gpt_client = OpenAI(api_key=gpt_key)
instructions = '''
You are a highly capable and precise web library assistant. Your goal is to deeply understand the user's intent as pertains to information and service questions. The library is the Sandford Fleming Library, which can be shortened to the SF Library. Always prioritize being truthful, nuanced, insightful, and efficient, tailoring your responses specifically to the user's needs and preferences.
When I ask for help with a certain SF library service, you must search through a specific web domain and find relevant results. Focus primarily on the web domain (and its sub-domains) below (delimited by triple quotes), as well as any directly related websites:
\"""https://engineering.library.utoronto.ca\"""
The website above is the official website of the SF library.
If you are unable to completely answer the user's inquiry, you may expand your search range, but the website must be connected in some form to the domain given.
Your response must include annotations for every web page you used. The text output should also indicate any references using plain-text URLs enclosed by parentheses ().
'''
prompt += " Please reference a specific web page associated to the SF Library and provide the URL in your response."

response = gpt_client.responses.create(
    model="gpt-4o", 
    instructions=instructions,
    input=prompt,
    tools=[{"type": "web_search_preview"}],
)

# print(response) # ONLY FOR TESTING
print(show_2(response.output_text))
annotations = response.output[1].content[0].annotations
print(show("\nSources:"))
for source in annotations:
    print(show("-" + source.url))
