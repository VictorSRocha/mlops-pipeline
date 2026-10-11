# CLAUDE.md — Trilha MLOps: Pipeline do Zero ao Fim

## Sobre o Projeto
Trilha de MLOps em 18 episódios (Nível 0 → 1 → 2) baseada no Google MLOps Maturity Model.
**Autor:** Victor Saraiva Rocha · **Case:** Previsão de churn de clientes de streaming
**Stack:** 100% Python, sem serviços pagos · **Portfólio:** https://victorsrocha.github.io/#projetos
Para progresso atual, episódios e mapa de pastas → consultar memórias persistentes.

## Pastas do Projeto

| Pasta | Função |
|-------|--------|
| `C:\mlops-pipeline` (ESTE dir) | Gravação de vídeos / montagem ao vivo. **Sem arquivos de contexto.** |
| `C:\Users\victo\Downloads\Serie_Mlops` | Materiais da série (playbooks, episódios, HTMLs) |
| `...\Serie_Mlops\arquivos_contexto\` | Somente referências: playbooks, documento mestre, artigo Google, texto do portfólio (arquivos de episódio ficam em `nivel_0\mlops-epNN\`) |
| `...\Serie_Mlops\nivel_0\mlops-epNN\` | Arquivos de cada episódio (código, roteiro, HTML, vídeos) |
| `...\Serie_Mlops\imagens\`, `videos\` | **NÃO LER** salvo pedido explícito (pesados) |

## Consulta Obrigatória de Playbooks

Antes de gerar qualquer artefato, **ler o playbook correspondente** em `arquivos_contexto/`:
- Criando código/episódio → ler `playbook-episodios.md`
- Criando HTML de conceitos → ler `playbook-html-conceitos.md`
- Criando página visual pré-episódio → ler `playbook-pre-episodio.md`
- Criando roteiro → ler `playbook-roteiros.md`
- Contexto geral da série → ler `serie-mlops-completa.md`

Nunca gerar um HTML, roteiro ou código de episódio sem antes consultar o playbook relevante.

## Regras de Geração de Código

1. **Sempre incluir comentários e docstrings** em todo arquivo .py criado
2. **Não quebrar o que já existe** — qualquer alteração deve manter testes anteriores passando
3. **Um arquivo por versão** — ao gerar novo arquivo, substituir o antigo; manter apenas o mais atualizado
4. **Mostrar localização** — sempre indicar onde o arquivo deve ser encaixado na estrutura do projeto
5. **Ler antes de editar** — sempre ler o arquivo existente antes de alterá-lo para estar atualizado
6. **Gerar apenas os alterados** — não regenerar arquivos que não mudaram
7. **Imports encadeados** — cada episódio importa dos anteriores; nunca quebrar a cadeia
8. **Instalação por parte** — nos notebooks, cada parte abre com uma célula `!pip install` apenas com os pacotes que o código daquela parte importa (versões do `requirements.txt`)

## Entregáveis por Episódio

Ao criar um novo episódio, sempre gerar:
1. **Arquivos de código** (.py) com comentários didáticos + testes
2. **Roteiro do episódio** (roteiro-epNN.md completo + roteiros por parte `roteiro-epNN-parteM.md`)
3. **HTML pré-episódio** (epNN-apoio-video.html) — abertura visual para o vídeo
4. **HTML de conceitos** (epNN-conceitos.html) — material de estudo completo
5. **Guia interno** (guia-interno-epNN-apoio-video.md) — cola para o apresentador

## Paridade HTML de Conceitos ↔ Notebook

Tudo que o `epNN-conceitos.html` aborda deve ter uma **célula de demo isolada** no notebook do episódio (padrão `demo-*`: conceito → exemplo executável → conexão com o código real).
- Ao criar/alterar o HTML ou o notebook, comparar os dois por parte e preencher o que faltar no lado defasado
- **Não repetir** conceitos já demonstrados em episódios anteriores (consultar `episodios-nivel-N` e notebooks anteriores); nesses casos, apenas citar "visto no EpNN" no HTML
- Conceitos só embutidos em uma classe/função (sem demo isolada) contam como faltantes

## Identidade Visual dos HTMLs

Seguir exatamente o estilo do portfólio `victorsrocha.github.io`:
- Fontes: `Syne` (display) + `DM Sans` (corpo)
- Background: `#0b0f1a`
- Cards: `#111827` com borda `rgba(255,255,255,0.07)`
- Accent primário: `#3b82f6` (azul elétrico)
- Accent secundário: `#06b6d4` (ciano)
- Texto principal: `#e8eaf0`

## Padrão de Demonstração de Erros

Toda falha demonstrada no episódio deve ter:
- **No roteiro:** 4 atos (provoque → explique → corrija → confirme)
- **No HTML:** um `error-demo-card` correspondente
- **Script fake_*.py** para cada sistema externo simulado

## Continuidade entre Episódios

- Mesmo dataset de churn em todos os 18 episódios
- Mesma estrutura de pastas — nunca reorganizar
- Testes anteriores devem continuar passando
- `dvc.yaml` atualizado com novos estágios a cada episódio

## Nomenclatura Padrão de Arquivos

| Artefato | Nome padrão |
|----------|-------------|
| HTML de conceitos | `epNN-conceitos.html` |
| Página visual pré-episódio | `epNN-apoio-video.html` |
| Roteiro completo | `roteiro-epNN.md` |
| Roteiro de fala por parte | `roteiro-epNN-parteM.md` |
| Guia interno apoio vídeo | `guia-interno-epNN-apoio-video.md` |
| Notebook | `epNN.ipynb` |

