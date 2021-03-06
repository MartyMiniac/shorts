from flask import *
import json
import requests

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
                    res=make_response(render_template('adminlogin.html'))
                    res.set_cookie('regno',regno)
                    res.set_cookie('pswd',pswd)
                    return res
                else:                    
                    res=make_response(render_template('normallogin.html'))
                    res.set_cookie('regno',regno)
                    res.set_cookie('pswd',pswd)
                    return res
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
        return render_template('accesslogin.html', loginfailed=True)
    else:
        regno=request.cookies.get('regno')
        pswd=request.cookies.get('pswd')

        f=open('static/json/sitelist.json', 'r')
        sitelistjson=json.load(f)
        f.close()

        if site in sitelistjson.keys():
            if sitelistjson[site]['open_to_all']:
                return redirect(sitelistjson[site]['link'])
            else:
                if checkLogin(regno, pswd) and regno!=None:
                    f=open('static/json/sitelist.json', 'r')
                    sitelistjson=json.load(f)
                    f.close()

                    if regno in sitelistjson[site]['users_authorized']:
                        return redirect(sitelistjson[site]['link'])
                    else:
                        return render_template('accessdenied.html')

                return render_template('accesslogin.html')

        return render_template('404.html')

@app.route('/getloginslist')
def getloginslist():
    regno=request.cookies.get('regno')
    pswd=request.cookies.get('pswd')

    if checkLogin(regno, pswd) == False or checkAdmin(regno)==False:
        return render_template('msgtimed.html', title='Authentication Failure', msg='Sever is Unable to resolve who you are due to password change or deletion of cookie. Please Login Again')

    f=open('static/json/logins.json','r')
    js=json.load(f)
    f.close()

    dr={"users":[]}

    for s in js['users']:
        dr['users'].append(s['regno'])

    return jsonify(dr)

@app.route('/urlsubmithandler', methods=['POST'])
def submithandler():
    regno=request.cookies.get('regno')
    pswd=request.cookies.get('pswd')

    if checkLogin(regno, pswd) == False or checkAdmin(regno)==False:
        return render_template('msgtimed.html', title='Authentication Failure', msg='Sever is Unable to resolve who you are due to password change or deletion of cookie. Please Login Again')

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
    updatedb('sitelist.json')
    return ('',204)

@app.route('/sitemanagerhtml')
def sitemanagerpage():
    regno=request.cookies.get('regno')
    pswd=request.cookies.get('pswd')
    if regno==None or checkLogin(regno,pswd)==False or checkAdmin(regno)==False:
        return jsonify({'Error':'Authentication Failure'})
    return render_template('sitemanage.html')

@app.route('/deletesitelisting', methods=['POST'])
def deletesitelisting():
    regno=request.cookies.get('regno')
    pswd=request.cookies.get('pswd')

    if checkLogin(regno, pswd) == False or checkAdmin(regno)==False:
        return render_template('msgtimed.html', title='Authentication Failure', msg='Sever is Unable to resolve who you are due to password change or deletion of cookie. Please Login Again')
    sname=request.form['sitename']
    f=open('static/json/sitelist.json','r')
    js=json.load(f)
    f.close()

    del js[sname]

    f=open('static/json/sitelist.json','w')
    f.write(json.dumps(js, indent=4))
    f.close()

    updatedb('sitelist.json')
    return 'Done!!'

@app.route('/sitemanager', methods=['GET', 'POST'])
def sitemanager():
    if request.method=='POST':
        
        regno=request.cookies.get('regno')
        pswd=request.cookies.get('pswd')

        if checkLogin(regno, pswd) == False or checkAdmin(regno)==False:
            return render_template('msgtimed.html', title='Authentication Failure', msg='Sever is Unable to resolve who you are due to password change or deletion of cookie. Please Login Again')

        f=open('static/json/sitelist.json','r')
        js=json.load(f)
        f.close()

        js[request.form['key']]['open_to_all']=request.form['open_to_all']=='yes'
        if js[request.form['key']]['open_to_all']==False:
            js[request.form['key']]['users_authorized']=request.form.getlist('students')
        js[request.form['key']]['link']=request.form['url']
        
        f=open('static/json/sitelist.json','w')
        f.write(json.dumps(js, indent=4))
        f.close()

        updatedb('sitelist.json')
        return redirect('/sitemanagerhtml')
    else:
        regno=request.cookies.get('regno')
        pswd=request.cookies.get('pswd')
        if regno==None or checkLogin(regno,pswd)==False or checkAdmin(regno)==False:
            return jsonify({'Error':'Authentication Failure'})
        else:
            f=open('static/json/sitelist.json','r')
            js=json.load(f)
            f.close()
            return jsonify(js)
        

@app.route('/changepass', methods=['POST'])
def changepass():
    regno=request.cookies.get('regno')
    pswd=request.cookies.get('pswd')

    if checkLogin(regno, pswd) == False:
        return render_template('msgtimed.html', title='Authentication Failure', msg='Sever is Unable to resolve who you are due to password change or deletion of cookie. Please Login Again')

    oldpass=request.form['oldpass']
    newpass=request.form['newpass']
    f=open('static/json/logins.json','r')
    js=json.load(f)
    f.close()
    for s in js['users']:
        if regno == s['regno'] and oldpass == s['pswd']:
            s['pswd']=newpass            
            f=open('static/json/logins.json','w')
            f.write(json.dumps(js, indent=4))
            f.close()
            updatedb('logins.json')
            return render_template('msgtimed.html',title='Password Changed', msg='Password Changed Successfully please Relogin using new Password')
    
    return render_template('msgtimed.html',title='Password Not Changed', msg='There was an Error. Your Regno or old password would be Wrong. Please Relogin using new Password')

def updatedb(s):
    js={
        "sitelist.json" : "5f7729a173d1b37e00027365",
        "logins.json" : "5f77298373d1b37e00027361",
        "admins.json" : "5f77295c73d1b37e0002735c"
    }

    url = "https://codexshorts-d55b.restdb.io/rest/basic/"+js[s]

    f=open('static\json\\'+s,'r')
    tmp=json.load(f)
    payload = {"value":json.dumps(tmp, indent=4)}
    print(payload)
    f.close()
    headers = {
        'content-type': "application/json",
        'x-apikey': "3efcf6caf6e519b2a48b14b7bc92c627887dd",
        'cache-control': "no-cache"
        }

    response = requests.request("PUT", url, data=json.dumps(payload), headers=headers)

    print(response.text)

def checkLogin(regno, pswd):
    f=open('static/json/logins.json')
    js=json.load(f)
    f.close()

    for s in js['users']:
        if s['regno']==regno and s['pswd']==pswd:
            return True
    
    return False

def checkAdmin(regno):
    f=open('static/json/admins.json')
    js=json.load(f)
    f.close()

    for s in js['users']:
        if s==regno:
            return True
    
    return False

if __name__ == '__main__':
    url = "https://codexshorts-d55b.restdb.io/rest/basic"

    f=open('restdbkey.txt','r')
    key=f.read()
    f.close()
    headers = {
        'content-type': "application/json",
        'x-apikey': key,
        'cache-control': "no-cache"
        }

    response = requests.request("GET", url, headers=headers)

    tmpjson=json.loads(response.text)
    for s in tmpjson:
        f=open('static\json\\'+s['name'],'w')
        f.write(json.dumps(s['value'], indent=4))
        f.close()

    app.run(debug=True)