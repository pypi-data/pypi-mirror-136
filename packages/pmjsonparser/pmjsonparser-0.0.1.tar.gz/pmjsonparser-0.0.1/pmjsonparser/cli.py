import argparse
import os
import pmjsonparser.parser

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Process JSON to generate postgres snippets')
  parser.add_argument('json_source', type=str, help='path of the json file to be parsed')
  parser.add_argument('json_target', type=str, help='target path resulting postman file')
  parser.add_argument('pm_js_target', type=str, help='target path resulting file')
  parser.add_argument('prefix', type=str, help='service prefix')

  args = parser.parse_args()
  json_source_path = args.json_source
  json_target_path = args.json_target
  js_target_path = args.pm_js_target

  prefix = args.prefix
  if not os.path.exists(json_source_path):
    print('could not find json path at' + json_source_path)
    exit(1)
  pmjsonparser.parser.run(json_source_path, json_target_path, js_target_path, prefix)
