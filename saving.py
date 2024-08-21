import requests
import random
import json

class Song:
  def __init__(self):
    self.notes = []
    self.user_map = {
      '🐨': 'piano',
      '🐮': 'strings',
      '🐱': 'marimba',
      '🐻': 'woodwind',
      '🦊': 'synth',
      '🐶': 'drum-kit',
      '🐸': 'drum-machine',
    }

  def set_notes(self, notes):
    self.notes = notes

  def user_for_instrument(self, instrument):
    if instrument in self.user_map.values():
      return list(self.user_map.keys())[list(self.user_map.values()).index(instrument)]
    else:
      return self.user_for_instrument('piano')

  def _generate_save_name(self):
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-'
    return ''.join([random.choice(chars) for _ in range(20)])

  def save(self):
    name = self._generate_save_name()

    headers = {
      'accept': '*/*',
      'accept-language': 'en-US,en;q=0.9',
      'content-type': 'multipart/related; boundary=64189289727574746616889059869415',
      'origin': 'https://musiclab.chromeexperiments.com',
      'priority': 'u=1, i',
      'referer': 'https://musiclab.chromeexperiments.com/',
      'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
      'sec-ch-ua-mobile': '?0',
      'sec-ch-ua-platform': '"macOS"',
      'sec-fetch-dest': 'empty',
      'sec-fetch-mode': 'cors',
      'sec-fetch-site': 'cross-site',
      'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
      'x-firebase-storage-version': 'webjs/7.14.3',
      'x-goog-upload-protocol': 'multipart',
    }

    params = {
      'name': name,
    }

    song_data = {
      "notes": self.notes,
      "elapsed": max([note['end'] for note in self.notes]) + 10,
      "users": self.user_map,
      "keymap": {
        "white": {
          "0": {"note": "C", "pitch": "", "hidden": False},
          "2": {"note": "D", "pitch": "", "hidden": False},
          "4": {"note": "E", "pitch": "", "hidden": False},
          "5": {"note": "F", "pitch": "", "hidden": False},
          "7": {"note": "G", "pitch": "", "hidden": False},
          "9": {"note": "A", "pitch": "", "hidden": False},
          "11": {"note": "B", "pitch": "", "hidden": False}
        },
        "black": {
          "1": {"note": "C", "pitch": "♯", "hidden": False},
          "3": {"note": "D", "pitch": "♯", "hidden": False},
          "6": {"note": "F", "pitch": "♯", "hidden": False},
          "8": {"note": "G", "pitch": "♯", "hidden": False},
          "10": {"note": "A", "pitch": "♯", "hidden": False}
        }
      },
      "showNoteNames": False,
      "showEmojis": True
    }

    data = (f'--64189289727574746616889059869415\r\nContent-Type: application/json; charset=utf-8\r\n\r\n{{"name":"{name}","contentType":"application/json"}}\r\n--64189289727574746616889059869415\r\nContent-Type: application/json\r\n\r\n' + json.dumps(song_data) + '\r\n--64189289727574746616889059869415--').encode()

    response = requests.post(
      'https://firebasestorage.googleapis.com/v0/b/cl-sharedpiano.appspot.com/o',
      params=params,
      headers=headers,
      data=data,
    )

    return response.json()
