from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys # only needed to press enter, remove after openAI API is integrated
from langdetect import detect
from langdetect import DetectorFactory
DetectorFactory.seed = 0 # To ensure consistency in language detection
from openai import OpenAI
import deepl

# ISO 639-1 Language Codes
languages = {
    "af": "Afrikaans", "ar": "Arabic", "bg": "Bulgarian", "bn": "Bengali", "ca": "Catalan",
    "cs": "Czech", "cy": "Welsh", "da": "Danish", "de": "German", "el": "Greek",
    "en": "English", "es": "Spanish", "et": "Estonian", "fa": "Persian", "fi": "Finnish",
    "fr": "French", "gu": "Gujarati", "he": "Hebrew", "hi": "Hindi", "hr": "Croatian",
    "hu": "Hungarian", "id": "Indonesian", "it": "Italian", "ja": "Japanese", "kn": "Kannada",
    "ko": "Korean", "lt": "Lithuanian", "lv": "Latvian", "mk": "Macedonian", "ml": "Malayalam",
    "mr": "Marathi", "ne": "Nepali", "nl": "Dutch", "no": "Norwegian", "pa": "Punjabi",
    "pl": "Polish", "pt": "Portuguese", "ro": "Romanian", "ru": "Russian", "sk": "Slovak",
    "sl": "Slovenian", "so": "Somali", "sq": "Albanian", "sv": "Swedish", "sw": "Swahili",
    "ta": "Tamil", "te": "Telugu", "th": "Thai", "tl": "Tagalog", "tr": "Turkish",
    "uk": "Ukrainian", "ur": "Urdu", "vi": "Vietnamese", "zh-cn": "Chinese", "zh-tw": "Chinese"}
# Note zh-cn is Simplified Chinese while zh-tw is Traditional Chinese, but DeepL does not make a distinction

def show(step):
    "To print colored text in the terminal to show the program working."
    return '\033[94m' + step + '\033[0m'

def show_2(step):
    "To print a second color of colored text in the terminal to show the final output."
    return '\033[92m' + step + '\033[0m'

def find_element_if_present(id):
    "To check if an element exists."
    try:
        return driver.find_element(By.ID, id)
    except NoSuchElementException:
        return None

translator = "https://www.deepl.com/en/translator/"
ai = "https://chatgpt.com"
gpt_key = ""
demo = True # True for short text (1 sentence) / False for long text

prompt = input(show("Enter a prompt: "))
# prompt = '''¿Dispone la Biblioteca de SF de un servicio de impresión y, en caso afirmativo, cuál es su precio?'''

# For easier processing later, convert the prompt to a single line / PARAGRAPH*
prompt = prompt.replace('\n', ' ').replace('\r', '')

# Detect language and display detected language
language_code = detect(prompt)
language = languages[language_code]
print(show_2(f"Detected language: {language}."))

# To account for DeepL translation at the end
if language_code == "zh-cn":
    language_code = "zh-hans"
if language_code == "zh-tw":
    language_code = "zh-hant"
if language_code == "pt":
    language_code = "pt-br"
language_code = language_code.upper()

