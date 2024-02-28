import sys
import requests
from bs4 import BeautifulSoup
import os
import urllib.parse

def get_website_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print("Error fetching website content:", e)
        return None

def save_content_to_file(content, file_path):
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
            print("Content saved to", file_path)
    except IOError as e:
        print("Error saving content:", e)

def extract_resources(html_content, base_url):
    soup = BeautifulSoup(html_content, 'html.parser')
    resources = []
    
    # Extract CSS links
    css_links = [urllib.parse.urljoin(base_url, link.get('href')) for link in soup.find_all('link', rel='stylesheet')]
    resources.extend(css_links)
    
    # Extract JavaScript links
    js_links = [urllib.parse.urljoin(base_url, script.get('src')) for script in soup.find_all('script', src=True)]
    resources.extend(js_links)
    
    # Extract image links
    img_links = [urllib.parse.urljoin(base_url, img.get('src')) for img in soup.find_all('img', src=True)]
    resources.extend(img_links)
    
    # Extract font links
    font_links = [urllib.parse.urljoin(base_url, font.get('href')) for font in soup.find_all('link', rel='stylesheet', href=lambda x: ('.otf' in x) or ('.woff' in x) or ('.ttf' in x))]
    resources.extend(font_links)
    
    return resources

def download_and_save_resources(resource_links, output_directory):
    try:
        os.makedirs(output_directory, exist_ok=True)
        for link in resource_links:
            response = requests.get(link)
            if response.status_code == 200:
                filename = os.path.join(output_directory, os.path.basename(urllib.parse.urlsplit(link).path))
                with open(filename, 'wb') as file:
                    file.write(response.content)
                print("Resource saved:", filename)
            else:
                print("Failed to download resource:", link)
    except requests.exceptions.RequestException as e:
        print("Error fetching resource:", e)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python copy_website.py <website_url> <output_directory>")
        sys.exit(1)

    website_url = sys.argv[1]
    output_directory = sys.argv[2]

    website_content = get_website_content(website_url)
    if website_content:
        base_url = urllib.parse.urlparse(website_url).scheme + "://" + urllib.parse.urlparse(website_url).netloc
        resources = extract_resources(website_content, base_url)

        # Download and save resources
        download_and_save_resources(resources, output_directory)

        # Save HTML content
        save_content_to_file(website_content, os.path.join(output_directory, "index.html"))
