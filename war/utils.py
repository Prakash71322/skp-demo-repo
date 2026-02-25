class Colors:
    RED = '\033[31m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'


def get_colored_message(_message_tuple: tuple):
  match _message_tuple[1].upper():
    case "RED":
      return (f"{Colors.RED}{_message_tuple[0]}{Colors.RESET}")
    case "GREEN":
      return(f"{Colors.GREEN}{_message_tuple[0]}{Colors.RESET}")
    case "YELLOW":
      return(f"{Colors.YELLOW}{_message_tuple[0]}{Colors.RESET}")
    case _:
      return _message_tuple[0] 
    

def string_format(_t_value: str, _replace_val = "and "):
  if len(_t_value) > 99:
    return _t_value.replace("::", f"\n{_replace_val}")
  #_indices = [index for index, char in enumerate(string_to_search) if char == char_to_find]
  return _t_value.replace("::", f"{_replace_val}")


def print_table(data_dic):
  format_row = "{:<25} {:<100} "
  format_value = lambda _value: _value.replace("\n", "\n" + " "*26) if "\n" in _value else _value
  print(format_row.format('Well Architected Entity', 'Value'))
  print(format_row.format("-" * 24, "-" * 99))
  _jnt = "\n" + " "*26
  for _key, _value in data_dic.items():
    if type(_value) == dict :
      if _key == "Data":
        print()
        print(format_row.format(_key, _jnt.join(f"{_key_}\n" + " "*26 + f"is{format_value(string_format(_value_, " "))}" for _key_, _value_ in _value.items())))
    elif type(_value) == list :
      print()
      print(format_row.format(_key, "".join([f"{format_value(_val_)}" for _val_ in _value])))
    else:
      _t_v = string_format(_t_value = _value)
      print(format_row.format(_key, format_value(_t_v)))
  




def print_table(data_dic):
  format_row = "{:<25} {:<100} "
  print(format_row.format('Well Architected Entity', 'Value'))
  print(format_row.format("-" * 24, "-" * 99))
  _jnt = "\n" + " "*26
  for _key, _value in data_dic.items():
      print(format_row.format(_key, _value))


if __name__ == "__main__":
  data = {"Pillar": "Security", "Question": "How do you manage identities and permissions for people and machines?", "Best Practice": "Use strong sign-in mechanism", "Validation": "Secure password policy status", "Status": "Not enforced"}
  #print_table(data)
  #print(formatt_string())
  print(get_colored_message(("Hello", "red")))
  print(get_colored_message(("Hello", "green")))
  print(get_colored_message(("Hello", "yellow")))
