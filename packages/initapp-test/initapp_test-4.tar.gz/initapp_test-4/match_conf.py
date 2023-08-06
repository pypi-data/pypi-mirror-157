import yaml
import os

BASE_DIR = os.path.dirname(__file__)
match_conf_path = os.path.join(BASE_DIR, 'tmp_img', 'match_config.yaml')
conf_path = os.path.join(BASE_DIR, 'conf', 'config.yaml')


def get_yaml(file_path):
    with open(file_path, encoding='utf-8') as f:
        try:
            y_instance = yaml.load(f, Loader=yaml.SafeLoader)
            return y_instance
        except yaml.YAMLError as e:
            print(e)


def get_config_value(*args) -> str:
    """
    在yaml中根据key获取对应的value
    :param args: 对应的key值
    :return:
    """
    obj = get_yaml(conf_path)
    for arg in args:
        obj = obj.get(arg) if arg else None
    return obj


pkg_name = get_config_value('pkg_name')


def get_match_config_value(*args) -> str:
    """
    在yaml中根据key获取对应的value
    :param args: 对应的key值
    :return:
    """
    obj = get_yaml(match_conf_path)
    for arg in args:
        obj = obj.get(arg) if arg else None
    return obj


def get_feed_tab_text(pkg_name):
    tab = get_match_config_value('feed_tab', pkg_name)
    if tab:
        return tab.split(",")
    return None

def get_ad_text(pkg_name):
    tab = get_match_config_value('ad_text', pkg_name)
    if tab:
        return tab.split(",")
    return None

def update_config_value(*args, value=None):
    """
    更新yaml中key对应的value
    :param args: 对应的key值
    :param value:
    """
    obj = get_yaml(conf_path)
    tmp = obj
    for arg in args[:-1]:
        tmp = tmp[arg]
    tmp[args[-1]] = value
    # print('update config: key:{}, value:{}'.format(str(args), value))
    with open(conf_path, encoding='utf-8', mode='w') as fw:
        yaml.dump(obj, fw, sort_keys=False)
