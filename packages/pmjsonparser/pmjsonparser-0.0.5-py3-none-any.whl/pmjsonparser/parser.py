import json


def replace_values_with_keypath(key_path, dictionary, replaced_values_list, key_path_prefix):
  for dict_key in dictionary.keys():
    if type(dictionary[dict_key]) is dict:
      extended_key_path = extend_key_path(key_path, dict_key)
      replaced_values_list + replace_values_with_keypath(extended_key_path, dictionary[dict_key], replaced_values_list,
        key_path_prefix)
    elif type(dictionary[dict_key]) is list:
      for i in range(len(dictionary[dict_key])):
        if type(dictionary[dict_key][i]) is not dict:
          key_path_dictionary_value = create_key_path_value(key_path_prefix, key_path, dict_key + '[' + str(i) + ']')

          dictionary[dict_key][i] = '{{' + key_path_dictionary_value.replace('[', '').replace(']', '') + '}}'
          replaced_values_list.append(key_path_dictionary_value)
        else:
          extended_key_path = extend_key_path(key_path, dict_key + '[' + str(i) + ']')
          replaced_values_list + replace_values_with_keypath(extended_key_path, dictionary[dict_key][i],
            replaced_values_list, key_path_prefix)
    else:
      key_path_dictionary_value = create_key_path_value(key_path_prefix, key_path, dict_key)
      dictionary[dict_key] = '{{' + key_path_dictionary_value.replace('[', '').replace(']', '') + '}}'
      replaced_values_list.append(key_path_dictionary_value)
  return replaced_values_list


def extend_key_path(key_path, dict_key):
  return key_path + '.' + dict_key


def create_key_path_value(key_path_prefix, key_path, dict_key):
  return key_path_prefix + extend_key_path(key_path, dict_key)


def run(json_source_path, json_target_path, js_target_path, prefix):
  with open(json_source_path, 'r') as json_source_file, open(js_target_path, 'w') as js_target_file, open(
    json_target_path, 'w') as json_target_file:
    json_content = json.loads(json_source_file.read())
    pm_var_list = replace_values_with_keypath('', json_content, [], prefix)
    js_target_file.write("const response = pm.response.json();\n")
    for pm_var in pm_var_list:
      pm_env_name = pm_var.replace('[', '').replace(']', '')
      response_source = pm_var[len(prefix):]
      js_target_file.write(f"pm.environment.set('{pm_env_name}',response'{response_source}');\n")
    # Don't put json dump in the loop above
    json.dump(json_content, json_target_file)
