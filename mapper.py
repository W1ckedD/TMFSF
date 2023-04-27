import os
import json
import re
import cv2
from datetime import datetime
import numpy as np
from tqdm import tqdm
from ultralytics import YOLO
from easyocr import Reader

class Mapper:
  def __init__(self, weights_path, video_path, output_path):
    self.mapping_func = {}
    self.weights_path = weights_path
    self.video_path = video_path
    self.output_path = output_path
    self.regex_pattern = "[1]?\d{1,2}(\:|\;|\.|\|)[0-5][0-9]?"
    self.model = self._load_detector(self.weights_path)
    self.ocr = self._load_ocr()

  def _load_detector(self, weights_path):
    """
    Loads the yolo scoreboard detector model.

    args:
      - weights_path: string *** path to the trained YOLO model weights

    returns:
      - model: YOLO instance 
    """
    print('Loading YOLO model ...')

    model = YOLO(weights_path)
    return model
  
  def _load_ocr(self):
    """
    Loads the EasyOCR model.

    returns: 
      - ocr: EasyOCR instance
    """
    print('Loading OCR model ...')
    ocr = Reader(['en'])
    return ocr
  
  def _detect(self, img):
    """
    Detects the scoreboard from the full size images.
    Crops the scoreboard using the bounding boxes.
    Returns the cropped img

    args:
      - img: Numpy.ndarray *** A numpy array with the shape of (N, M, 3) representing the full size image.
    
    returns:
      - img: Numpy.ndarray *** A numpy array with the shape of (N, M, 3) representing the cropped scoreboard.
    """
    detector = self.model
    res = detector(img, verbose=False)[0]
    bboxes = res.boxes.xyxy.cpu().numpy()
    if bboxes.size != 0:
      x_tl, y_tl, x_br, y_br = bboxes[0]
      img = img[int(np.floor(y_tl)): int(np.ceil(y_br)), int(np.floor(x_tl)): int(np.ceil(x_br)), :]

    return img
    
  
  def _read_text(self, img):
    """
    Reads the text from the image.

    args:
      - img: Numpy.ndarray *** A numpy array with the shape of (N, M, 3) representing the cropped scoreboard.
    
    returns:
      - res: list *** A list of detected text in the format of [coordinates, text, confidence]
    """
    ocr = self.ocr
    res = ocr.readtext(img)
    return res

  def extract_time(self, reader_res):
    """
    Extracts the timestamps from the text read by the OCR.

      - Goes through every element of the ocr results. 
      - Applies a simple regex pattern.
      - Extracts the timestamps
      - If the character + is found in the timestamps, it indicates that it was recorded in the added times.

    args:
      - reader_res: _read_text *** The result of the _read_text method.

    returns:
      - time_dict: dict *** A dictionary with the format of {timestamps, added_time}
    """
    timestamps = []
    added_time = False
    for item in reader_res:
      if re.match('\+', item[1]):
        added_time = True
    for item in reader_res:
      search = re.search(self.regex_pattern, item[1])
      if search:
        txt = search.string
        timestamp = re.sub("(\:|\.|\;|\|)", ":", txt)
        timestamps.append(timestamp)

    time_dict = {'timestamps': timestamps, 'added_time': added_time}
    return time_dict

  def _format_timestamp(self, timestamps, added_time):
    """
    Formats the timestamps extracted in the extract_time method.
    If the timestamp was recorded during added time, a + character will be added to the end of the formatted timestamp.
    
    args:
      - timestamps: list *** list of timestamps
      - added_time: bool *** a boolean indicating whether the timestamp was recorded during added time.

    returns:
      - timestamp: string *** a string representing the formatted timestamp.
    """
    if added_time and timestamps[0] in ['45', '90', '45:00', '90:00']:
      [minute, second] = timestamps[0].split(':')
      [minute_added, second_added] = timestamps[1].split(':')
      return f'{int(minute) + int(minute_added)}:{int(second) + int(second_added)}+'
    else:
      return timestamps[0]


  def map(self, step_size=1):
    """
    Goes through every {step_size} frame of the given video.
    Detects the scoreboard
    Reads the text
    Extracts the timestamps
    Formats the timestamps
    Generates the mapping dictionary
    Exports the mapping dictionary to a json file

    args:
      - step_size: int *** a multiplier of the distance between two consecutive frames in seconds.
    
    returns:
      - saved_path: string *** Path to the saved mappings json file
    """

    print('Detecting scoreboards ...')
    
    # count = 0
    cap = cv2.VideoCapture(self.video_path)
    success = True
    duration = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS))
    print(duration)
    for count in tqdm(range(duration // step_size)):
      frame_time = count * step_size * 1000
      cap.set(cv2.CAP_PROP_POS_MSEC, frame_time)
      success, img = cap.read()

      img = self._detect(img)
      if img is None:
        continue

      if not success:
        print (f'success: {success}')
        break

      ocr_res = self._read_text(img)
      time = self.extract_time(ocr_res)
      video_time = self._ms_to_time(frame_time)
      if len(time['timestamps']) != 0:
        timestamps = sorted(time['timestamps'], reverse=True)
        key = self._format_timestamp(timestamps, time['added_time'])
        self.mapping_func[key] = video_time
        # f_name = key.replace(':', '-')
        # cv2.imwrite(f'frames/{f_name}.jpg', img)
      # count += 1
    # while success:
      
    cap.release()
    # file_name = self.video_path.split('/')[-1][:-4]
    saved_path = f'{self.output_path}'
    self._save_mappings(saved_path)
    
    return saved_path

    
  def _save_mappings(self, path):
    """
      Saves the mapping function to a json file
      
      args:
        - path: string *** path to where the mappings json file needs to be stored.
      returns: None
    """
    
    with open(path, 'w') as f:
      f.write(json.dumps(self.mapping_func))
  
  def _ms_to_time(self, ms):
    """
    Turns time in milliseconds to a string format of hh:mm:ss

    args:
      - ms: int *** time in milliseconds

    returns:
      - formatted_time: string *** time string in the format of mm:ss
    """
    seconds = ms // 1000
    seconds = seconds % (24 * 3600)
    minutes = seconds // 60
    seconds %= 60
     
    formatted_time = "%02d:%02d" % (minutes, seconds)
    
    return formatted_time

  def test_single_img(self, img):
    """
    Tests the functionality of the pipeline for a single frame.

    args:
      - img: Numpy.ndarray *** A numpy array with the shape of (N, M, 3) representing the full size image.
    
    returns: None
    """
    img = self._detect(img)
    res = self._read_text(img)
    timestamps = self.extract_time(res)
    print(timestamps)

    while True:
      cv2.imshow('test', img)

      if cv2.waitKey(0) & 0xff == ord('q'):
        cv2.destroyAllWindows()
        break
  