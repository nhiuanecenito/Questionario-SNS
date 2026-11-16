# Questionário SNS — Segurança Cibernética

Aplicação web para recolha anónima das 17 respostas do questionário da monografia.

## Executar localmente

```bash
pip install -r requirements.txt
export ADMIN_PASSWORD='defina-uma-palavra-passe-forte'
export SECRET_KEY='uma-chave-secreta'
python app.py
```

Aceda a `http://localhost:5000`. Administração em `/admin`; configure `ADMIN_PASSWORD` no ambiente. O CSV é exportado na área administrativa.

## Publicação

O `render.yaml` configura o serviço web e disco persistente. Defina `ADMIN_PASSWORD` como segredo no Render antes de usar a área administrativa.

O formulário não solicita nome ou e-mail. A primeira pergunta é texto livre; as restantes seguem as opções apresentadas no documento fornecido.
