# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import requests
from bs4 import BeautifulSoup
from topic import Topic


def apicrawl():
    # Set up the YouTube Data API client
    a = Topic('fpv')
    a.exploreTopicDry()
    a.exploreChannels()
    a.persistChannels()

def crawl():
    # Set the URL of the YouTube page you want to scrape
    url = "https://www.youtube.com/@casey/videos/"

    # Send an HTTP GET request to the URL
    response = requests.get(url)

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, "html.parser")

    # Find all the video elements on the page
    video_elements = soup.find_all("a", class_="yt-simple-endpoint style-scope ytd-rich-grid-media")

    # Extract the title and creator name for each video
    for video_element in video_elements:
        title = video_element.get("title")
        creator = video_element.get("aria-label").split("by ", 1)[-1]

        # Print the title and creator name
        print("Title:", title)
        print("Creator:", creator)
        print()

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    apicrawl()
    crawl()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
