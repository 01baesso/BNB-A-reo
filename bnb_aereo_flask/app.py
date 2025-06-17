from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime, date, timedelta

app = Flask(__name__)
app.secret_key = "uma_chave_secreta_qualquer"  # necessário para flash messages

# ---------------------------------------------------
# 1. Dados em memória: listas de dicionários
# ---------------------------------------------------

# Usuários: cada dicionário terá as chaves:
# id, nome, email, tipo (proprietario ou hospede), telefone, cpf
usuarios = []
proximo_id_usuario = 1

# Imóveis: cada dicionário terá as chaves:
# id, titulo, descricao, endereco, cidade, estado, cep,
# tipo_imovel, num_quartos, num_banheiros, num_vagas,
# acomoda_hospedes, preco_noite, proprietario_id, ativo
imoveis = []
proximo_id_imovel = 1

reservas = []
proximo_id_reserva = 1

avaliacoes = []
proximo_id_avaliacao = 1

# ---------------------------------------------------
# 2. Rotas Gerais (Home)
# ---------------------------------------------------
@app.route("/")
def index():
    return render_template("base.html")  # página inicial simples

# ---------------------------------------------------
# 3. CRUD de Usuários
# ---------------------------------------------------

# 3.1 Listar e filtrar usuários (RF3)
@app.route("/usuarios")
def usuarios_list():
    filtro_nome = request.args.get("nome", "").lower()
    filtro_email = request.args.get("email", "").lower()
    filtro_tipo = request.args.get("tipo", "")

    resultados = []
    for u in usuarios:
        match_nome = filtro_nome in u["nome"].lower() if filtro_nome else True
        match_email = filtro_email in u["email"].lower() if filtro_email else True
        match_tipo = (u["tipo"] == filtro_tipo) if filtro_tipo else True
        if match_nome and match_email and match_tipo:
            resultados.append(u)

    return render_template(
        "usuarios_list.html",
        usuarios=resultados,
        filtros={"nome": filtro_nome, "email": filtro_email, "tipo": filtro_tipo}
    )

# 3.2 Formulário “novo usuário” (RF1)
@app.route("/usuarios/novo")
def usuario_novo():
    return render_template("usuario_form.html", acao="criar", usuario={})

# 3.3 Criar usuário (RF1)
@app.route("/usuarios/criar", methods=["POST"])
def usuario_criar():
    global proximo_id_usuario

    nome = request.form.get("nome", "").strip()
    email = request.form.get("email", "").strip()
    senha = request.form.get("senha", "").strip()
    tipo = request.form.get("tipo", "").strip()
    telefone = request.form.get("telefone", "").strip()
    cpf = request.form.get("cpf", "").strip()

    # Validações básicas:
    if not nome or not email or not senha or not tipo or not cpf:
        flash("Preencha todos os campos obrigatórios.", "error")
        return render_template("usuario_form.html", acao="criar", usuario=request.form)

    # Verificar se email ou CPF já estão em uso:
    for u in usuarios:
        if u["email"].lower() == email.lower():
            flash("Já existe um usuário com este e-mail.", "error")
            return render_template("usuario_form.html", acao="criar", usuario=request.form)
        if u["cpf"] == cpf:
            flash("Já existe um usuário com este CPF.", "error")
            return render_template("usuario_form.html", acao="criar", usuario=request.form)

    # Criar e adicionar à lista
    novo = {
        "id": proximo_id_usuario,
        "nome": nome,
        "email": email,
        "senha": senha,   # em projeto real, jamais armazene a senha em texto puro!
        "tipo": tipo,     # "proprietario" ou "hospede"
        "telefone": telefone,
        "cpf": cpf
    }
    usuarios.append(novo)
    proximo_id_usuario += 1

    flash("Usuário cadastrado com sucesso!", "success")
    return redirect(url_for("usuarios_list"))

# 3.4 Formulário “editar usuário” (RF2)
@app.route("/usuarios/<int:id>/editar")
def usuario_editar(id):
    u = next((u for u in usuarios if u["id"] == id), None)
    if not u:
        flash("Usuário não encontrado.", "error")
        return redirect(url_for("usuarios_list"))
    return render_template("usuario_form.html", acao="editar", usuario=u)