> **Nota:** o Ep01 usa `introducao-ep01.html` em vez de `ep01-apoio-video.html` (legado). A partir do Ep02 o padrão correto é seguido.

## Gestão de Memória

### Limites
- Máximo **~12 arquivos** de memória. Nunca criar arquivo por sessão ou por episódio individual.
- Cada arquivo deve caber em **~30 linhas** (excluindo frontmatter). Se crescer além disso, sanitizar.

### Princípio: foto do estado atual, não diário
Cada memória registra **o estado corrente**, não o histórico. O git já versiona os arquivos — o passado fica nos commits, não na memória.

### Regras de sanitização (aplicar a cada atualização)
1. **Substituir, não acumular** — ao atualizar `progresso-atual`, sobrescrever com o estado novo; não adicionar ao que tinha.
2. **Uma linha por item** — `episodios-nivel-N` tem 1 linha por episódio com status atual; notas detalhadas de sessões anteriores são descartadas.
3. **Remover o resolvido** — problemas corrigidos, decisões já aplicadas no código e informações temporárias saem na próxima atualização.
4. **Deletar o obsoleto** — se uma memória inteira perdeu relevância (ex: uma regra que mudou completamente), deletar o arquivo e remover do MEMORY.md.
5. **Não duplicar o que o CLAUDE.md já diz** — memórias guardam contexto e porquês; regras de ação ficam no CLAUDE.md.

### Categorias fixas de memória
| Categoria | Arquivo | Atualização |
|---|---|---|
| Perfil do usuário | `user-profile` | Raro |
| Visão geral do projeto | `trilha-mlops-overview` | Raro |
| Estrutura de pastas | `estrutura-pastas` | Quando mudar pastas |
| Progresso | `progresso-atual` | Toda sessão (sobrescrever) |
| Playbooks | `playbooks-serie` | Raro |
| Contexto das regras | `regras-codigo` | Quando regras mudarem |
| Mapa de episódios | `episodios-nivel-N` | Quando status de ep mudar |
| Repositórios GitHub | `github-repos` | Quando config mudar |

## Encerramento de Sessão

Quando o Victor disser "vamos encerrar", "terminamos por hoje", ou indicar fim de sessão:
1. **Sanitizar e atualizar** `progresso-atual.md` — sobrescrever com estado corrente, não acumular
2. Incluir: data, episódio trabalhado, o que foi feito, próximos passos
3. Atualizar mapa do episódio em `episodios-nivel-N.md` se status mudou
4. Confirmar ao Victor o que foi salvo
5. **Lições aprendidas** — executar a seção abaixo antes de dar a sessão por encerrada

## Lições Aprendidas (obrigatório ao encerrar e após correções relevantes)

Antes de encerrar, revisar a sessão e perguntar: *o que descobrimos que não estava escrito em lugar nenhum?* Para cada lição, registrar **no lugar certo** (uma vez só, sem duplicar):

| Tipo de lição | Destino |
|---|---|
| Regra de ação que deve valer sempre (como fazer / não fazer) | `CLAUDE.md` |
| Boa prática de produção de roteiro / HTML / código de episódio | o `playbook-*.md` correspondente em `arquivos_contexto/` |
| Contexto, porquê, preferência do Victor, estado do projeto | memória da categoria existente (respeitar o limite de ~12 arquivos) |
| Procedimento repetido 2+ vezes, com passos fixos | propor uma **skill** nova |

Regras:
1. **Listar as lições ao Victor e pedir confirmação** antes de gravar em `CLAUDE.md`, playbooks ou criar skill. Memórias podem ser atualizadas direto.
2. **Atualizar antes de criar** — se já existe regra/memória sobre o assunto, editar a existente.
3. **Corrigir a causa, não só o sintoma** — se um bug revelou uma lacuna (ex.: falta de teste), a lição inclui o teste/checagem que a cobre.
4. **Descartar o que é só desta sessão** — o que o git já registra não vira lição.

### Checklist de validação antes de gravar um episódio
**Ao criar ou alterar roteiro, notebook, HTML ou código de episódio, invocar a skill `validar-episodio` antes de dar o trabalho como entregue** — ela executa o procedimento abaixo (inclui a auditoria da seção 1.4 do `playbook-roteiros.md` e a paridade HTML ↔ notebook ↔ roteiro). O checklist resume o que ela cobre:

1. Rodar `pytest` do episódio (todos passando) e **executar o notebook célula a célula** — sem saídas de erro.
2. Comparar HTML de conceitos ↔ notebook ↔ roteiro por parte (paridade; ver seção acima).
3. **Rodar o que o roteiro/HTML afirma** — explicações técnicas (ex.: "o dict seria compartilhado") devem ser verificadas executando o código, não apenas lendo.
4. Testar o caso de borda "vazio / sem novidades" de cada coletor (ex.: um ciclo sem dados novos não pode corromper o watermark).
5. Código de apoio (`fake_*.py`, `generate_*.py`) validado contra o coletor real e sincronizado entre `Serie_Mlops` e os repos.
6. Roteiros são **texto de fala** (sem tom de conversa/chat, sem referência à sessão de edição).
7. Só então: commit e push (código → `mlops-pipeline`; roteiros/HTMLs/playbooks → `trilha-mlops-conteudo`).
