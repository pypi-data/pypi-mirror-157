import re
import os

_get_module_path = lambda path: os.path.normpath(os.path.join(os.getcwd(),
                                                 os.path.dirname(__file__), path))

def _read_sentences(filename):
    lines = []
    with open(filename, "r") as f:
        for line in f:
            if line.startswith("#"):
                continue
            lines.append(line.strip().lower())
    return lines


def _read_table(filename):
    res = []
    with open(filename, "r") as f:
        for line in f:
            if line.startswith("#"):
                continue
            line = re.split("\\s+", line.strip().lower())
            res.append(line)
    di = dict()
    if len(res) > 0:
        for i, line in enumerate(res):
            if i == 0:
                for name in res[0]:
                    di[name] = []
            else:
                for j, name in enumerate(res[0]):
                    if j >= len(line):
                        break
                    di[name].append(line[j])
    return di


def _process_table(index_table, scope_table, enum_table, unit_table):
    index_alias = dict()
    index_unit = dict()
    scope_word_alias = dict()
    scope_word_order = dict()
    for name, alias, default_unit, possible_unit in zip(index_table["name"], index_table["alias"], index_table["default_unit"], index_table["possible_unit"]):
        name = name.strip()
        alias = re.split("[,，]", alias)
        alias.append(name)
        alias = [elem.strip() for elem in alias]
        for elem in alias:
            index_alias[elem] = name
        default_unit = default_unit.strip()
        possible_unit = re.split("[,，]", possible_unit)
        possible_unit = [elem.strip() for elem in possible_unit]
        possible_unit.append(default_unit)
        possible_unit = list(set(possible_unit))
        index_unit[name] = {"default_unit": default_unit, "possible_unit": possible_unit}


    for word, norm_name, allowed_order in zip(scope_table["word"], scope_table["norm_name"], scope_table["allowed_order"]):
        word = word.strip()
        norm_name = norm_name.strip()
        allowed_order = re.split("[,，]", allowed_order)
        allowed_order = [elem.strip() for elem in allowed_order]
        scope_word_alias[word] = norm_name
        scope_word_order[word] = allowed_order

    #指标对应枚举
    enum_value = dict()
    direct_enum_value = dict()
    for alias, name, result in zip(enum_table["alias"], enum_table["name"], enum_table["result"]):
        name = name.strip()
        result = result.strip()
        alias = re.split("[,，]", alias)
        if name not in enum_value:
            enum_value[name] = set()
        enum_value[name].add(result)
        for d_name in alias:
            direct_enum_value[d_name.strip()] = name + result
        direct_enum_value[name + result] = name + result

    #单位转换
    unit_transform = dict()
    for base_unit, unit, times in zip(unit_table["base_unit"], unit_table["unit"], unit_table["times"]):
        base_unit, unit, times = base_unit.strip(), unit.strip(), float(times.strip())
        if base_unit not in unit_transform:
            unit_transform[base_unit] = dict()
        unit_transform[base_unit][unit] = times

    return index_alias, enum_value, direct_enum_value, scope_word_alias, scope_word_order, index_unit, unit_transform



def get_corpus():
    index_table = _read_table(_get_module_path("index_table"))
    scope_table = _read_table(_get_module_path("scope_table"))
    enum_table = _read_table(_get_module_path("enum_table"))
    unit_table = _read_table(_get_module_path("unit_table"))
    return _process_table(index_table, scope_table, enum_table, unit_table)


def get_sentence():
    return _read_sentences("stockpick/sentences.txt")

# index_alias, enum_value, direct_enum_value = get_corpus()
# print(index_alias)
# print(enum_value)
# print(direct_enum_value)