# 3.5 Atualizar usuário (RF2)
@app.route("/usuarios/<int:id>/atualizar", methods=["POST"])
def usuario_atualizar(id):
    u = next((u for u in usuarios if u["id"] == id), None)
    if not u:
        flash("Usuário não encontrado.", "error")
        return redirect(url_for("usuarios_list"))

    nome = request.form.get("nome", "").strip()
    email = request.form.get("email", "").strip()
    senha = request.form.get("senha", "").strip()
    telefone = request.form.get("telefone", "").strip()
    # Não permitimos editar CPF e tipo de usuário para simplificar

    if not nome or not email:
        flash("Nome e e-mail são obrigatórios.", "error")
        return render_template("usuario_form.html", acao="editar", usuario=request.form)

    # Verificar se outro usuário já usa o mesmo email:
    for outro in usuarios:
        if outro["id"] != id and outro["email"].lower() == email.lower():
            flash("Já existe um usuário com este e-mail.", "error")
            return render_template("usuario_form.html", acao="editar", usuario=request.form)

    # Atualizar campos
    u["nome"] = nome
    u["email"] = email
    if senha:
        u["senha"] = senha
    u["telefone"] = telefone

    flash("Usuário atualizado com sucesso!", "success")
    return redirect(url_for("usuarios_list"))

# 3.6 Remover usuário (RF4)
@app.route("/usuarios/<int:id>/remover", methods=["POST"])
def usuario_remover(id):
    u = next((u for u in usuarios if u["id"] == id), None)
    if not u:
        flash("Usuário não encontrado.", "error")
        return redirect(url_for("usuarios_list"))

    # Se for proprietário, verificar se há imóveis vinculados (RF4)
    if u["tipo"] == "proprietario":
        tem_imovel = any(im for im in imoveis if im["proprietario_id"] == id and im["ativo"])
        if tem_imovel:
            flash("Não é possível remover: este proprietário tem imóvel ativo.", "error")
            return redirect(url_for("usuarios_list"))

    # Remover da lista
    usuarios.remove(u)
    flash("Usuário removido com sucesso!", "success")
    return redirect(url_for("usuarios_list"))

# ---------------------------------------------------
# 4. CRUD de Imóveis
# ---------------------------------------------------

# 4.1 Listar e filtrar imóveis (RF7)
@app.route("/imoveis")
def imoveis_list():
    filtro_cidade = request.args.get("cidade", "").lower()
    filtro_estado = request.args.get("estado", "").lower()
    filtro_tipo = request.args.get("tipo", "")

    resultados = []
    for im in imoveis:
        if not im["ativo"]:
            continue
        match_cidade = filtro_cidade in im["cidade"].lower() if filtro_cidade else True
        match_estado = filtro_estado in im["estado"].lower() if filtro_estado else True
        match_tipo = (im["tipo_imovel"] == filtro_tipo) if filtro_tipo else True
        if match_cidade and match_estado and match_tipo:
            resultados.append(im)

    return render_template(
        "imoveis_list.html",
        imoveis=resultados,
        filtros={"cidade": filtro_cidade, "estado": filtro_estado, "tipo": filtro_tipo},
        usuarios=usuarios  # para exibir nome do proprietário
    )

# 4.2 Formulário “novo imóvel” (RF5)
@app.route("/imoveis/novo")
def imovel_novo():
    # Precisamos passar a lista de proprietários existentes
    proprietarios = [u for u in usuarios if u["tipo"] == "proprietario"]
    return render_template(
        "imovel_form.html",
        acao="criar",
        imovel={},
        proprietarios=proprietarios,
        usuarios=usuarios
    )

