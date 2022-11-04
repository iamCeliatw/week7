from flask import * 
import mysql.connector
from mySQL import MySQLPassword

app = Flask(
    __name__,
    static_folder="static/",
    static_url_path="/"
)

#設定session 密鑰
app.secret_key= "fjehiwqdmkdn313"
# connect sql

# 連接資料庫
mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    password=MySQLPassword(),
    database='website')


# 把資料庫連接常用指令做成Function
def select1(sql, val):
    # 使用cursor方法建立指標對象
    mycursor = mydb.cursor()
    mycursor.execute(sql, val)
    data = mycursor.fetchone()
    mycursor.close()
    return data


def sql_execute(sql, val=''):
    mycursor = mydb.cursor()
    mycursor.execute(sql, val)
    mydb.commit()
    mycursor.close()

def selectall(sql, val=''):
    mycursor = mydb.cursor()
    mycursor.execute(sql, val)
    data = mycursor.fetchall()
    mycursor.close()
    return data


@app.route("/",methods=["GET", "POST"])
def index():
    return render_template("index2.html")


@app.route('/signup', methods=["POST"])
def signup():
    name = request.form['name']
    account = request.form['account']
    password = request.form['password']
    sql = 'SELECT * FROM member WHERE username = %s'
    val = [account]
    user = select1(sql, val)
    if user != None:
        return redirect("/error?message=帳號已經被註冊")
    elif name == "" or account == "" or password == "":
        return redirect("/error?message=請輸入完整資訊")
    # 把資料放進資料庫
    sql = "INSERT INTO member (name, username, password) VALUES (%s, %s, %s)"
    val = [name, account, password]
    sql_execute(sql, val)
    return redirect('/')


# 驗證系統路由 使用POST
@app.route("/signin", methods=["POST"])
def signin():
    account = ''
    password = ''
    if 'account' in request.form and 'password' in request.form:
        account = request.form['account']
        password = request.form['password']
    # 使用execute執行SQL檢查是否有相同名字
    val = [account, password]
    sql = 'SELECT * FROM member WHERE username = %s AND password = %s'
    user = select1(sql, val)
    if user:
        session['login'] = True
        session['id'] = user[0]
        session['name'] = user[1]
        session['act'] = user[2]
        session['pwd'] = user[3]
        return redirect('/member')
    elif account == "" or password == "":
        return redirect("/error?message=請輸入帳號、密碼")
    else:
        return redirect("/error?message=帳號、或密碼輸入錯誤")


# 成功登入頁
@app.route("/member")
def member():
    if 'act' in session and 'pwd' in session:
        sql = 'SELECT member.name, message.content FROM `message` \
             JOIN `member`ON member_id = member.id ORDER BY message.time DESC ;'
        res = selectall(sql)
        return render_template("success.html", username=session['name'], data=res)
    else:
        return redirect("/")

# 驗證訊息框內容是否為空
@app.route("/message", methods=['POST'])
def message():
    data = request.form.to_dict()
    # 需要做登入驗證 因為前端發的request是不可被信任的 會被模擬出來
    member_id = session['id']
    if data['message'] != '':
        sql = "INSERT INTO message(member_id, content) VALUES (%s, %s)"
        val = [member_id, data['message']]
        sql_execute(sql, val)
        return redirect('/member')
    else:
        return redirect("/error?message=請輸入文字")

# 失敗登入頁
@app.route("/error")
def error():
    data = request.args.get('message', '發生錯誤')
    return render_template("error.html", data=data)


# 成功登出頁
@app.route("/signout")
def signout():
    session.clear()
    return redirect("/")

@app.route('/api/member',methods=['GET','PATCH'])
def api_member():
    result = request.args.get('userName')
    if request.method == 'GET':
        sql = "SELECT json_object('id',id, 'name', name, 'username', username) FROM member WHERE username = %s"
        val = [result]
        mycursor = mydb.cursor()
        mycursor.execute(sql, val)
        result = mycursor.fetchone()
        if result is None or result == '':
            return jsonify({'data': None})
        json_data = json.loads(result[0])
        return jsonify({'data': json_data})


    if request.method == 'PATCH':
       # 取得使用者輸入的值並轉成json格式
        data = request.get_data()
        json_data = json.loads(data.decode("UTF-8"))
         # 檢查欄位是否為空 並將輸入值更新mysql & session
        if json_data['name'] != '':
            sql = 'UPDATE member SET name = %s WHERE id = %s'
            val = [json_data['name'], session['id']]
            sql_execute(sql, val)
            session['name'] = json_data['name']
            return jsonify({"ok": True})
        else:
            return jsonify({"error": True})


if __name__ == '__main__':
    app.run(port=3000, debug=True)
