# TMFSF:Timestamp Mapping For Soccer Footage

Large-scale sports analysis is a field that has attracted considerable attention in recent years. Machine learning and deep learning approaches, particularly in combination with computer vision,
have shown tremendous improvement in achieving state-of-theart results in this field and therefore, gained incredible popularity [15]. However, the utilization of these methods requires highquality structured data. Although nowadays many high-quality
sports datasets exist, they mainly consist of highly-processed and
abstracted data and could greatly benefit from processed video
data. In this project, we will take advantage of existing high-quality
sports datasets to design and implement a preprocessing software
that can process raw videos of football matches to be suitable for
usage in numerous applications in the field of large-scale sports
analysis. More specifically, we introduce TMFSF, a software that
utilizes computer vision and machine learning techniques to map
timestamps in a football match time frame, to the corresponding
timestamps in the time frame of video footage of said football match.


### Installation
```sh
pip install --no-deps -r requirements.txt
```
**Note**: Currently there is an inconsistency for the required version of one of the shared dependencies of two of the core packages. To avoid installation errors, make sure to use ```--no-deps``` flag in the above command.

**Note**: For a convinent installation process, we included the CPU version of the PyTorch library in the requirements.txt file. Please feel free to install the GPU version of the PyTorch library manually and based on the cuda version installed on your system to have faster calculations.

### Demo

#### Demo file parameters

<table>
      <thead>
        <tr>
              <td><b>Parameter</b></td>
              <td><b>Type</b></td>
              <td><b>Description</b></td>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>weights_path</td>
          <td>String</td>
          <td>Path to the weights for the YOLOv8 model</td>
        </tr>
        <tr>
          <td>video_path</td>
          <td>String</td>
          <td>Path to the related video of the football match</td>
        </tr>
        <tr>
          <td>output_path</td>
          <td>String</td>
          <td>Path to file where the mapping function is going to be stored</td>
        </tr>
        <tr>
          <td>mappings_path</td>
          <td>String</td>
          <td>Path to the previously stored mapping file</td>
        </tr>
        <tr>
          <td>timestamp (required)</td>
          <td>String</td>
          <td>The desired timestamp in the format of (m)mm:ss(+)</td>
        </tr>
        <tr>
          <td>map</td>
          <td>Boolean</td>
          <td>
            If "True", the mapping and matching process will run. If "False"
            only the matching process will run (Note the capital "T" and "F" for
            True and False)
          </td>
        </tr>
        <tr>
          <td>render</td>
          <td>Boolean</td>
          <td>
            If "True", a video player will display the frame for the matching
            timstamp (Note the capital "T" and "F" for True and False)
          </td>
        </tr>
        <tr>
          <td>error_margin</td>
          <td>Integer</td>
          <td>
            The value (in seconds) for the difference threshold between the
            desired time stamp and the closest matching timestamp
          </td>
        </tr>
        <tr>
          <td>step_size</td>
          <td>Integer</td>
          <td>
            The value (in seconds) for the distance between to consecutive
            frames of the video
          </td>
        </tr>
      </tbody>
    </table>

#### Demo Example
```sh
python demo.py --timestamp 91:03+ --step_size 1 --error_margin 10 -- map True --render True --weights_path model/weights/best.pt --video_path samples/videos/chelsea_vs_arsenal.mp4 --output_path samples/mappings/chelsea_vs_arsenal.json --mappings_path samples/mappings/chelsea_vs_arsenal.json
```

**Note**: Due to large size of videos, we could not upload a sample video to the repository. Therefore you need to replace the value for ```--video_path``` in the example to a custom video path in your machine.

### Modules

#### Mapper:
The Mapper module reads the frames from a video, for each frame it detects the scoreboards, reads the text from the scoreboards, and extracts the timestamp from the text snippets. Finally it generates a JSON file contating a key-value object where the keys are football match timestamps and the values are the corresponding video frame timestamps.


**Methods**:

| Name  | Description | Arguments | Returns |
| ------------- |:-------------:|:-------------:|:-------------:|
| \_\_init__      |   Constructor method   | weights_path: **str** - Path to the weights for the YOLOv8 model <br /> video_path: **str** - Path to the related video of the football match <br /> output_path: **str** - Path to file where the mapping function is going to be stored <br />| None
| map      | runs the mapping process     |step_size: **int** - a multiplier of the distance between two consecutive frames in seconds |saved_path: **str** - Path to the saved mappings json file
| extract_time | Extracts the timestamps from the text read by the OCR     | reader_res: **list** - A list containing the result of the OCR readtext method. | time_dict: **dict** - A dictionary with the format of {timestamps, added_time}

  
#### Matcher
            
**Methods**:

| Name  | Description | Arguments | Returns |
| ------------- |:-------------:|:-------------:|:-------------:|
| \_\_init__      |   Constructor method   | mappings_path: **str** - Path to the previously stored mapping file <br/> video_path: **str** - Path to the related video of the football match| None
| match      | runs the matching process     |timestamp: **str**: A string desired timestamp in the format of (m)mm:ss(+) <br />  error_margin: **int** - A multiplicator of the error margin allowd for matching the desired timestamps in seconds <br /> render: **bool** - If True, the video of the timestampe will be rendered (Note the uppercase True and False). |match: **str** - the exact or the closest corrolated video frame in the format of hh:mm:ss


### Example
```py
from mapper import Mapper
from matcher import Matcher

mapper = Mapper(
        weights_path="model/weights/best.pt",
        video_path="samples/videos/chelsea_vs_arsenal.mp4",
        output_path="samples/mappings/chelsea_vs_arsenal.json"
    )

mappings_path = mapper.map(step_size=1)

matcher = Matcher(
        mappings_path=mappings_path or "samples/mappings/chelsea_vs_arsenal.json",
        video_path="samples/videos/chelsea_vs_arsenal.mp4",
    )
    
result = matcher.match(
    timestamp="91:03+",
    error_margin=10,
    render=True
)
  
print(result)
```
**Note**: Again, due to large size of videos, we could not upload a sample video to the repository. Therefore you need to replace the value for ```video_path``` in the example to a custom video path in your machine.