# 4.3 Criar imóvel (RF5)
@app.route("/imoveis/criar", methods=["POST"])
def imovel_criar():
    global proximo_id_imovel

    titulo = request.form.get("titulo", "").strip()
    descricao = request.form.get("descricao", "").strip()
    endereco = request.form.get("endereco", "").strip()
    cidade = request.form.get("cidade", "").strip()
    estado = request.form.get("estado", "").strip()
    cep = request.form.get("cep", "").strip()
    tipo_imovel = request.form.get("tipo_imovel", "").strip()
    num_quartos = request.form.get("num_quartos", "").strip()
    num_banheiros = request.form.get("num_banheiros", "").strip()
    num_vagas = request.form.get("num_vagas", "").strip()
    acomoda = request.form.get("acomoda", "").strip()
    preco = request.form.get("preco", "").strip()
    proprietario_id = request.form.get("proprietario_id", "").strip()

    # Validações básicas
    if not (titulo and descricao and endereco and cidade and estado and cep
            and tipo_imovel and num_quartos.isdigit()
            and num_banheiros.isdigit() and acomoda.isdigit()
            and preco.replace(".", "").isdigit() and proprietario_id.isdigit()):
        flash("Preencha todos os campos corretamente.", "error")
        return redirect(url_for("imovel_novo"))

    # Verificar se o proprietário existe
    pid = int(proprietario_id)
    obj_prop = next((u for u in usuarios if u["id"] == pid and u["tipo"] == "proprietario"), None)
    if not obj_prop:
        flash("Selecione um proprietário válido.", "error")
        return redirect(url_for("imovel_novo"))

    novo = {
        "id": proximo_id_imovel,
        "titulo": titulo,
        "descricao": descricao,
        "endereco": endereco,
        "cidade": cidade,
        "estado": estado,
        "cep": cep,
        "tipo_imovel": tipo_imovel,
        "num_quartos": int(num_quartos),
        "num_banheiros": int(num_banheiros),
        "num_vagas": int(num_vagas) if num_vagas.isdigit() else 0,
        "acomoda_hospedes": int(acomoda),
        "preco_noite": float(preco),
        "proprietario_id": pid,
        "ativo": True
    }
    imoveis.append(novo)
    proximo_id_imovel += 1

    flash("Imóvel cadastrado com sucesso!", "success")
    return redirect(url_for("imoveis_list"))

# 4.4 Formulário “editar imóvel” (RF6)
@app.route("/imoveis/<int:id>/editar")
def imovel_editar(id):
    im = next((im for im in imoveis if im["id"] == id), None)
    if not im:
        flash("Imóvel não encontrado.", "error")
        return redirect(url_for("imoveis_list"))
    proprietarios = [u for u in usuarios if u["tipo"] == "proprietario"]
    return render_template(
        "imovel_form.html",
        acao="editar",
        imovel=im,
        proprietarios=proprietarios,
        usuarios=usuarios
    )

# 4.5 Atualizar imóvel (RF6)
@app.route("/imoveis/<int:id>/atualizar", methods=["POST"])
def imovel_atualizar(id):
    im = next((im for im in imoveis if im["id"] == id), None)
    if not im:
        flash("Imóvel não encontrado.", "error")
        return redirect(url_for("imoveis_list"))

    titulo = request.form.get("titulo", "").strip()
    descricao = request.form.get("descricao", "").strip()
    endereco = request.form.get("endereco", "").strip()
    cidade = request.form.get("cidade", "").strip()
    estado = request.form.get("estado", "").strip()
    cep = request.form.get("cep", "").strip()
    tipo_imovel = request.form.get("tipo_imovel", "").strip()
    num_quartos = request.form.get("num_quartos", "").strip()
    num_banheiros = request.form.get("num_banheiros", "").strip()
    num_vagas = request.form.get("num_vagas", "").strip()
    acomoda = request.form.get("acomoda", "").strip()
    preco = request.form.get("preco", "").strip()
    # proprietario_id não editável para simplificar

    # Validações básicas
    if not (titulo and descricao and endereco and cidade and estado and cep
            and tipo_imovel and num_quartos.isdigit()
            and num_banheiros.isdigit() and acomoda.isdigit()
            and preco.replace(".", "").isdigit()):
        flash("Preencha todos os campos corretamente.", "error")
        return redirect(url_for("imovel_editar", id=id))

    # Atualizar campos
    im["titulo"] = titulo
    im["descricao"] = descricao
    im["endereco"] = endereco
    im["cidade"] = cidade
    im["estado"] = estado
    im["cep"] = cep
    im["tipo_imovel"] = tipo_imovel
    im["num_quartos"] = int(num_quartos)
    im["num_banheiros"] = int(num_banheiros)
    im["num_vagas"] = int(num_vagas) if num_vagas.isdigit() else 0
    im["acomoda_hospedes"] = int(acomoda)
    im["preco_noite"] = float(preco)

    flash("Imóvel atualizado com sucesso!", "success")
    return redirect(url_for("imoveis_list"))

