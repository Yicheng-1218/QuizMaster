
from flask import Flask, session, redirect, render_template, jsonify, request
from flask.helpers import flash, make_response, send_file, send_from_directory, url_for
from flask.wrappers import Response
from flask_wtf import csrf
from wtforms.validators import UUID
from forms import *
from format import *
import os
import datetime
import uuid

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


def form_init():
    prefix_p = str(uuid.uuid3(uuid.NAMESPACE_DNS, 'export'))
    prefix_d = str(uuid.uuid3(uuid.NAMESPACE_DNS, 'del'))
    f = {
        'del': delete_quiz(prefix=prefix_d),
        'exp': export_quiz(prefix=prefix_p),
        'qm': session.get('quiz_map'),
        'pm': session.get('preview_map'),
    }
    return f


@app.route('/builder/True_or_False/<int:count>', methods=['GET', 'POST'])
def TF_page(count):
    f = form_init()
    TF_count = session['quiz_map']['TF']['count']
    dataset = f['qm']

    class DynamicForm(FlaskForm):
        submit = SubmitField('增加試題')

    if count > 10:
        count = 10
    elif count < 1:
        count = 1
    for i in range(0, count):
        setattr(DynamicForm, 'form-' + str(i), FormField(CreateTF))
    form = DynamicForm()
    # 如果TF表單成功送出
    if form.validate_on_submit():
        for field in form:
            if field != form['submit'] and field != form['csrf_token']:
                # 印出格式化表單內容
                print('[成功建立題目]:', TF_format(field))

                # 使用區域變數修正再存入
                dataset['TF']['count'] += 1
                dataset['TF']['list'].append(TF_format(field))
                session['quiz_map'] = dataset
                #
                preview_TF(field, f['pm'])
                session['preview_map'] = f['pm']

        # 引導回TF頁
        return redirect(count)

    if f['del'].validate_on_submit():
        return del_quiz()

    if f['exp'].validate_on_submit():
        return export()

    return render_template('moodle/True_or_False.html', builder_active=act_map['b_act'], TF_form=form, TF_count=TF_count, del_form=f['del'], export_form=f['exp'], pm=f['pm'])


@app.route('/builder/Multiple_choice/<int:count>', methods=['GET', 'POST'])
def MC_page(count):
    f = form_init()
    MC_count = session['quiz_map']['MC']['count']
    dataset = f['qm']

    class DynamicForm(FlaskForm):
        submit = SubmitField('增加試題')

    if count > 10:
        count = 10
    elif count < 1:
        count = 1
    for i in range(0, count):
        setattr(DynamicForm, 'form-' + str(i), FormField(CreateMC))
    MC_form = DynamicForm()

    # 如果MC表單成功送出
    if MC_form.validate_on_submit():
        for field in MC_form:
            if field != MC_form['submit'] and field != MC_form['csrf_token']:
                # 印出格式化表單內容
                print('[成功建立題目]:', MC_format(field))

                # 使用區域變數修正再存入
                dataset['MC']['count'] += 1
                dataset['MC']['list'].append(MC_format(field))
                session['quiz_map'] = dataset
                #
                preview_MC(field, f['pm'])
                session['preview_map'] = f['pm']

        # 引導回MC頁
        return redirect(count)

    if f['del'].validate_on_submit():
        return del_quiz()

    if f['exp'].validate_on_submit():
        return export()

    return render_template('moodle/Multiple_choice.html', builder_active=act_map['b_act'], MC_form=MC_form, MC_count=MC_count, del_form=f['del'], export_form=f['exp'], pm=f['pm'])


@app.route('/builder/Short_ans/<int:count>', methods=['GET', 'POST'])
def SA_page(count):
    f = form_init()
    SA_count = session['quiz_map']['SA']['count']
    dataset = f['qm']

    class DynamicForm(FlaskForm):
        submit = SubmitField('增加試題')

    if count > 10:
        count = 10
    elif count < 1:
        count = 1
    for i in range(0, count):
        setattr(DynamicForm, 'form-' + str(i), FormField(CreateSA))
    form = DynamicForm()
    # 如果SA表單成功送出
    if form.validate_on_submit():

        # 印出格式化表單內容
        print('[成功建立題目]:', SA_format(f['SA']))

        # 使用區域變數修正再存入
        dataset['SA']['count'] += 1
        dataset['SA']['list'].append(SA_format(f['SA']))
        session['quiz_map'] = dataset
        #
        preview_SA(f['SA'], f['pm'])
        session['preview_map'] = f['pm']

        # 引導回SA頁
        return redirect(count)

    if f['del'].validate_on_submit():
        return del_quiz()

    if f['exp'].validate_on_submit():
        return export()

    return render_template('moodle/short_ans.html', builder_active=act_map['b_act'], SA_form=form, SA_count=SA_count, del_form=f['del'], export_form=f['exp'], pm=f['pm'])


def del_quiz():
    # pop session試卷
    session.pop('quiz_map')
    session.pop('preview_map')
    return redirect('/builder')


def export():
    def generate():
        # 取得session資料
        dataset = session.get('quiz_map')
        # 組合最後字串
        final_str = b''
        for type in dataset:
            for line in dataset[type]['list']:
                final_str += line.encode('utf-8')+b'\n\n'
        return final_str
    timenow = time.time()
    local_time = time_format(timenow)
    # !超強大功能!!!!!!直接生成檔案回傳，不存在伺服端
    response = make_response(Response(generate(), mimetype='text/gift'))
    response.headers["Content-Disposition"] = "attachment; filename=%s.gift;" % (
        local_time)
    return response


@app.route('/contact')
def contact():

    return render_template('contact.html', contact_active=act_map['c_act'])


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    # !正式入口
    app.run(host='0.0.0.0', port=port)
    # app.run(debug=True)
