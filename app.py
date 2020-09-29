from flask import *
import json

app=Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method=='POST':
        regno=request.form['regno']
        pswd=request.form['pass']
        f=open('static/json/logins.json','r')
        js=json.load(f)
        f.close()

        #login check
        for i in js['users']:
            if i['regno']==regno and i['pswd']==pswd:
                
                f=open('static/json/admins.json', 'r')
                adjs=json.load(f)
                f.close()

                if regno in adjs['users']:
                    return render_template('adminlogin.html')
                else:
                    return render_template('normallogin.html')
        return render_template('index.html', loginfailed=True)
    else:
        return render_template('index.html')

@app.route('/access/')
def accesssite404():
    return render_template('404.html')

@app.route('/access/<site>', methods=['POST', 'GET'])
def accesssite(site):
    if request.method=='POST':
        regno=request.form['regno']
        pswd=request.form['pass']
        f=open('static/json/logins.json','r')
        js=json.load(f)
        f.close()

        #login check
        for i in js['users']:
            if i['regno']==regno and i['pswd']==pswd:

                f=open('static/json/sitelist.json', 'r')
                sitelistjson=json.load(f)
                f.close()

                if regno in sitelistjson[site]['users_authorized']:
                    return redirect(sitelistjson[site]['link'])
                else:
                    return render_template('accessdenied.html')
        return render_template('index.html', loginfailed=True)
    else:
        f=open('static/json/sitelist.json', 'r')
        sitelistjson=json.load(f)
        f.close()

        if site in sitelistjson.keys():
            if sitelistjson[site]['open_to_all']:
                return redirect(sitelistjson[site]['link'])
            else:
                return render_template('accesslogin.html')

        return render_template('404.html')

@app.route('/getloginslist')
def getloginslist():
    f=open('static/json/logins.json','r')
    js=json.load(f)
    f.close()

    dr={"users":[]}

    for s in js['users']:
        dr['users'].append(s['regno'])

    return jsonify(dr)

@app.route('/urlsubmithandler', methods=['POST'])
def submithandler():
    print(request.form.getlist('students'))
    f=open('static/json/sitelist.json','r')
    js=json.load(f)
    f.close()
    t={}
    t['users_authorized']=request.form.getlist('students')
    print(request.form['open_to_all'])
    t['open_to_all']=request.form['open_to_all']=='yes'
    t['link']=request.form['link']
    js[request.form['custom']]=t

    
    f=open('static/json/sitelist.json','w')
    f.write(json.dumps(js, indent=4))
    f.close()
    return str(js)

if __name__ == '__main__':
    app.run(debug=True)