# 4.6 “Remover” (desativar) imóvel (RF8)
@app.route("/imoveis/<int:id>/remover", methods=["POST"])
def imovel_remover(id):
    im = next((im for im in imoveis if im["id"] == id), None)
    if not im:
        flash("Imóvel não encontrado.", "error")
        return redirect(url_for("imoveis_list"))
    # Aqui não implementamos reservas; permitimos remover diretamente
    im["ativo"] = False
    flash("Imóvel removido/desativado com sucesso!", "success")
    return redirect(url_for("imoveis_list"))

# =====================
# CRUD de Reservas
# =====================
@app.route('/reservas')
def reservas_list():
    filtro_hospede = request.args.get('hospede', '').lower()
    filtro_status = request.args.get('status', '')
    resultados = []
    for r in reservas:
        # busca por nome do hóspede
        hosp = next((u for u in usuarios if u['id']==r['hospede_id']), None)
        match_hosp = filtro_hospede in hosp['nome'].lower() if filtro_hospede else True
        match_status = (r['status']==filtro_status) if filtro_status else True
        if match_hosp and match_status:
            r_display = r.copy()
            r_display['hospede_nome'] = hosp['nome']
            im = next((i for i in imoveis if i['id']==r['imovel_id']), None)
            r_display['imovel_titulo'] = im['titulo'] if im else ''
            resultados.append(r_display)
    return render_template('reservas_list.html', reservas=resultados, filtros={'hospede': filtro_hospede, 'status': filtro_status})

@app.route('/reservas/novo', methods=['GET','POST'])
def reserva_novo():
    global proximo_id_reserva
    if request.method=='GET':
        # enviar listas de hóspedes e imóveis
        hospedes = [u for u in usuarios if u['tipo']=='hospede']
        ativos = [i for i in imoveis if i['ativo']]
        return render_template('reserva_form.html', acao='criar', reserva={}, hospedes=hospedes, imoveis=ativos)

    # POST: criar reserva
    imovel_id = int(request.form.get('imovel_id','0'))
    hospede_id = int(request.form.get('hospede_id','0'))
    checkin_s = request.form.get('checkin','')
    checkout_s = request.form.get('checkout','')
    qtd = request.form.get('qtd_hospedes','')
    try:
        checkin = datetime.strptime(checkin_s, '%Y-%m-%d').date()
        checkout = datetime.strptime(checkout_s, '%Y-%m-%d').date()
    except:
        flash('Datas inválidas.', 'error')
        return redirect(url_for('reserva_novo'))
    if checkout <= checkin:
        flash('Check-out deve ser após check-in.', 'error')
        return redirect(url_for('reserva_novo'))
    # ver disponibilidade
    for r in reservas:
        if r['imovel_id']==imovel_id and r['status']!='Cancelada':
            if checkin < r['checkout'] and checkout > r['checkin']:
                flash('Imóvel indisponível no intervalo informado.', 'error')
                return redirect(url_for('reserva_novo'))
    # cálculo preço
    im = next((i for i in imoveis if i['id']==imovel_id), None)
    noites = (checkout - checkin).days
    total = im['preco_noite'] * noites
    nova = {
        'id': proximo_id_reserva,
        'imovel_id': imovel_id,
        'hospede_id': hospede_id,
        'checkin': checkin,
        'checkout': checkout,
        'qtd_hospedes': int(qtd),
        'preco_total': total,
        'status': 'Pendente'
    }
    reservas.append(nova)
    proximo_id_reserva += 1
    flash('Reserva criada com sucesso!', 'success')
    return redirect(url_for('reservas_list'))

@app.route('/reservas/<int:id>/editar', methods=['GET','POST'])
def reserva_editar(id):
    r = next((r for r in reservas if r['id']==id), None)
    if not r:
        flash('Reserva não encontrada.', 'error')
        return redirect(url_for('reservas_list'))
    hoje = date.today()
    if request.method=='GET':
        hospedes = [u for u in usuarios if u['tipo']=='hospede']
        ativos = [i for i in imoveis if i['ativo']]
        return render_template('reserva_form.html', acao='editar', reserva=r, hospedes=hospedes, imoveis=ativos)
    # POST: atualizar
    checkin = datetime.strptime(request.form.get('checkin'), '%Y-%m-%d').date()
    checkout = datetime.strptime(request.form.get('checkout'), '%Y-%m-%d').date()
    if checkin <= hoje:
        flash('Não é possível editar após início da estadia.', 'error')
        return redirect(url_for('reservas_list'))
    # mesma validação de disponibilidade
    for other in reservas:
        if other['id']!=id and other['imovel_id']==r['imovel_id'] and other['status']!='Cancelada':
            if checkin < other['checkout'] and checkout > other['checkin']:
                flash('Imóvel indisponível no novo intervalo.', 'error')
                return redirect(url_for('reservas_list'))
    r['checkin'] = checkin
    r['checkout'] = checkout
    noites = (checkout - checkin).days
    r['preco_total'] = next(i for i in imoveis if i['id']==r['imovel_id'])['preco_noite'] * noites
    flash('Reserva atualizada.', 'success')
    return redirect(url_for('reservas_list'))

