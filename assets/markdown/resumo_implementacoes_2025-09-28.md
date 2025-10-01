# Resumo do que foi implementado hoje (28/09/2025)

Este documento descreve, de ponta a ponta, tudo que foi desenvolvido e ajustado hoje na tela de disponibilidade para extras e regras de cálculo associadas.

- Arquivo principal: `screens/disponibilidade_extras_screen.py`
- Classe: `DisponibilidadeExtrasScreen`
- Método principal: `get_content()`
- Funções relevantes:
  - `calcular_disponibilidade(opcao, interticio_label)`
  - `render_tabela(linhas)`

## Fluxo geral
A funcionalidade permite consultar quantas vagas de extra existem por data e turno, considerando uma série de regras de presença/ausência e ajustes 24h. Há duas opções no dropdown: `Rotina` e `OBLL`.

## OBLL
- Capacidade fixa de 2 vagas por dia.
- Busca em `extras` com `operacao = 'OBLL'` e intertício selecionado (entre as datas do intertício) para saber quantas já estão ocupadas.
- Retorna as vagas restantes (máximo 2).

## Rotina – Regras por etapas (Etapas 1 a 8)
O cálculo percorre todas as datas do intertício e aplica as regras na ordem abaixo. Todas as etapas possuem prints de debug no console para auditoria.

### Etapa 1 – Base por equipe
- Para cada data, obtém a `equipe` em `calendario` (campo `equipe`).
- Conta os policiais da `equipe` na tabela `policiais` com filtro adicional: `unidade = 'NUVIG'`.
- Esse total é a base de presentes 24h (somam para diurno e noturno).
- Debug: imprime a equipe do dia e a lista de QRA/Nomes considerados na base.

### Etapa 2 – Licenças
- Consulta a tabela `licencas` juntando com `policiais` e filtra:
  - `p.escala = equipe` e `p.unidade = 'NUVIG'`.
  - `date(data_atual)` entre `[inicio, fim]` da licença.
- O total encontrado é subtraído da base (base_presentes).
- Debug: imprime a lista de QRA/Nomes em licença na data.

### Etapa 3 – Férias (3 períodos)
- Consulta a tabela `ferias` (colunas `inicio1/fim1`, `inicio2/fim2`, `inicio3/fim3`) juntando com `policiais` e filtra:
  - `p.escala = equipe` e `p.unidade = 'NUVIG'`.
  - `date(data_atual)` dentro de qualquer um dos 3 intervalos.
- O total encontrado é subtraído da base.
- Debug: imprime a lista de QRA/Nomes em férias.

### Etapa 4 – Compensações (24h)
- Tabela: `compensacoes (policial_id, compensacao, a_compensar)`
- Regras:
  - Na data `compensacao`: adiciona +24h (entra na presença), filtrando `p.unidade = 'NUVIG'`.
  - Na data `a_compensar`: remove −24h somente se o policial seria do plantão (mesma `equipe`), filtrando `p.unidade = 'NUVIG'`.
- Debug: lista QRA/Nomes adicionados (+24h) e removidos (−24h).

### Etapa 5 – Permutas (24h)
- Tabela: `permutas (solicitante, permutado, data_solicitante, data_permutado)`
- Regras:
  - Quando `data == data_permutado`: entra o `solicitante` (+24h). Sai o `permutado` (−24h) se estaria de plantão na `equipe` do dia (com `unidade='NUVIG'`).
  - Quando `data == data_solicitante`: entra o `permutado` (+24h). Sai o `solicitante` (−24h) se estaria de plantão na `equipe` do dia (com `unidade='NUVIG'`).
- Em teoria, permutas mantêm o total estável, mas o sistema registra a troca (para depuração e rastreabilidade).
- Debug: listas de QRA/Nomes adicionados e removidos pela permuta.

### Etapa 6 – Acordo de conduta (24h)
- Tabela: `conduta (policial_id, data)`
- Na data indicada, policiais de `unidade='NUVIG'` recebem +24h (somam em diurno e noturno).
- Debug: lista de QRA/Nomes adicionados por conduta.

