
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
    erp_code: str
    name: str
    cellphone: str
    phone: str
    login: str
    password: str
    supervisor: bool
    temporary_password: bool
    activate_representative: bool
    email: str
    sale_region: SaleRegion
    manager: bool
    goal: int
    goal_percentage: int
    aprovacao_pedido_automatica: bool
    percentual_comissao: int
    percentual_alcada: int
    hierarquia_venda: SaleHierarchy
    codigo_representante_pai: str

    def __init__(self, codigo_externo, nome, telefone_celular, telefone_fixo, login, password, supervisor, senha_temporaria, ativar_representante, email, regiao_venda, gerente, meta, percentual_meta,
                 aprovacao_pedido_automatica, percentual_comissao, percentual_alcada, hierarquia_venda, codigo_representante_pai):
        self.erp_code = codigo_externo
        self.name = nome
        self.cellphone = telefone_celular
        self.phone = telefone_fixo
        self.login = login
        self.password = password
        self.supervisor = supervisor
        self.temporary_password = senha_temporaria
        self.activate_representative = ativar_representante
        self.email = email
        self.sale_region = regiao_venda
        self.manager = gerente
        self.goal = meta
        self.goal_percentage = percentual_meta
        self.aprovacao_pedido_automatica = aprovacao_pedido_automatica
        self.percentual_comissao = percentual_comissao
        self.percentual_alcada = percentual_alcada
        self.hierarquia_venda = hierarquia_venda
        self.codigo_representante_pai = codigo_representante_pai

