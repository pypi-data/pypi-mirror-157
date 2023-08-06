def max_backward_match(word_list, vocab, max_k=5):
    res = []
    end = len(word_list)

    while end > 0:
        break_flag = False
        for i in range(max_k):
            start = end - max_k + i
            start = start if start >= 0 else 0
            temp = "".join(word_list[start:end])
            if temp in vocab:
                res.append([temp, start, end])
                end = start
                break_flag = True
                break
        if not break_flag:
            end -= 1
    res.reverse()
    return res