import json
import numpy as np
import tkinter as tk
from tkVideoPlayer import TkinterVideo

class Matcher:
  def __init__(self, mappings_path, video_path):
    """
    args:
      - mappings_path: string *** Path to the mappings json file
      - video_path: string *** Path to the input video
    """
    self.mappings_path = mappings_path
    self.video_path = video_path

    self._load_mappings()

  def _load_mappings(self):
    """
    Loads the mapping from the json file

    args: None

    returns: None
    """
    with open(self.mappings_path, 'r') as f:
      self.mappings = json.loads(f.read())

  def match(self, timestamp, error_margin=5, render=False):
    """
    Matches the desired timestamp to either the exact or the closest corrolated video frame.
    
    args:
      - timestamp: string *** A string desired timestamp in the format of mm:ss or mmm:ss
      - error_margin: int *** A multiplicator of the error margin allowd for matching the desired timestamps in seconds
      - render: bool *** If true, the video of the timestampe will be rendered.
    
    returns:
      - match: string *** the exact or the closest corrolated video frame in the format of hh:mm:ss
    """
    mappings_list = []
    for item in self.mappings.keys():
      if item.replace(':', '').replace('+', '').isdigit():
        mappings_list.append(self._str_to_ms(item))

    # print(mappings_list)

    mappings_array = np.array(mappings_list)
    # mappings_array = np.array([self._str_to_ms(item) for item in self.mappings.keys() if item.split(':', '').isdigit()])
    timestamp = self._str_to_ms(timestamp)
    arg_min_dist = np.argmin(np.abs(mappings_array[:, 0] - timestamp[0]))
    min_dist = np.min(np.abs(mappings_array[:, 0] - timestamp[0]))
    if min_dist > error_margin * 1000 or mappings_array[arg_min_dist, 1] != timestamp[1]:
      print('No frames found within the error margin')
      return None
    
    print(f'Found frame with timestamp: {self._ms_to_time(mappings_array[arg_min_dist])}, with {self._ms_to_str(min_dist)} difference from desired timestamp.')
    match = self.mappings[self._ms_to_time(mappings_array[arg_min_dist])]
    print(f'The corresponding video timestamp is: {match}')
    if render:
      self._render(match)

    return match
  
  def _render(self, timestamp):
    """
    Renders the video of the desired timestamp.

    args:
      - timestamp: string *** A string desired timestamp in the format of mm:ss or mmm:ss
    
    returns: None
    """
    root = tk.Tk()
    root.geometry('1280x720')
    videoplayer = TkinterVideo(master=root, scaled=True, keep_aspect=True)
    videoplayer.load(self.video_path)
    videoplayer.seek(int(self._str_to_ms(timestamp)[0] / 1000) - 3)
    # videoplayer.seek(10)
    videoplayer.pack(expand=True, fill="both")
    videoplayer.play()
    root.mainloop()
    
  
  def _ms_to_str(self, ms):
    """
    Turns time in milliseconds to a string format of hh:mm:ss

    args:
      - ms: int *** time in milliseconds

    returns:
      - formatted_time: string *** time string in the format of mm:ss
    """
    seconds = ms // 1000
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
     
    formatted_time = "%02d:%02d:%02d" % (hour, minutes, seconds)
    
    return formatted_time

  def _str_to_ms(self, time_str):
    """
    Turns a string format of a timestamp to milliseconds

    args: 
      - time_str: string *** time string in the format of mm:ss(+)

    returns:
      - res: list *** a list in the format of [ms, added_time]
    """
    added_time = False
    if '+' in time_str:
      added_time = True
    time = time_str.replace('+', '')
    time = time.split(':')
    ms = 0
    for i, item in enumerate(reversed(time)):
      ms += (60 ** i) * 1000 * int(item)
    res = ms, added_time
    return res

  def _ms_to_time(self, ms):
    """
    Turns time in milliseconds to a string format of hh:mm:ss

    args:
      - ms: int *** time in milliseconds

    returns:
      - formatted_time: string *** time string in the format of mm:ss(+)
    """
    seconds = ms[0] // 1000
    seconds = seconds % (24 * 3600)
    minutes = seconds // 60
    seconds %= 60
     
    formatted_time = "%02d:%02d" % (minutes, seconds)
    formatted_time += '+' if ms[1] else ''
    
    return formatted_time