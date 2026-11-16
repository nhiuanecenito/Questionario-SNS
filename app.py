import os, sqlite3, csv, io
from functools import wraps
from flask import Flask, request, redirect, url_for, session, Response, render_template_string, flash
app=Flask(__name__)
app.secret_key=os.environ.get("SECRET_KEY","change-this-secret-before-production")
DB=os.environ.get("DATABASE_PATH","responses.db")
QUESTIONS=[
("1","Qual é o seu nome e há quanto tempo trabalha na SNS?","text",[]),
("2","Com que frequência utiliza sistemas informáticos no seu trabalho diário?","choice",["Raramente","Algumas vezes por semana","Diariamente","Não Utiliza"]),
("3",'O que é "phishing"?',"choice",["Um tipo de Vírus que danifica o computador","Uma tentativa fraudulenta de obter informação sensível fazendo-se passar por uma entidade confiável","Uma falha técnica no sistema de e-mail","Não Sei"]),
("4","Qual das seguintes opções descreve melhor a autenticação multifator?","choice",["Utilizar duas ou mais formas de verificação para aceder a uma conta","Utilizar uma palavra-passe mais longa","Alterar a palavra-passe todos os dias","Não sei"]),
("5","A empresa já lhe deu alguma formação sobre segurança da informação?","choice",["Sim","Não"]),
("6","Com que frequência muda a sua palavra-passe de acesso aos sistemas da empresa?","choice",["Nunca","Raramente","Regularmente","Conforme Política da empresa"]),
("7","Partilhou alguma vez a sua palavra-passe com colegas, por conveniência?","choice",["Sim","Não"]),
("8","Apresentar um exemplo real ou simulado de e-mail de phishing. Reconheceria este e-mail como suspeito?","choice",["Sim","Não","Não tenho a certeza"]),
("9","Se recebesse um e-mail a pedir urgentemente a sua palavra-passe, o que faria?","choice",["Responderia com a Informação","Ignoraria","Reportaria ao departamento de TI"]),
("10","Sabe se existe uma política escrita de segurança da informação na SNS?","choice",["Sim","Não"]),
("11","Se suspeitasse de um problema de segurança (ex.: computador infectado, e-mail suspeito), a quem reportaria?","choice",["Ao departamento de TI / responsável de informática","A um colega de trabalho, informalmente","Não saberia a quem reportar","Resolveria sozinho (a), sem reportar"]),
("12","Numa escala de 1 a 5, como classifica o nível de preparação da SNS para lidar com um ataque cibernético? (1 = nada preparada, 5 = muito preparada)","scale",["1","2","3","4","5"]),
("13","Numa escala de 1 (baixo) a 5 (crítico), como classificaria o risco actual da rede da SNS sofrer um ataque bem-sucedido nos próximos meses?","scale",["1","2","3","4","5"]),
("14","Sente que tem conhecimento suficiente para identificar uma ameaça cibernética no seu dia-a-dia de trabalho?","choice",["Sim","Não"]),
("15","Um colaborador ter a sua palavra-passe roubada através de um e-mail falso (phishing). Classifique a gravidade para a SNS (1 = pouco grave; 5 = muito grave).","scale",["1","2","3","4","5"]),
("16","Um ex-colaborador continuar a ter acesso aos sistemas da empresa após sair. Classifique a gravidade para a SNS (1 = pouco grave; 5 = muito grave).","scale",["1","2","3","4","5"]),
("17","Um computador da empresa ficar infectado com um vírus que apaga ficheiros. Classifique a gravidade para a SNS (1 = pouco grave; 5 = muito grave).","scale",["1","2","3","4","5"])]
def db():
 c=sqlite3.connect(DB); c.execute("CREATE TABLE IF NOT EXISTS responses(id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT DEFAULT CURRENT_TIMESTAMP, answers TEXT NOT NULL)"); return c
def admin_required(f):
 @wraps(f)
 def w(*a,**k):
  if not session.get("admin"): return redirect(url_for("login"))
  return f(*a,**k)
 return w
