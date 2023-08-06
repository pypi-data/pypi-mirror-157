#1.识别指标
#如PE
#分完美匹配，其次别名，其次考虑错别字或者字向量相近

#2.指标对应类型：数字型、枚举
#数字型：走范围逻辑、相等逻辑（模糊？）、排序逻辑，默认单向范围
#枚举型：走枚举逻辑，考虑相近说法

#3.判断and or not 及先后结合顺序，默认and
#找到指标后 连接后面所有对应直到找到下一个指标
#问题：对应可能在前面 如：大于10倍市盈

#4.异常处理
#如果没找到指标：考虑用实体识别方式
#如果找到指标后面无对应或对应奇怪

#TODO:
#数字后处理，如%，万，倍等，是否应该推理单位？单位合理性
#等于的处理？默认等于上下的范围？
#"或"的情况？
#判断冲突？
#汉字数字情况
#指标分配范围时 多个范围冲突如>30又>20，同一级别应只保留一个最可能的
#分段后处理，会损失一部分情况？有没有更好办法
#找同义词存入词表 OR定位实体对应相应词（需要训练NER模型）
#复杂情况：如20倍市盈率以下
#指标+范围分数计算优化，如指标限定范围或者指标范围可能性分数
#TOPn情况更多情况


#topn情况：
#前[num]
#最大/小的[num]个 出现最大/最小可无num 默认为1
#topn 分词时会分成一个



import os
import re
from jieba import Tokenizer
from jieba.posseg import POSTokenizer
import stockpick.utils as utils
import stockpick.corpus_process as corpus_process

_pseg_dict = {}
_get_module_path = lambda path: os.path.normpath(os.path.join(os.getcwd(),
                                                 os.path.dirname(__file__), path))
