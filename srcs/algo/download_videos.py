import json
import logging
import yt_dlp as youtube_dl
from typing import Callable, Any, Optional
import re
import os
from algo import utils


class UrlData:
    def __init__(self, title: str, url: str):
        self.title = title
        self.url = url

    def __repr__(self):
        return f"UrlData(title={self.title}, url={self.url})"


def get_playlist_urls(playlist_url: str) -> list[UrlData]:
    ydl_opts = {
        'quiet': True,  # Suppress console output
        'extract_flat': True,  # Extract only URLs, no metadata
        'logger': logging.Logger("quiet", 60)
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            result = ydl.extract_info(playlist_url, download=False)
        except youtube_dl.utils.DownloadError:
            print(f"Error: Invalid url")
            return []

        if "entries" in result:
            return [UrlData(entry['title'], entry['url']) for entry in result['entries']]
        elif "webpage_url" in result and "title" in result:
            return [UrlData(result['title'], result['webpage_url'])]
        else:
            print(list(result))
            return []


def download_video(url: str, directory: str, title: str, progress_hook_func: Callable[[float], Any] = lambda d: None):
    downloaded_file_path: Optional[str] = None
    dst_basename = os.path.join(directory, title)
    dst_basename = utils.unique_basename(dst_basename)

    def _progress_hook(d):
        nonlocal downloaded_file_path
        # print(json.dumps(d, indent=2))
        if d['status'] == 'finished':
            progress_hook_func(1.0)
            downloaded_file_path = f"{d["info_dict"]["filename"]}"
        elif d['status'] == "downloading":
            progress_hook_func(int(d["downloaded_bytes"]) / int(d["total_bytes"]))
        else:
            progress_hook_func(0.0)

    ydl_opts = {
        'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
        'outtmpl': f"{dst_basename}.%(ext)s",
        'quiet': True,  # Suppress console output
        'progress_hooks': [_progress_hook],
        'logger': logging.Logger("quiet", level=60),
        'postprocessors': []
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    if downloaded_file_path is None:
        raise RuntimeError("Unable to retrieve downloaded path")
    return downloaded_file_path


def get_video_title(url: str) -> Optional[str]:
    """
    Retrieves the title of the video from the given URL.
    """
    ydl_opts = {
        'quiet': True,  # Suppress console output
        'extract_flat': True,  # Extract only URLs, no metadata
        'logger': logging.Logger("quiet", 60)
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(url, download=False)
            return info_dict.get('title', "Unknown")
        except youtube_dl.utils.DownloadError as exc:
            raise ValueError(exc)


def is_url_format(_str: str) -> bool:
    """
    Checks if the provided string is a valid URL using regex.
    """
    url_regex = re.compile(
        r'^(https?|ftp)://'  # Protocol
        r'(\S+:\S+@)?'  # Optional username:password@
        r'((([a-zA-Z0-9\-]+\.)+[a-zA-Z]{2,})|localhost|'  # Domain name or localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # OR IPv4 address
        r'\[[a-fA-F0-9:]+])'  # OR IPv6 address
        r'(:\d+)?'  # Optional port
        r'(/\S*)?$', re.IGNORECASE)  # Path and query string

    return re.match(url_regex, _str) is not None


def is_valid_url(_str: str) -> bool:
    if not is_url_format(_str):
        return False
    try:
        get_video_title(_str)
    except ValueError:
        return False
    return True


def test():
    # url = r"https://www.youtube.com/playlist?list=PLS19zOYsmnkwokOUuQC0Kw0M8HAdtWVYj"
    # all_data = get_playlist_urls(url)
    # print(all_data)
    # for data in all_data:
    #     print(data.title, data.url)
    import json
    # x = download_video(r"https://www.youtube.com/watch?v=0gsKxV3dmkU", "./test/", "testfilename2.txt", lambda p: print(p))
    x = get_video_title("https://www.youtube.com/playlist?list=PL3PKlQIgZgrtf0p5Hl_UUjs7v0T-b8PW1")
    print(x)


if __name__ == '__main__':
    test()
