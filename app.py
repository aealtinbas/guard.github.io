from flask import Flask, render_template, request
import requests
import pandas as pd
import tldextract
import socket
import urllib.parse
import joblib

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
    result = None
    if request.method == 'POST':
        url_input = request.form['url_input']
def resolve_short_url(short_url):
    if not isinstance(short_url, str):
        return short_url
    
    if not short_url.startswith('http'):
        short_url = 'http://' + short_url
    
    try:
        response = requests.head(short_url, allow_redirects=True, timeout=30)
        return response.url
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return short_url

def is_different_extension(short_url_input, long_url_result):
    url_extension = short_url_input.split('.')[-1].lower()
    long_url_extension = long_url_result.split('.')[-1].lower()
    return '1' if url_extension != long_url_extension else '0'

def count_digits_in_tld(url):
    ext = tldextract.extract(url)
    digit_count = len([char for char in ext.domain if char.isdigit()])
    return digit_count

def count_special_characters(url):
    dot_count = str(url).count('.')
    semicolon_count = str(url).count(';')
    slash_count = str(url).count('/')
    underscore_count = str(url).count('_')
    percent_sign_count = str(url).count('%')
    ampersand_count = str(url).count('&')
    colon_count = str(url).count(':')
    question_mark_count = str(url).count('?')
    plus_sign_count = str(url).count('+')
    backslash_count = str(url).count('\\')
    left_parenthesis_count = str(url).count('(')
    right_parenthesis_count = str(url).count(')')
    left_square_bracket_count = str(url).count('[')
    right_square_bracket_count = str(url).count(']')
    at_sign_count = str(url).count('@')
    comma_count = str(url).count(',')
    tilde_count = str(url).count('~')
    
    length = len(str(url))

    return {
        'Length': length,
        'Dot Count': dot_count,
        'Semicolon Count': semicolon_count,
        'Slash Count': slash_count,
        'Underscore Count': underscore_count,
        'Percent Sign Count': percent_sign_count,
        'Ampersand Count': ampersand_count,
        'Colon Count': colon_count,
        'Question Mark Count': question_mark_count,
        'Plus Sign Count': plus_sign_count,
        'Backslash Count': backslash_count,
        'Left Parenthesis Count': left_parenthesis_count,
        'Right Parenthesis Count': right_parenthesis_count,
        'Left Square Bracket Count': left_square_bracket_count,
        'Right Square Bracket Count': right_square_bracket_count,
        'At Sign Count': at_sign_count,
        'Comma Count': comma_count,
        'Tilde Count': tilde_count,
    }

def get_subdomain_count(url):
    try:
        domain_info = tldextract.extract(url)
        subdomain = domain_info.subdomain
        if subdomain and subdomain.lower() == "www":
            subdomain = None
        subdomains = subdomain.split('.') if subdomain else []
        subdomain_count = len(subdomains)
        return subdomain_count
    except Exception as e:
        print(f"Error: {e}")
        return 0

def add_http_prefix(url):
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "http://" + url
    return url

def get_host_from_url(url):
    try:
        parsed_url = urllib.parse.urlparse(url)
        hostname = parsed_url.hostname
        if hostname is None:
            return "Hostname couldn't be extracted from the URL."
        ip_address = socket.gethostbyname(hostname)
        return ip_address
    except Exception as e:
        return str(e)

def make_prediction(url_input):
    response = requests.get(url_input, timeout=5)
    time = response.elapsed.total_seconds()

    short_url_input = url_input
    long_url_result = resolve_short_url(short_url_input)
    isShort = is_different_extension(url_input, long_url_result)
    
    digit_count_result = count_digits_in_tld(url_input)
    
    result = count_special_characters(url_input)
    total_sum = sum(result.values())
    
    subdomain_count_result = get_subdomain_count(url_input)
    
    url_input_with_http = add_http_prefix(url_input)
    ip_address_result = get_host_from_url(url_input_with_http)
    ip_address_result_without_dots = ip_address_result.replace(".", "")

    prediction_data = pd.DataFrame({
        'time': [time],
        'short_url': [isShort],
        'number_of_Integer': [digit_count_result],
        'Length': [result.get('Length', 0)],
        'Dot_Count': [result.get('Dot Count', 0)],
        'Semicolon_Count': [result.get('Semicolon Count', 0)],
        'Slash_Count': [result.get('Slash Count', 0)],
        'Underscore_Count': [result.get('Underscore Count', 0)],
        'Percent_Sign_Count': [result.get('Percent Sign Count', 0)],
        'Ampersand_Count': [result.get('Ampersand Count', 0)],
        'Colon_Count': [result.get('Colon Count', 0)],
        'Question_Mark_Count': [result.get('Question Mark Count', 0)],
        'Plus_Sign_Count': [result.get('Plus Sign Count', 0)],
        'Backslash_Count': [result.get('Backslash Count', 0)],
        'Left_Parenthesis_Count': [result.get('Left Parenthesis Count', 0)],
        'Right_Parenthesis_Count': [result.get('Right Parenthesis Count', 0)],
        'Left_Square_Bracket_Count': [result.get('Left Square Bracket Count', 0)],
        'Right_Square_Bracket_Count': [result.get('Right Square Bracket Count', 0)],
        'At_Sign_Count': [result.get('At Sign Count', 0)],
        'Comma_Count': [result.get('Comma Count', 0)],
        'Tilde_Count': [result.get('Tilde Count', 0)],
        'Number_of_Special_Characters': [total_sum],
        'Subdomain_Count': [subdomain_count_result],
        'IP': [ip_address_result_without_dots]
    })

    loaded_model = joblib.load('random_forest_model.joblib')
    predictions = loaded_model.predict(prediction_data)

    #return predictions[0]

    result = make_prediction(url_input)
    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
