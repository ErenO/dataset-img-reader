from flask import Markup
from flask import Blueprint, Flask, flash, render_template, request, session
from flask_bootstrap import Bootstrap
import os
import sys
import random
import pandas as pd
import random
import json
from pprint import pprint

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'my unobvious secret key'
df = None
lbls = None
lbl_req = ''
imgLst = None
data = None
tags = None
imgLen = 0
tag_to_imgs = {}
img_to_tags = {}
lbl_to_tag = {}

def create_tag_to_imgs():
    dic = {}
    for i in range(0, 229):
        keyLst = []
        for key, value in img_to_tags.items():
            if i in value:
                keyLst.append(key)
        dic[i] = keyLst
    return (dic)

def create_lbl_to_tag():
    dic = {}
    for i in range(0, 229):
        for ind, lbl in enumerate(lbls):
            dic.update({lbl:float(ind)})
    return (dic)

def save_df():
    df = pd.DataFrame()
    df['tag'] = tags
    df['label'] = lbls
    df['delete'] = dels
    df.to_csv('tagsLbl2.csv', index=False)
    
@app.before_first_request
def set_model():
    global df
    global lbls
    global lbl_req
    global imgLst
    global data
    global img_to_tags
    global tag_to_imgs
    global lbl_to_tag
    global tags
    global dels
    
    lbl_req = 'pull'
    imgLst = os.listdir('./static/train')
    df = pd.read_csv('tagsLbl.csv')
    lbls = df['label'].values
    tags = df['tag'].values
    with open('./train.json') as f:
        data = json.load(f)
    img_to_tags = {int(dic['imageId']):list(map(int, dic['labelId']))
                   for ind, dic in enumerate(data['annotations'])
                   if ind < len(imgLst)}        
    tag_to_imgs = create_tag_to_imgs()
    lbl_to_tag = create_lbl_to_tag()
    print (lbl_to_tag)
    dels = []
    for i in range(0, 229):
        dels.append(False)
        
@app.route('/handle_data', methods=['GET','POST'])
def handle_data():
    global lbl_req
    lbl_req = request.form.get('lbl_select')
    print ('lbl_req {}'.format(lbl_req))
    return (index())

@app.route('/delete_lbl', methods=['GET','POST'])
def delete_lbl():
    lbl_to_del = request.form['lbl_del']
    tag_to_del = request.form['tag_del']
#     print ('lbl_to_del {}'.format(lbl_to_del))
    dels[tag_to_del] = True
    save_df()
    return (index())

@app.route('/')
def index():
    print ('lbl_req {}'.format(lbl_req))
    if lbl_req == '' or not lbl_req:
        print ('yo')
        randLst = random.sample(range(len(imgLst), 10))
        imgRand = [imgLst[rand] for rand in randLst]
    else:
        print ('bonjour')
        tag_req = lbl_to_tag[lbl_req]        
        print ('tag_req {}'.format(tag_req))
        imgs_req = tag_to_imgs[tag_req]
        randLst = random.sample(range(len(imgs_req)), 10)
        imgRand = [imgs_req[rand] for rand in randLst]
        print (img_to_tags[imgRand[0]])
    res = render_template('index.html',
                         imgFolder=imgRand,
                         lbls=lbls,
                         img_to_tags=img_to_tags,
                         lbl_req=lbl_req)
    return (res)

if __name__ == '__main__':
    app.debug = True
    app.run()