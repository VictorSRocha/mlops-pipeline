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
| `...\Serie_Mlops\arquivos_contexto\` | Playbooks, documento mestre, HTML Ep01, artigo Google |
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

## Entregáveis por Episódio

Ao criar um novo episódio, sempre gerar:
1. **Arquivos de código** (.py) com comentários didáticos + testes
2. **Roteiro do episódio** (roteiro-epNN.md + roteiro-epNN-enxuto.md)
3. **HTML pré-episódio** (epNN-apoio-video.html) — abertura visual para o vídeo
4. **HTML de conceitos** (epNN-conceitos.html) — material de estudo completo
5. **Guia interno** (guia-interno-epNN-apoio-video.md) — cola para o apresentador

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
| Roteiro enxuto | `roteiro-epNN-enxuto.md` |
| Guia interno apoio vídeo | `guia-interno-epNN-apoio-video.md` |
| Notebook | `epNN.ipynb` |

> **Nota:** o Ep01 usa `introducao-ep01.html` em vez de `ep01-apoio-video.html` (legado). A partir do Ep02 o padrão correto é seguido.

## Encerramento de Sessão

Quando o Victor disser "vamos encerrar", "terminamos por hoje", ou indicar fim de sessão:
1. Atualizar a memória `progresso-atual.md` com o que foi feito e o que ficou pendente
2. Incluir data, episódio trabalhado, arquivos alterados e próximos passos
3. Confirmar ao Victor o que foi salvo