class Extractor():
    def init(self, **kwargs):
        """
          Args:
              ``` dt ```                : class Tokenizer from jieba
              ``` user_dict_path ```    : user cut dict path
        """
        _cut = Tokenizer()
        _cut.load_userdict(_get_module_path("gupiao_dict.txt"))

        _pseg_dict["gupiao"] = POSTokenizer(_cut)


    def __init__(self):
        self.init()
        self.index_alias, self.enum_value, self.direct_enum_value, self.scope_word_alias, self.scope_word_order, self.index_unit, self.unit_transform = corpus_process.get_corpus()

    def _extract_keyword(self, query):
        # concat_words = {"且": "&&", "并且": "&&", "&&": "&&", "&": "&&", "而且": "&&", "或": "||", "|": "||", "||": "||", "或者": "||", "or": "||", "and": "&&"}
        between_pattern = "[在|处于|是|为|从]?([\d]+\.?[\d]*[倍|亿|%|万|万亿]?)[-|~|～|到|至]([\d]+\.?[\d]*[倍|亿|%|万|万亿]?)[之间|间]?"
        all_words = set(self.index_alias.keys()).union(set(self.scope_word_alias.keys())).union(
            set(self.direct_enum_value.keys()))

        query = query.strip()
        _pseg = _pseg_dict['gupiao']
        words = [w for w in _pseg.cut(query) if w.word.strip()]
        # 助词去掉
        words = list(filter(lambda x: not x.flag.startswith("u"), words))
        _type = None
        word_list = [w.word for w in words]
        tag_list = [w.flag for w in words]
        index_hits = utils.max_backward_match(word_list, all_words)
        index_hits_type = []
        for i, index_hit in enumerate(index_hits):
            type = ""
            allowed_order = []
            hit_name = index_hit[0]
            if hit_name in self.index_alias:
                type = "指标"
                hit_name = self.index_alias[hit_name]
            elif hit_name in self.scope_word_alias:
                type = "范围类型"
                allowed_order = self.scope_word_order[hit_name]
                hit_name = self.scope_word_alias[hit_name]
            elif hit_name in self.direct_enum_value:
                type = "枚举指标"
                hit_name = self.direct_enum_value[hit_name]
            index_hits_type.append([hit_name, index_hit[1], index_hit[2], allowed_order, type])
        index_hits_final = []
        for i, iht in enumerate(index_hits_type):
            if iht[-1] == "枚举指标":
                index_hits_final.append(iht)
            if iht[-1] == "指标":
                if iht[0] in self.enum_value:
                    enum_result = self.enum_value[iht[0]]
                    end_index = len(word_list) if i + 1 >= len(index_hits_type) else index_hits_type[i + 1][1]
                    # 允许一个匹配
                    for j in range(iht[2], end_index):
                        if word_list[j] in enum_result:
                            index_hits_final.append(
                                [iht[0] + word_list[j], iht[1], iht[2], j, "枚举指标"])
                            break
                else:
                    index_hits_final.append(iht)

            elif iht[-1] == "范围类型":
                allowed_order = iht[3]
                for order in allowed_order:
                    if order == "after":
                        end_index = len(word_list) if i + 1 >= len(index_hits_type) else index_hits_type[i + 1][1]
                        value_list = []
                        for j in range(iht[2], end_index):
                            if tag_list[j] == "m" or word_list[j].isdigit():
                                value_list.append(word_list[j])
                            else:
                                break
                        if len(value_list) != 0:
                            index_hits_final.append(
                                [[iht[0], "".join(value_list)], iht[1], iht[2] + len(value_list), "数字范围"])
                            break
                    elif order == "before":
                        start_index = 0 if i == 0 else index_hits_type[i - 1][2]
                        value_list = []
                        for j in range(iht[1] - 1, start_index - 1, -1):
                            if tag_list[j] == "m" or word_list[j].isdigit():
                                value_list.append(word_list[j])
                            else:
                                break
                            value_list.reverse()
                        if len(value_list) != 0:
                            index_hits_final.append(
                                [[iht[0], "".join(value_list)], iht[1], iht[2] + len(value_list), "数字范围"])
                            break
                    elif order == "null":
                        index_hits_final.append([[iht[0]], iht[1], iht[2], "数字范围"])
                        break
        index_hits = []
        if len(index_hits_final) > 0:
            left_start = 0
            left_end = index_hits_final[0][1]
            between_res = re.match(between_pattern, "".join(word_list[left_start:left_end]))
            if between_res:
                index_hits.append([["~", between_res.group(1), between_res.group(2)], left_start, left_end, "数字范围"])

        for i, index in enumerate(index_hits_final):
            index_hits.append(index)
            right_start = index[2]
            right_end = len(word_list) if (i == len(index_hits_final) - 1 or len(index_hits_final) == 1) else \
                index_hits_final[i + 1][1]
            between_res = re.match(between_pattern, "".join(word_list[right_start:right_end]))
            if between_res:
                index_hits.append([["~", between_res.group(1), between_res.group(2)], right_start, right_end, "数字范围"])
        return index_hits, len(word_list)

    # 一个指标对应范围去掉冲突和无用的
    def _func(self, di, value_list):
        x = sorted(di.items(), key=lambda d: d[1], reverse=True)
        new_di = dict()
        allowed = []
        if len(x) >= 1:
            new_di[x[0][0]] = x[0][1]
            value = value_list[x[0][0]][0][0]
            if value in (">", ">="):
                allowed = ["<", "<="]
            elif value in ("<", "<="):
                allowed = [">", ">="]
        if len(x) >= 2:
            value = value_list[x[1][0]][0][0]
            valid = False
            for elem in allowed:
                valid = valid | (value == elem)
            if valid:
                new_di[x[1][0]] = x[1][1]
        return new_di

    # 单位转换，提取数字
    def _transform_number(self, index, num_str):
        regex = "([\d]+\.?[\d]*)(.*)"
        res = re.match(regex, num_str)
        number = res.group(1)
        unit = res.group(2)
        default_unit = self.index_unit[index]["default_unit"]
        if default_unit in self.unit_transform:
            times = self.unit_transform[default_unit].get(unit, 1)
        else:
            times = self.unit_transform["null"].get(unit, 1)
        return float(number) * times

    def _extract_num_combine(self, li, index):
        symbol = li[0]
        new_li = [symbol]
        for elem in li[1:]:
            new_li.append(self._transform_number(index, elem))
        return new_li

    # 优先级：
    # 范围在指标后优先
    # 距离越近越加分 +1/(距离+1)
    def _combine(self, index_hits, l):
        result = []
        index2value = dict()
        value2index = dict()
        index_list = []
        value_list = []
        for ih in index_hits:
            if ih[-1] == "枚举指标":
                result.append(ih[0])
                index_list.append(ih)
            elif ih[-1] == "指标":
                index_list.append(ih)
            elif ih[-1] == "数字范围":
                value_list.append(ih)
            else:
                print("error!")
                return []
        for i, index in enumerate(index_list):
            left_start = 0 if (i == 0 or len(index_list) == 1) else index_list[i - 1][2]
            left_end = index[1]
            right_start = index[2]
            right_end = l if (i == len(index_list) - 1 or len(index_list) == 1) else index_list[i + 1][1]
            if index[-1] == "指标":
                index2value[i] = {}
                for ii, value in enumerate(value_list):
                    if value[1] >= right_start and value[2] <= right_end:
                        # 后面优先，距离越近分数越高
                        index2value[i][ii] = 0.3 + 1 / (value[1] - right_start + 1)
                for ii in range(len(value_list) - 1, -1, -1):
                    value = value_list[ii]
                    if value[1] >= left_start and value[2] <= left_end:
                        index2value[i][ii] = 1 / (left_end - value[2] + 1)
                index2value[i] = self._func(index2value[i], value_list)
        for index, value_score in index2value.items():
            for value, score in value_score.items():
                if value not in value2index:
                    value2index[value] = dict()
                if score >= 0.5:
                    value2index[value][index] = score
        save1_value_index = dict()
        index_value = dict()
        for value, index_score in value2index.items():
            if len(index_score) > 0:
                save1_value_index[value] = sorted(index_score.items(), key=lambda d: d[1], reverse=True)[0][0]
                index = save1_value_index[value]
                if index not in index_value:
                    index_value[index] = []
                index_value[index].append(value)

        res = []
        for index, value in index_value.items():
            elem = [index_list[index][0]]
            for v in value:
                elem.append(self._extract_num_combine(value_list[v][0], index_list[index][0]))
            res.append(elem)

        for elem in result:
            res.append(elem)
        return res


    def process_sentence(self, sentence):
        parts = re.split("[,，!！?？、]", sentence.lower())
        res = []
        for part in parts:
            index_hits, l = self._extract_keyword(part)
            res.extend(self._combine(index_hits, l))
        return res





















# ex = Extractor()
# sentences = corpus_process.get_sentence()
# for sentence in sentences:
#     print(sentence)
#     res = ex.process_sentence(sentence)
#     #print(res)
#     print("\n\n\n")



























