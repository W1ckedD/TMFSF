from argparse import ArgumentParser

from mapper import Mapper
from matcher import Matcher

def find_mappings(**kwargs):
  
  mappings_path = ''
  if eval(kwargs['map']):
    mapper = Mapper(
      weights_path=kwargs['weights_path'],
      video_path=kwargs['video_path'],
      output_path=kwargs['output_path']
    )
    mappings_path = mapper.map(step_size=int(kwargs['step_size']))

  matcher = Matcher(
    mappings_path=mappings_path if eval(kwargs['map']) else kwargs['output_path'] if not kwargs['mappings_path'] else kwargs['mappings_path'],
    video_path=kwargs['video_path'],
  )

  res = matcher.match(
    timestamp=kwargs['timestamp'],
    error_margin=int(kwargs['error_margin']),
    render=eval(kwargs['render'])
  )
  


  # img = cv2.imread('samples/imgs/53.jpg')
  # mapper.test_single_img(img)

if __name__ == '__main__':
  parser = ArgumentParser()
  parser.add_argument('--weights_path', default='model/weights/best.pt')
  parser.add_argument('--video_path', default='samples/videos/chelsea_vs_arsenal.mp4')
  parser.add_argument('--output_path', default='samples/mappings/chelsea_vs_arsenal.json')
  parser.add_argument('--mappings_path', default='samples/mappings/chelsea_vs_arsenal-mapping.json')
  parser.add_argument('--timestamp', required=True)
  parser.add_argument('--map', default="True")
  parser.add_argument('--render', default="True")
  parser.add_argument('--error_margin', default=2)
  parser.add_argument('--step_size', default=1)
  args = parser.parse_args()
  
  find_mappings(
    weights_path=args.weights_path,
    video_path=args.video_path,
    output_path=args.output_path,
    mappings_path=args.mappings_path,
    timestamp=args.timestamp,
    error_margin=args.error_margin,
    render=args.render,
    map=args.map,
    step_size=args.step_size
  )