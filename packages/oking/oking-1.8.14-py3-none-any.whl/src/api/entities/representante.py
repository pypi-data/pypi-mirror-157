
class SaleRegion:
    name: str
    erp_code: str

    def __init__(self, nome, codigo_externo):
        self.name = nome
        self.erp_code = codigo_externo


class SaleHierarchy:
    description: str
    commission_percentage: int
    commission_scope: int
    parent_sale_hierarchy: str

    def __init__(self, descricao, percentual_comissao, percentual_alcada, hierarquia_venda_pai):
        self.description = descricao
        self.commission_percentage = percentual_comissao
        self.commission_scope = percentual_alcada
        self.parent_sale_hierarchy = hierarquia_venda_pai


class Representative:
    codigo_externo: str
    nome: str
    telefone_celular: str
    telefone_fixo: str
    login: str
    password: str
    supervisor: bool
    senha_temporaria: bool
    ativar_representante: bool
    email: str
    regiao_venda: SaleRegion
    gerente: bool
    meta: int
    percentual_meta: int
    aprovacao_pedido_automatica: bool
    percentual_comissao: int
    percentual_alcada: int
    hierarquia_venda: SaleHierarchy
    codigo_representante_pai: str

    def __init__(self, codigo_externo, nome, telefone_celular, telefone_fixo, login, password, supervisor, senha_temporaria, ativar_representante, email, regiao_venda, gerente, meta, percentual_meta,
                 aprovacao_pedido_automatica, percentual_comissao, percentual_alcada, hierarquia_venda, codigo_representante_pai):
        self.codigo_externo = codigo_externo
        self.nome = nome
        self.telefone_celular = telefone_celular
        self.telefone_fixo = telefone_fixo
        self.login = login
        self.password = password
        self.supervisor = supervisor
        self.senha_temporaria = senha_temporaria
        self.ativar_representante = ativar_representante
        self.email = email
        self.regiao_venda = regiao_venda
        self.gerente = gerente
        self.meta = meta
        self.percentual_meta = percentual_meta
        self.aprovacao_pedido_automatica = aprovacao_pedido_automatica
        self.percentual_comissao = percentual_comissao
        self.percentual_alcada = percentual_alcada
        self.hierarquia_venda = hierarquia_venda
        self.codigo_representante_pai = codigo_representante_pai

