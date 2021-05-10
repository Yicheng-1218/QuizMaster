
from flask import Flask, session, redirect, render_template, jsonify, request
from flask.helpers import flash, make_response, send_file, send_from_directory
from flask.wrappers import Response
from forms import *
from format import *
import os
import datetime

app = Flask(__name__)

# csrf_token
app.config['SECRET_KEY'] = '408637147'

# web cache lifetime
# app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# session lifetime
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=7)


@app.before_request
def session_create():
    # 設定session存在時間延長，而不是關閉瀏覽器就刪除
    session.permanent = True

    # 如果session不存在則建立
    if session.get('quiz_map') == None:
        print('create quiz_map')
        session['quiz_map'] = quiz_map
    if session.get('preview_map') == None:
        print('create preview_map')
        session['preview_map'] = perview_map


@app.route('/')
def index():
    return render_template('index.html', index_active=act_map['i_act'])


@app.route('/builder')
def fun_page():

    # 印出session內題目表
    print(session['quiz_map'])
    return render_template('moodle/builder.html', builder_active=act_map['b_act'])


@app.route('/builder/<method>', methods=['GET', 'POST'])
def method_page(method):
    TF_form = CreateTF()
    MC_form = CreateMC()
    SA_form = CreateSA()

    # 印出session內題目表
    print(session['quiz_map'])

    # 取得session內題庫並存入區域變數
    dataset = session.get('quiz_map')
    pm = session.get('preview_map')

    # 如果TF表單成功送出
    if TF_form.validate_on_submit():

        # 印出格式化表單內容
        print('[成功建立題目]:', TF_format(TF_form))

        # 使用區域變數修正再存入
        dataset['TF']['count'] += 1
        dataset['TF']['list'].append(TF_format(TF_form))
        session['quiz_map'] = dataset
        #
        preview_TF(TF_form, pm)
        session['preview_map'] = pm

        # 引導回TF頁
        return redirect('True_or_False')

    # 如果MC表單成功送出
    if MC_form.validate_on_submit():

        # 印出格式化表單內容
        print('[成功建立題目]:', MC_format(MC_form))

        # 使用區域變數修正再存入
        dataset['MC']['count'] += 1
        dataset['MC']['list'].append(MC_format(MC_form))
        session['quiz_map'] = dataset
        #
        preview_MC(MC_form, pm)
        session['preview_map'] = pm

        # 引導回MC頁
        return redirect('Multiple_choice')

    # 如果SA表單成功送出
    if SA_form.validate_on_submit():

        # 印出格式化表單內容
        print('[成功建立題目]:', SA_format(SA_form))

        # 使用區域變數修正再存入
        dataset['SA']['count'] += 1
        dataset['SA']['list'].append(SA_format(SA_form))
        session['quiz_map'] = dataset
        #
        preview_SA(SA_form, pm)
        session['preview_map'] = pm

        # 引導回SA頁
        return redirect('short_ans')

    # 檢查get路由引導路徑
    if method == 'True_or_False':
        TF_count = session['quiz_map']['TF']['count']
        return render_template('moodle/True_or_False.html', builder_active=act_map['b_act'], TF_form=TF_form, TF_count=TF_count)
    elif method == 'Multiple_choice':
        MC_count = session['quiz_map']['MC']['count']
        return render_template('moodle/Multiple_choice.html', builder_active=act_map['b_act'], MC_form=MC_form, MC_count=MC_count)
    elif method == 'short_ans':
        SA_count = session['quiz_map']['SA']['count']
        return render_template('moodle/short_ans.html', builder_active=act_map['b_act'], SA_form=SA_form, SA_count=SA_count)
    else:
        return '404 PAGE NOT FOUND'


@app.route('/export', methods=['GET', 'POST'])
def export():
    del_form = delete_quiz()
    export_form = export_quiz()

    # 如果刪除表單成功送出
    if del_form.validate_on_submit():
        # 設定session試卷為空模板
        session.pop('quiz_map')
        session.pop('preview_map')
        return redirect('/')
    if export_form.validate_on_submit():
        def generate():
            # 取得session資料
            dataset = session.get('quiz_map')
            # 組合最後字串
            final_str = b''
            for type in dataset:
                for line in dataset[type]['list']:
                    final_str += line.encode('utf-8')+b'\n\n'
            return final_str

        # !超強大功能!!!!!!直接生成檔案回傳，不存在伺服端
        response = make_response(Response(generate(), mimetype='text/gift'))
        response.headers["Content-Disposition"] = "attachment; filename=quiz.gift;"
        return response

    return render_template('export.html', export_active=act_map['e_act'], del_form=del_form, export_form=export_form)


@app.route('/preview')
def preview():
    dataset = session.get('preview_map')
    return render_template('preview.html', preview_active=act_map['p_act'], dataset=dataset)


@app.route('/contact')
def contact():

    return render_template('contact.html', contact_active=act_map['c_act'])


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    # !正式入口
    app.run(host='0.0.0.0', port=port)