@app.route('/reservas/<int:id>/remover', methods=['POST'])
def reserva_remover(id):
    r = next((r for r in reservas if r['id']==id), None)
    if not r:
        flash('Reserva não encontrada.', 'error')
    else:
        if date.today() >= r['checkin']:
            r['status'] = 'Cancelada'
            flash('Reserva cancelada.', 'success')
        else:
            reservas.remove(r)
            flash('Reserva removida.', 'success')
    return redirect(url_for('reservas_list'))

# =====================
# CRUD de Avaliações
# =====================
@app.route('/avaliacoes')
def avaliacoes_list():
    filtro_nota = request.args.get('nota_min', '')
    resultados = []
    for a in avaliacoes:
        hosp = next((u for u in usuarios if u['id']==a['hospede_id']), None)
        im = next((i for i in imoveis if i['id']==a['imovel_id']), None)
        if filtro_nota and a['nota'] < int(filtro_nota):
            continue
        rec = a.copy()
        rec['hospede_nome'] = hosp['nome']
        rec['imovel_titulo'] = im['titulo']
        resultados.append(rec)
    return render_template('avaliacoes_list.html', avaliacoes=resultados, filtro_nota=filtro_nota)

@app.route('/avaliacoes/novo', methods=['GET','POST'])
def avaliacao_novo():
    global proximo_id_avaliacao
    if request.method=='GET':
        # só reservas concluídas
        concluidas = [r for r in reservas if r['checkout'] < date.today()]
        return render_template('avaliacao_form.html', acao='criar', avaliacao={}, reservas=concluidas)
    # POST
    reserva_id = int(request.form.get('reserva_id'))
    nota = int(request.form.get('nota'))
    comentario = request.form.get('comentario','').strip()
    # única avaliação por reserva
    if any(a['reserva_id']==reserva_id for a in avaliacoes):
        flash('Avaliação já existe para esta reserva.', 'error')
        return redirect(url_for('avaliacao_novo'))
    # criar
    res = next(r for r in reservas if r['id']==reserva_id)
    hospede_id = res['hospede_id']
    imovel_id = res['imovel_id']
    now = datetime.now()
    nova = {
        'id': proximo_id_avaliacao,
        'reserva_id': reserva_id,
        'hospede_id': hospede_id,
        'imovel_id': imovel_id,
        'nota': nota,
        'comentario': comentario,
        'data': now
    }
    avaliacoes.append(nova)
    proximo_id_avaliacao += 1
    flash('Avaliação cadastrada!', 'success')
    return redirect(url_for('avaliacoes_list'))

@app.route('/avaliacoes/<int:id>/editar', methods=['GET','POST'])
def avaliacao_editar(id):
    a = next((a for a in avaliacoes if a['id']==id), None)
    if not a:
        flash('Avaliação não encontrada.', 'error')
        return redirect(url_for('avaliacoes_list'))
    if request.method=='GET':
        return render_template('avaliacao_form.html', acao='editar', avaliacao=a)
    # POST
    if datetime.now() - a['data'] > timedelta(hours=24):
        flash('Prazo de 24h para editar expirado.', 'error')
        return redirect(url_for('avaliacoes_list'))
    a['nota'] = int(request.form.get('nota'))
    a['comentario'] = request.form.get('comentario','').strip()
    flash('Avaliação atualizada.', 'success')
    return redirect(url_for('avaliacoes_list'))

@app.route('/avaliacoes/<int:id>/remover', methods=['POST'])
def avaliacao_remover(id):
    a = next((a for a in avaliacoes if a['id']==id), None)
    if not a:
        flash('Avaliação não encontrada.', 'error')
    else:
        avaliacoes.remove(a)
        flash('Avaliação removida.', 'success')
    return redirect(url_for('avaliacoes_list'))

# ---------------------------------------------------
# 5. Execução do servidor
# ---------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)