from flask import Flask, render_template_string
import sqlite3

app = Flask(__name__)

DB = "saas.db"

HTML = """
<h1>📦 SaaS Admin</h1>
<table border=1 cellpadding=10>
<tr><th>ID</th><th>Ім’я</th><th>Товар</th><th>Статус</th></tr>
{% for o in orders %}
<tr>
<td>{{o[0]}}</td>
<td>{{o[1]}}</td>
<td>{{o[2]}}</td>
<td>{{o[3]}}</td>
</tr>
{% endfor %}
</table>
"""

def get_orders():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders ORDER BY id DESC")
    return cur.fetchall()

@app.route("/admin")
def admin():
    return render_template_string(HTML, orders=get_orders())

app.run(debug=True)