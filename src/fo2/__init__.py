__version__ = '0.1.121'
__version__date__ = '11/09/2018'

# histórico
#
# - ?.?.??? - 20??/??/??
#
# - 0.1.121 - 2018/09/11
#   . Produção : Tela de perdas
#   . Produção : Tela de conserto melhorada
#
# - 0.1.120 - 2018/09/04
#   . Command : Indexando lotes do Fo2 e melhorando output de commands que
#               atualizam essa tabela.
#               Melhoria de performance do command de sincronização de NF.
#
# - 0.1.119 - 2018/08/24
#   . Remessa : Total por cor; Total geral de peças
#   . OS : Sem lotes não aparecia
#
# - 0.1.118 - 2018/08/21
#   . Produto : Detalha roteiros por cor / tamanho
#   . Produto : Diversas melhorias
#   . Remessas para industrialização: Novos filtros
#
# - 0.1.117 - 2018/08/20
#   . Produto : Alternativas e roteiros: preve alternativas por cor
#
# - 0.1.116 - 2018/08/16
#   . Produto : Estruturas: Correções de visualizão
#   . Produto e OP: Diversos links adicionados entre telas
#
# - 0.1.115 - 2018/08/13
#   . CD : inventariar: Também permite movimentar lotes no 66 no systêxtil
#
# - 0.1.114 - 2018/08/10
#   . Produto: Melhoria na apresentação da estrutura
#   . OP: Grades de produtos componentes de OP
#
# - 0.1.113 - 2018/08/09
#   . Produto: Na busca de produto, pode buscas por cor e, se o fizer,
#              apresenta a cor
#   . CD : Também permite movimentar lotes finalizados
#
# - 0.1.112 - 2018/08/08
#   . CD: Só inventaria lotes que estejam nos estágios 57 ou 63
#
# - 0.1.111 - 2018/08/06
#   . RH: Melhorias em aniversariantes
#   . RH: mais 1 dica
#
# - 0.1.110 - 2018/08/02
#   . OP: Tela que apresenta todos os produtos em conserto.
#   . CD: Em inconsistências indica se OP do lote estocado está cancelada
#
# - 0.1.109 - 2018/08/02
#   . OP: Acertar grades de OP (considerando lotes adicionados)
#   . OP: Grades de produtos componentes de OP
#   . Contábil: Descr. Cliente (infAdProd)
#
# - 0.1.108 - 2018/08/01
#   . Produto: apresentando os vários componentes produto de uma alternativa
#   . OP: Busca OP
#
# - 0.1.107 - 2018/07/24
#   . Insumos
#     . Mapa de compra por semana
#       - acertados valores considerando lead time
#       - acertando lote múltiplo
#
# - 0.1.106 - 2018/07/24
#   . Insumos
#     . Mapa de compra por semana - Primeira candidada a versão final
#
# - 0.1.105 - 2018/07/23
#   . Insumos
#     . Mapa de compra por semana - Primeira versão funcional
#     . Rolo: Mostra OP associada
#
# - 0.1.104 - 2018/07/19
#   . Painel: Limitando imput em edição chamada de informativo
#
# - 0.1.103 - 2018/07/12
#   . Fo2: Muitas correções de namespace
#
# - 0.1.102 - 2018/07/10
#   . Insumos
#     . Mapa de compra - Apresentando também necessidades das previsões
#
# - 0.1.101 - 2018/07/09
#   . Insumos
#     . Mapa de compra - Cálculo de Necessidades semanais estava errado
#     . Detalhe de necessidade de insumo em uma semana - Diversas melhorias de
#       layout
#     . Recebido - Diversas melhorias de layout
#
# - 0.1.100 - 2018/06/29
#   . OP - Mostrando grades atuais de OP ignorando a grade inicial, pois podem
#          ter sido adicionados novos lotes
#
# - 0.1.99 - 2018/06/29
#   . RH - Atualizações
#   . Comandos utilitários
#
# - 0.1.98 - 2018/06/19
#   . insumos/Previsão - Diversos desenvolvimentos
#
# - 0.1.97 - 2018/06/05
#   . CD - Histórico simples de OP no CD
#
# - 0.1.96 - 2018/05/29
#   . RH - Fotos e vídeos SIPAT 2018
#   . Pedido - Apresentando também data de embarque e observação
#   . OP - Responsáveis e datas de movimentações de estágios
#
# - 0.1.95 - 2018/05/28
#   . CD - Visualizando o estoque em grades de
#          . inventário
#          . solicitações
#          . disponível
#
# - 0.1.94 - 2018/05/25
#   . Produção - Distribuição de lotes - primeira versão
#   . CD - Verifica endereço de lote
#
# - 0.1.93 - 2018/05/24
#   . Estoque - Sempre apresenta quantidade disponível para solicitar
#             - adicionado link para detalhamento de solicitação
#
# - 0.1.92 - 2018/05/23
#   . Detalhe de solicitação - Melhor apresentação das grades
#   . Solicitações - Ao ativar uma solicitação as outras do mesmo usuário são
#     desativadas
#   . Solicitações - Não reposiciona tela ao solicitar lote
#   . Detalhe de solicitação - Mantém aba em refresh
#   . Detalhe de solicitação - Grades com totalizadores
#
# - 0.1.91 - 2018/05/17
#   . CD estoque - Solicitação: Funcionando solicitação de qtd de lote
#   . CD estoque - Solicitação: Tela com detalhes de uma solicitação inidiada
#     e funcional
#
# - 0.1.90 - 2018/05/15
#   . CD estoque: Iniciada rotina de solicitação de lotes
#   . Lista de caixas de lotes: Corrigida
#   . CD estoque: show/hide filtro
#   . CD estoque: Tela de conferencia de endereços 63
#
# - 0.1.89 - 2018/05/11
#   . CD Estoque: Paginação
#   . Utilitários: Comando para corrigir sequancias zeradas de estágios
#     de lotes
#
# - 0.1.88 - 2018/05/10
#   . Responsável por estágio: Mais detalhes
#   . RH: Vários
#   . Lotes sincronizados: Estágio e quantidade atuais
#
# - 0.1.87 - 2018/05/04
#   . CD - Detalhes de Inconsistência: Melhorias
#
# - 0.1.86 - 2018/05/03
#   . CD: Inconsistências Systêxtil
#   . CD: Primeira versão de Detalhes de Inconsistência
#   . CD: Iniciando (não funcional) mapa e conferencia de endereços
#
# - 0.1.85 - 2018/04/27
#   . Lotes sincronizados: Problema com log de alterações
#   . CD: Rotina de inventário de lotes também pode ser utilizada para retirar
#         lotes do CD
#
# - 0.1.84 - 2018/04/27
#   . CD - troca endereço de lote no 63-CD
#   . CD - estoque 63: Filtro por data
#
# - 0.1.83 - 2018/04/26
#   . CD: Melhorias nas telas de inventário e de pesquisa no estoque 63
#
# - 0.1.82 - 2018/04/25
#   . primeira versão funcional de Relatório de remessa para industrialização
#
# - 0.1.81 - 2018/04/20
#   . Insumos: Tela de bipar rolo
#   . Acompanhamento de NF: Melhora nos filtros e dados mostrados
#
# - 0.1.80 - 2018/04/19
#   . CD - estoque: Primeira versão funcional de pesquisa de estoque de 63-CD
#
# - 0.1.79 - 2018/04/18
#   . CD: Primeira versão funcional de rotina de inventário de lotes,
#         com endereço
#
# - 0.1.78 - 2018/04/17
#   . Util: Command para importar lotes
#
# - 0.1.77 - 2018/04/16
#   . CD: iniciando rotina de inventário de lotes, com endereço
#
# - 0.1.76 - 2018/04/16
#   . Posição de lote: nova visualização (ainda e evolução)
#
# - 0.1.75 - 2018/04/12
#   . OP: Corrigindo totais de 2a. qualidade
#   . Busca de produto: Por cliente
#   . Posição de lote: Mostra quantidade em conserto
#
# - 0.1.74 - 2018/04/10
#   . Necessidade de insumos de Previsão de produção passou a ser link em
#     Previsão de produção
#
# - 0.1.73 - 2018/04/09
#   . Previsão de produção: Tela que apresenta previsão já distribuida pelas
#     cores e tamanhos
#   . Necessidade de insumos de Previsão de produção
#
# - 0.1.72 - 2018/04/03
#   . Caixas: Iniciando rotina de controle de caixas.
#
# - 0.1.71 - 2018/03/28
#   . RH: Páscoa.
#
# - 0.1.70 - 2018/03/27
#   . Mapa de compras: Correção no calculo de necessidades.
#   . OP: Mostra grade de perdas e de segunda qualidade
#
# - 0.1.69 - 2018/03/26
#   . OP por período e alternativa: ajustes de apresentação
#   . OP por data de corte e alternativa: ajustes de apresentação
#   . Mapa de compras: Detalhe de necessidade de insumo em uma semana
#
# - 0.1.68 - 2018/03/23
#   . Mapa de compras: insumo já enviado para facção não conta como necessidade
#   . Impressão de etiquetas de lote: Parou de utilizar a narrativa da nota e
#     passou a utilizar a narrativa montada na hora com as descrições de
#     referencia, tamanho e cor.
#   . Impressão de etiquetas de lote: apresenta a narrativa ma tela
#
# - 0.1.67 - 2018/03/22
#   . Mapa de compras: Corrigido o cálculo do estoque
#   . Mapa de compras: Corrigido o sugestão de compras'
#   . Mapa de compras: Mostrando sugestão ideal
#
# - 0.1.66 - 2018/03/21
#   . Insumo: Primeira versão completa do Mapa de compras por insumo
#
# - 0.1.65 - 2018/03/20
#   . Intranet: Link para GS1
#
# - 0.1.64 - 2018/03/16
#   . Insumo: Insumos para mapa de compras
#   . Insumo: Iniciano Mmapa de compras
#
# - 0.1.63 - 2018/03/14
#   . Insumo: Tela de A Receber - melhorias
#   . Insumo: Tela de Estoque - melhorias
#
# - 0.1.62 - 2018/03/13
#   . POPs - Controle de usuário por permissões
#   . login no cabeçalho
#   . Necessidade: Adicionado filtros de periodo de corte e
#                  de periodo de compra
#   . Insumo: Tela de A Receber
#   . Insumo: Tela de Estoque
#
# - 0.1.61 - 2018/03/12
#   . Ajustes nas páginas do RH
#   . Uploda dos POPs
#
# - 0.1.60 - 2018/de03/02
#   . Várias melhorias
#
# - 0.1.50 - 2018/01/29
#   . Várias melhorias
#
# - 0.1.40 - 2017/12/01
#   . Pedido: grade de itens pedidos
#
# - 0.1.39 - 2017/11/30
#   . App RH
#   . Impressão de cartelas de lote melhorada
#   . Toda rotina de bipagem para inventário de rolos e geração de arquivo
#     de inventário para o Systêxtil
#
# - 0.1.38 - 2017/11/17
#   . Alteração de layout e algumas ULRs
#   . Adição de link de base de conhecimento
#
# - 0.1.37 - 2017/11/13
#   . Abrindo Systêxtil sem ajuda de página externa (funcionando também de fora
#     da Tussor)
#
# - 0.1.36 - 2017/11/09
#   . OP: Prevendo OP com mais de uma finha na informações básicas
#   . OP e OS: acertando quantidades apresentadas - considerando perda e etc.
#
# - 0.1.35 - 2017/11/08
#   . Pedido: Situação da venda
#   . OP e OS: Link para pedido
#   . Pedido: OPs
#
# - 0.1.34 - 2017/11/08
#   . OP pendente: filtro por coleção
#
# - 0.1.33 - 2017/11/07
#   . Conferência de pedido: melhorias
#   . Pedido: Inicio de desenvolvimento
#
# - 0.1.32 - 2017/11/06
#   . OP + número de pedido e pedido de cliente
#   . renomeando páginas da intranet
#   . Melhorias em várias telas
#
# - 0.1.31 - 2017/10/18
#   . Ordens pendentes por estágio
#   . Melhorias em várias telas
#
# - 0.1.30 - 2017/09/29
#   . Primeira rotina de impressão térmica
#     . Impressão de etiqueta de lote
#
# - 0.1.29 - 2017/09/26
#   . Produto: links para insumos
#   . Insumo: adicionada informação de "Usado em"
#     . links para produtos
#
# - 0.1.28 - 2017/09/26
#   . Layout: alterações
#   . Insumo: Início da APP
#
# - 0.1.26 - 2017/09/12
#   . OP: depósitos destino da produção
#
# - 0.1.25 - 2017/09/12
#   . gravando log de alterações na tabela RecordTracking
#
# - 0.1.24 - 2017/09/11
#   . criando log de alterações em registros de tabelas
#   . Criada tabela RecordTracking para guardar log de alterações
#   . OP: adicionando quat. de 2a. qualidade e perda ao resumo por estágio
#   . App Utils para Classes, Middlewares e outras coisas uteis para
#     vários Apps
#
# - 0.1.23 - 2017/08/30
#   . adição de varios links para referência
#   . criação de view de modelo
#
# - 0.1.22 - 2017/08/29
#   . ajustes de layout (finalizado)
#
# - 0.1.21 - 2017/08/28
#   . view de referências - continuando
#   . ajustes de layout (iniciando por produto / ref e contagem)
#
# - 0.1.20 - 2017/08/25
#   . view de referências (produtos confeccionados)
#   . Layout:
#     . sem bordas
#     . eliminando footer
#     . não imprime href link
#
# - 0.1.19 - 2017/08/08
#   . refactoring de lotes.models
#   . análise de produzido
#     . qtd por período e alternativa
#     . qtd por data de corte e alternativa
#
# - 0.1.18 - 2017/08/04
#   . OP: datas
#
# - 0.1.17 - 2017/08/04
#   . OS: datas, observação, insumos
#
# - 0.1.16 - 2017/08/03
#   . estatística de produto: prevendo PG
#   . OS: retornos, datas
#
# - 0.1.15 - 2017/08/01
#   . OS: lotes
#   . Posição de lote: OSs
#   . OP: Mais informações
#
# - 0.1.14 - 2017/07/31
#   . Posição de lote: Mais informações
#   . OP: Mais informações
#   . OS: Iniciando busca de informações de OS
#
# - 0.1.13 - 2017/07/20
#   . ficha de cliente: pequena correção e melhoria
#   . visualização de OP:
#     . links para lotes
#     . situação de OP
#     . OP relacionada
#   . posição de lote:
#     . GET
#     . apresentando como tipo (MD, PG, PA), ref., cor e tam.
#     . link para OP
#
# - 0.1.12 - 2017/07/12
#   . controle de data de saída:
#     . transportadora
#     . ajustes de tela
#
# - 0.1.11 - 2017/07/11
#   . melhorias na consulta de OP
#   . adicionados campos à tela de controle de data de saída
#
# - 0.1.10 - 2017/07/10
#   . Evoluindo controle de data de saída
#   . Evoluindo dados de pedido para conferencia
#     Era só infAdProd, adicionei EAN e Narrativa
#
# - 0.1.9 - 2017/07/07
#   . controle de data de saída: Mais informações
#
# - 0.1.8 - 2017/07/06
#   . iniciando app logística
#   . controle de data de saída
#
# - 0.1.7 - 2017/07/05
#   . ficha de cliente (consultando F1)
#
# - 0.1.6 - 2017/06/30
#   . consulta infAdProd por número de pedido
#
# - 0.1.5 - 2017/06/29
#   . corrigido bug em view de OP
#   . posição de lote reescrita - vira classe
#   . responsáveis aparece estágio sem responsável
#   . autofocus nos forms
#
# - 0.1.4 - 2017/06/23
#   . menus reestruturados
#   . posição de lote reescrita - tira ajax e utiliza models
#
# - 0.1.3 - 2017/06/16
#   . consulta de OP: lotes por estágios, por OS e individuais
#   . lista produtos nível 1 sem preço médio
#
# - 0.1.2 - 2017/06/14
#   . consulta de responsável por estágio
#   . mostra cadastro de estágios
#   . em Produtos, mostra tamanhos e cores
#   . em Produtos, nível 1, mostra alternativas e roteiros
#
# - 0.1.1 - 2017/06/12
#   . melhorias na visualização das informações do lote
#   . mostra cadastro de depósitos
#
# - 0.1.0 - 2017/06/07
#   . primeira versão divulgada
#   . estatística de produtos