BASE="""<!doctype html><html lang=pt><meta name=viewport content="width=device-width,initial-scale=1"><title>{{title}}</title><style>
*{box-sizing:border-box}body{font-family:Arial,sans-serif;background:#f3f5f8;color:#172033;margin:0;padding:20px}.wrap{max-width:850px;margin:20px auto;background:white;padding:28px;border-radius:14px;box-shadow:0 4px 22px #14213d12}h1{color:#123c65}h2{font-size:18px;margin-top:28px;color:#123c65}.muted{color:#5c6675;line-height:1.6}.q{padding:15px 0;border-bottom:1px solid #e8edf2}.opt{display:block;padding:8px 0}input[type=text],input[type=password]{width:100%;padding:12px;border:1px solid #ccd4df;border-radius:8px}button,.btn{background:#145b91;color:white;border:0;padding:12px 18px;border-radius:8px;text-decoration:none;display:inline-block;cursor:pointer;margin:8px 5px 8px 0}button:hover,.btn:hover{background:#0c426d}.notice{background:#eef7ff;padding:14px;border-radius:8px}.err{color:#a22}table{border-collapse:collapse;width:100%;font-size:14px}td,th{border:1px solid #dce2e8;padding:8px;text-align:left}small{color:#697586}</style><div class=wrap>{% with messages=get_flashed_messages() %}{% for m in messages %}<p class=notice>{{m}}</p>{% endfor %}{% endwith %}{{body|safe}}</div></html>"""
def page(title,body,**kw): return render_template_string(BASE,title=title,body=render_template_string(body,**kw))
@app.get("/")
def index():
 body="""<h1>Questionário — Segurança Cibernética na SNS</h1><p class=muted><b>Dirigido a:</b> Funcionários Administrativos</p><p class=muted>Este questionário é aplicado no âmbito de uma monografia de licenciatura, com o objectivo de compreender as práticas e os conhecimentos dos colaboradores da SNS em matéria de segurança cibernética. As respostas são confidenciais e serão utilizadas exclusivamente para fins académicos. Como este questionário solicita o seu nome, a participação não é anónima. O preenchimento é voluntário e pode ser interrompido a qualquer momento sem qualquer consequência. Não existem respostas certas ou erradas: pretende-se apenas conhecer a sua experiência e percepção reais. Agradece-se a sua colaboração.</p><form method=post action=/submit>"""
 sections={1:"Perfil",3:"Conhecimento Geral de Segurança Cibernética",6:"Práticas de Palavra-passe",8:"Reconhecimento de Ameaças (cenário prático)",10:"Políticas Internas",12:"Percepção de Risco",15:"Percepção de Gravidade dos Riscos"}
 for n,q,t,opts in QUESTIONS:
  if n in sections: body+=f"<h2>Secção {list(sections).index(n)+1}: {sections[n]}</h2>"
  body+=f'<div class=q><b>{n}. {q}</b>'
  if t=="text": body+=f'<p><input type=text name=q{n} required placeholder="Escreva a sua resposta"></p>'
  else:
   if t=="scale": body+='<p><small>Seleccione uma opção de 1 a 5.</small></p>'
   for o in opts: body+=f'<label class=opt><input type=radio name=q{n} value="{o}" required> {o}</label>'
  body+="</div>"
 body+="<p class=notice>Ao submeter, confirma que participa voluntariamente. O seu nome será recolhido apenas para fins desta pesquisa e tratado com confidencialidade.</p><button type=submit>Enviar respostas</button></form>"
 return page("Questionário SNS",body)
@app.post("/submit")
def submit():
 import json
 answers={}
 for n,_,_,_ in QUESTIONS:
  v=request.form.get("q"+n,"").strip()
  if not v: return "Falta responder à pergunta "+n,400
  answers[n]=v
 c=db(); c.execute("INSERT INTO responses(answers) VALUES(?)",(json.dumps(answers,ensure_ascii=False),)); c.commit(); c.close()
 return page("Resposta recebida","<h1>Obrigado pela sua participação!</h1><p class=muted>As suas respostas foram registadas anonimamente com sucesso.</p>")
@app.route("/admin",methods=["GET","POST"])
def login():
 if request.method=="POST":
  if request.form.get("password")==os.environ.get("ADMIN_PASSWORD",""):
   if not os.environ.get("ADMIN_PASSWORD"): return page("Configuração necessária","<h1>Configuração necessária</h1><p>Defina ADMIN_PASSWORD nas variáveis de ambiente do serviço.</p>")
   session["admin"]=True; return redirect("/admin/responses")
  flash("Palavra-passe incorrecta.")
 return page("Administração","<h1>Área administrativa</h1><form method=post><p>Palavra-passe de administrador</p><input type=password name=password required><button>Entrar</button></form>")
@app.get("/admin/responses")
@admin_required
def responses():
 import json
 c=db(); rows=c.execute("SELECT id,created_at,answers FROM responses ORDER BY id DESC").fetchall(); c.close()
 body="<h1>Respostas recebidas</h1><p><a class=btn href=/admin/export>Exportar CSV</a> <a class=btn href=/admin/logout>Sair</a></p><p>Total: "+str(len(rows))+"</p><table><tr><th>#</th><th>Data</th><th>Respostas</th></tr>"
 for rid,dt,a in rows:
  body+="<tr><td>"+str(rid)+"</td><td>"+dt+"</td><td>"+ " | ".join(f"{k}: {v}" for k,v in json.loads(a).items())+"</td></tr>"
 body+="</table>"
 return page("Respostas",body)
@app.get("/admin/export")
@admin_required
def export():
 import json
 c=db(); rows=c.execute("SELECT id,created_at,answers FROM responses ORDER BY id").fetchall(); c.close()
 out=io.StringIO(); w=csv.writer(out); w.writerow(["ID","Data"]+[q[1] for q in QUESTIONS])
 for rid,dt,a in rows:
  ans=json.loads(a); w.writerow([rid,dt]+[ans.get(q[0],"") for q in QUESTIONS])
 return Response("\ufeff"+out.getvalue(),mimetype="text/csv",headers={"Content-Disposition":"attachment; filename=respostas_sns.csv"})
@app.get("/admin/logout")
def logout(): session.clear(); return redirect("/")
if __name__=="__main__": app.run(host="0.0.0.0",port=int(os.environ.get("PORT",5000)))