if language != "English":
    print(show("Opening translator..."))
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, timeout=20)
    driver.get(translator)
    # driver.fullscreen_window() # for fullscreen

    # Execute a Javascript script to remove the "Get Extension" pop-up (necessary - would block a button needed later)
    driver.execute_script("sessionStorage.setItem(\"LMT_browserExtensionPromo.displayed\", true)")

    # Send the prompt to be translated 
    driver.find_element(By.XPATH, "//*[@id=\"textareasContainer\"]/div[1]/section/div/div[1]/d-textarea/div[1]").send_keys(prompt)

    # Wait for initial translation & page to load - longer prompts need a longer wait time 
    driver.implicitly_wait(15)

    # Sequence of actions:
    driver.execute_script("window.scrollTo(0, 0)") # scroll to top of page
    driver.find_element(By.XPATH, "//*[@id=\"cookieBanner\"]/div/span/button").click() # click on Close Cookie Banner 

    try: 
        driver.find_element(By.ID, "headlessui-popover-button-:rk:").click()
    except NoSuchElementException:
        driver.find_element(By.ID, "headlessui-popover-button-:rj:").click()

    # lang_target = find_element_if_present(id="headlessui-popover-button-:rk:") # find Select Target Language element
    # if lang_target != None:
    #     lang_target.click() # click on Select Target Language if found
    # else:
    #     driver.find_element(By.ID, "headlessui-popover-button-:rj:").click() 

    driver.find_element(By.XPATH, "//button[8]/div/div/span").click() # click on English (American)

    if demo == True:
        # DeepL splits sentences into separate elements so for a demo only the first sentence is used.
        prompt = driver.find_element(By.XPATH, "//*[@id=\"textareasContainer\"]/div[3]/section/div[1]/d-textarea/div/p[1]/span[1]").text

    elif demo == False:
        
        prompt_tl = ""
        i = 1
        element_exists = True

        while element_exists:
            try:
                # Iterate through each span element in the first <p> and retrieve inner text (only for 1st PARAGRAPH*)
                sentence = driver.find_element(By.XPATH, f"//*[@id=\"textareasContainer\"]/div[3]/section/div[1]/d-textarea/div/p/span[{i}]").text
                prompt_tl += f"{sentence} " # add a space after every period
                i += 1
            except NoSuchElementException:
                element_exists = False

        prompt = prompt_tl

print(show_2(f"The prompt is: {prompt}"))
print(show("Opening AI..."))

# This is a 'fake' use of AI for show 
driver.get(ai)
driver.implicitly_wait(5)

# cloudflare = find_element_if_present(id="DPxlC8") # check for a cloudflare prompt
# if cloudflare is not None:
#     cloudflare.click() # submit cloudflare check if it exists
# else:
#     None
    
driver.find_element(By.XPATH, "//*[@id=\"prompt-textarea\"]/p").send_keys(prompt + Keys.RETURN)
driver.implicitly_wait(15)

# GPT Web Search
gpt_client = OpenAI(api_key=gpt_key)
instructions = '''
You are a highly capable and precise web library assistant. Your goal is to deeply understand the user's intent as pertains to information and service questions. The library is the Sandford Fleming Library, which can be shortened to the SF Library. Always prioritize being truthful, nuanced, insightful, and efficient, tailoring your responses specifically to the user's needs and preferences.
When I ask for help with a certain SF library service, you must search through a specific web domain to find relevant results. You may only use the web domain (and its sub-domains) below (delimited by triple quotes):
\"""https://engineering.library.utoronto.ca\"""
Your response must include a URL for every web page where results where found. The text output should also indicate any references using plain-text URLs enclosed by parentheses (). You must include at least one annotation in your response.
It is of utmost priority that you reference specific web pages (with URLs).
'''
prompt += " Please reference a specific web page and provide the URL in your response."

response = gpt_client.responses.create(
    model="gpt-4o", 
    instructions=instructions,
    input=prompt,
    tools=[{"type": "web_search_preview"}],
)
# print(response) # ONLY FOR TESTING

if language != "English":
    deepl_key = "95bb1296-7b6c-44a2-994d-515a64ae1700:fx"
    deepl_client = deepl.DeepLClient(deepl_key)
    response_tl = str(deepl_client.translate_text(response.output_text, target_lang=language_code, model_type='prefer_quality_optimized'))
    print(show_2(response_tl))
    sources = str(deepl_client.translate_text("Sources", target_lang=language_code, model_type='prefer_quality_optimized'))
    print(show(f"\n{sources}:\n- https://engineering.library.utoronto.ca"))
else:
    print(show_2(response.output_text))
    print(show("\nSources:\n- https://engineering.library.utoronto.ca"))

annotations = response.output[1].content[0].annotations
for source in annotations:
    print(show("- " + source.url))