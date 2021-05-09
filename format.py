# 記錄哪一個頁面活動中
act_map = {
    'i_act': 'active',
    'b_act': 'active',
    'e_act': 'active',
    'p_act': 'active',
    'c_act': 'active',
}

# 記錄整份考卷的map模板
# !先使用session儲存模板再用區域變數修改
quiz_map = {
    'TF': {
        'count': 0,
        'list': []
    },
    'MC': {
        'count': 0,
        'list': []
    },
    'SA': {
        'count': 0,
        'list': []
    },
}

perview_map = {
    'TF': {
        'count': 0,
        'list': []
    },
    'MC': {
        'count': 0,
        'list': []
    },
    'SA': {
        'count': 0,
        'list': []
    },
}


def preview_TF(formdata, local_map):
    local_map['TF']['count'] += 1
    local_map['TF']['list'].append(
        [formdata.content.data, formdata.True_or_False.data])


def preview_MC(formdata, local_map):
    local_map['MC']['count'] += 1
    local_map['MC']['list'].append([formdata.content.data, formdata.A.data, formdata.B.data,
                                    formdata.C.data, formdata.D.data, formdata.Which_True.data])


def preview_SA(formdata, local_map):
    local_map['SA']['count'] += 1
    local_map['SA']['list'].append(
        [formdata.content.data, formdata.answer_box.data.replace(' ', ',')])


def TF_format(formdata):
    # 處理是非題格式
    result = formdata.content.data+'{'+formdata.True_or_False.data+'}'
    return result


def MC_format(formdata):
    # 處理選擇題格式
    data = {
        'content': formdata.content.data,
        'A': {
            'label': formdata.A.data,
            'ans': '~' if formdata.Which_True.data != 'A' else '='
        },
        'B': {
            'label': formdata.B.data,
            'ans': '~' if formdata.Which_True.data != 'B' else '='
        },
        'C': {
            'label': formdata.C.data,
            'ans': '~' if formdata.Which_True.data != 'C' else '='
        },
        'D': {
            'label': formdata.D.data,
            'ans': '~' if formdata.Which_True.data != 'D' else '='
        },
    }
    result = data['content'] +\
        '{'+data['A']['ans']+data['A']['label']+' ' +\
        data['B']['ans']+data['B']['label']+' ' + \
        data['C']['ans']+data['C']['label']+' ' +\
        data['D']['ans']+data['D']['label']+' '+'}'
    return result


def SA_format(formdata):
    # 處理簡答題格式
    answer = formdata.answer_box.data.split()
    result = formdata.content.data+'{'
    temp = ''
    for char in answer:
        temp += f'={char} '
    result += temp+'}'
    return result
