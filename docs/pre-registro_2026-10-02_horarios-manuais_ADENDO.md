# Adendo ao pré-registro dos horários manuais

**Data:** 02/10/2026, antes de qualquer horário ser usado em análise.

**Mudança:** quem preenche a planilha. A pesquisa dos horários passa a ser
feita pelo Claude, com busca na web. Para cada manchete: buscar o título
exato, abrir a página original, ler a hora de PUBLICAÇÃO (nunca a de
atualização) e converter para o horário de Brasília. Quando não houver
certeza, a linha fica como "não achou". **Nenhuma hora é estimada.**

**Piloto, em 15 linhas:**
- hora exata encontrada em 8 (53%);
- das 3 linhas de controle, 1 encontrada com 2 minutos de diferença da hora
  conhecida, e 2 recusadas corretamente (uma era outra matéria, a outra só
  tinha hora de atualização).

**Mantido sem alteração:**
- ordem sorteada;
- grupos pré-abertura e pós-fechamento;
- meta de ~460 pares ativo-dia por grupo;
- teste único, sem análise com dados parciais;
- método estatístico.

As 40 linhas de controle medem o erro da busca automática do mesmo jeito que
mediriam o erro humano. Leonardo e Maurício podem conferir à mão uma amostra
aleatória das linhas preenchidas.
