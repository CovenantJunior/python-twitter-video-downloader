import sys
import re
import logging
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def download_video(url, file_name):
    """Download a video from a URL into a filename.

    Args:
        url (str): The video URL to download.
        file_name (str): The file name or path to save the video to.
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        total_size = int(response.headers.get("content-length", 0))
        block_size = 1024
        progress_bar = tqdm(total=total_size, unit="B", unit_scale=True)

        download_path = Path.home() / "Downloads" / file_name

        with open(download_path, "wb") as file:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)

        progress_bar.close()
        logging.info("Video downloaded successfully!")

    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to download video: {e}")
    except OSError as e:
        logging.error(f"File error: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

def extract_video_info(url):
    """Extract the highest quality video URL and file name from a Twitter post.

    Args:
        url (str): The Twitter post URL to extract video info from.

    Returns:
        tuple: A tuple containing the highest quality video URL and sanitized file name.
    """
    try:
        api_url = f"https://twitsave.com/info?url={url}"
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an HTTPError for bad responses

        soup = BeautifulSoup(response.text, "html.parser")
        download_button = soup.find("div", class_="origin-top-right")
        quality_buttons = download_button.find_all("a")
        highest_quality_url = quality_buttons[0].get("href")  # Highest quality video URL

        file_name_elem = soup.find("div", class_="leading-tight").find("p", class_="m-2")
        file_name = file_name_elem.text if file_name_elem else "video"
        file_name = re.sub(r"[^a-zA-Z0-9]+", ' ', file_name).strip() + ".mp4"  # Remove special characters

        return highest_quality_url, file_name

    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to extract video info: {e}")
    except AttributeError as e:
        logging.error(f"Failed to parse video info: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
    return None, None

def download_twitter_video(url):
    """Download the highest quality video from a Twitter post URL.

    Args:
        url (str): The Twitter post URL to download from.
    """
    highest_quality_url, file_name = extract_video_info(url)
    if highest_quality_url and file_name:
        download_video(highest_quality_url, file_name)
    else:
        logging.error("Failed to download the video due to missing information.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logging.error("Please provide the Twitter video URL as a command line argument.\nEg: python twitter_downloader.py <URL>")
    else:
        url = sys.argv[1]
        if url:
            download_twitter_video(url)
        else:
            logging.error("Invalid Twitter video URL provided.")