### Etapa 7 – Extras por turno (Rotina)
- Tabela: `extras (policial_id, data_id, turno, operacao, interticio, ...)` com JOIN em `calendario` para obter a data real a partir de `data_id`.
- Regras:
  - Apenas `operacao = 'Rotina'`.
  - Se `turno = 'Diurno'`: soma ao diurno daquela data.
  - Se `turno = 'Noturno'`: soma ao noturno daquela data.
- Importante: por solicitação, nesta etapa o filtro de `unidade = 'NUVIG'` NÃO é aplicado (apenas aqui).
- Debug: listas de QRA/Nomes por turno e contagem.

### Etapa 8 – Remoção de "Administrativo"
- Após aplicar todas as adições, remove da contagem policiais cuja `funcao = 'Administrativo'`, respeitando a origem de onde foram adicionados:
  - Se vieram da base: decrementa a `base_ajustada`.
  - Se vieram de ajustes 24h: decrementa de `ajustes_24h_total`.
  - Se vieram de extras diurno/noturno: decrementa de `extras_diurno` ou `extras_noturno`.
- Não remove novamente quem já foi removido por ausência (licença/férias/compensações −24h/permutas −24h).
- Debug: imprime QRA/Nomes removidos em cada categoria (Base, +24h, Extras D, Extras N).

### Consolidação de totais e vagas
- Após aplicar base, ausências, ajustes 24h e extras por turno (e remoções administrativas), o código computa:
  - `presentes_diurno = base_ajustada + ajustes_24h_total + extras_diurno`
  - `presentes_noturno = base_ajustada + ajustes_24h_total + extras_noturno`
  - Vagas:
    - `diurno`: `max(0, 11 - presentes_diurno)`
    - `noturno`: `max(0, 14 - presentes_noturno)`
- As linhas retornadas incluem apenas as datas/turnos com vagas > 0.

## Prints de debug
- Todas as etapas imprimem o detalhamento de quem foi considerado em cada categoria, além dos totais por data:
  - Etapa 1: equipe e lista da base (NUVIG).
  - Etapas 2 e 3: listas de ausências (licenças, férias).
  - Etapas 4, 5 e 6: ajustes 24h (compensações, permutas, conduta) – adicionados e removidos.
  - Etapa 7: extras por turno.
  - Etapa 8: removidos por `funcao='Administrativo'` (QRA/Nome).
  - Totais: Base, ausências, base ajustada, ajustes 24h por origem, extras por turno e disponíveis vs necessários.

## UI/UX – Ajustes visuais da tabela
- A tabela foi centralizada horizontalmente e limitada a 800px de largura:
  - `ListView` dentro de `ft.Container(width=800, alignment=ft.alignment.center)`.
  - `ListView(width=800, height=500, expand=False)` para permitir rolagem.
- As colunas foram distribuídas igualmente (200px cada) para melhor apresentação:
  - Data (200), Tipo (200), Turno (200), Quantidade (200).
- Dropdowns com `bgcolor=ft.Colors.WHITE`.

## Observações e decisões
- O filtro `unidade = 'NUVIG'` foi aplicado para a base (Etapa 1), licenças, férias, compensações e permutas (na remoção por estar de plantão). Foi removido apenas para a Etapa 7 (extras por turno), conforme solicitado.
- As queries lidam com possíveis retornos como dicionário ou tupla.
- Robustez: todas as consultas estão em blocos `try/except` com logs de erro.

## Possíveis melhorias futuras
- Header fixo ao rolar a listagem.
- Linhas zebradas na tabela e estado vazio estilizado.
- Exportação do relatório em PDF diretamente daqui (há um botão `Exportar PDF` já preparado como placeholder).
- Configurar capacidades (11/14) por unidade/equipe via tabela de parâmetros.

---
Documento gerado automaticamente a partir das implementações em `screens/disponibilidade_extras_screen.py` em 28/09/2025.
