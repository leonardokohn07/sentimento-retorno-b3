# Pré-registro — Fase F: trocar o léxico por um modelo de linguagem?

**Data:** 02/10/2026, escrito **antes** de rodar qualquer modelo sobre as
manchetes. Nenhum escore de modelo existe ainda no projeto.

**O que já se sabia ao escrever:** o resultado preliminar da Fase E. Contra o
consenso de dois anotadores automáticos, o léxico tem kappa 0,39 (razoável),
acurácia reponderada de 61%, e quase nunca troca o sinal. O erro típico dele é
com o neutro.

## Pergunta

Um modelo de linguagem treinado mede o sentimento das manchetes melhor que o
léxico? E, se medir, as conclusões do estudo mudam quando se usa a medida
melhor?

## Candidatos (fixados agora)

| | Medida | Papel |
|---|---|---|
| L | Léxico atual (`score_polaridade`, limiar ±0,15) | referência |
| F | **FinBERT-PT-BR** (`lucas-leme/FinBERT-PT-BR`, Hugging Face), BERT em português ajustado para o mercado financeiro brasileiro | **candidato principal** |
| D | Modelo já previsto no código (`lxyuan/distilbert-base-multilingual-cased-sentiments-student`, usado pelo `AnalisadorV2` quando disponível), multilíngue e genérico | secundário |
| H1 | Híbrido do código: 0,5 × léxico + 0,5 × D, limiar ±0,15 (é o que o `AnalisadorV2` faria) | secundário |
| H2 | Híbrido 0,5 × léxico + 0,5 × F, limiar ±0,15 | secundário |

- **Entrada dos modelos:** a manchete sem o " - Nome do Jornal", o mesmo
  texto que os anotadores leram.
- **Saída:** probabilidade de positivo, negativo e neutro. Classe = a de maior
  probabilidade. Escore contínuo = P(positivo) − P(negativo), de −1 a +1.
- **Rótulos:** o mapeamento segue o `config.json` e o cartão oficial de cada
  modelo, salvos em `dados/modelos/` no momento do download.

## Validação

- **Amostra e referência:** as 300 manchetes da Fase E e o consenso dos
  anotadores. Hoje, os dois automáticos. Depois, Leonardo e Maurício.
- **Métrica principal:** kappa de Cohen **reponderado para a população**. A
  amostra foi estratificada pela classe do léxico, então cada manchete pesa
  (peso da classe na população) / (número de manchetes daquela classe na
  amostra). Sem isso, a comparação ficaria presa ao desenho da amostra.
- **Métricas de apoio:** acurácia reponderada, precisão e recall por classe,
  Spearman entre o escore contínuo e o rótulo (−1, 0, +1).

## Regra de decisão (fixada agora)

- **O FinBERT-PT-BR substitui o léxico como medida principal das análises
  NOVAS se:**
  - o kappa reponderado dele for maior que o do léxico; **e**
  - o IC 95% da diferença (FinBERT − léxico) ficar inteiro acima de zero.
    O IC vem de bootstrap pareado e estratificado, com 10.000 reamostragens e
    semente 42.
- **Candidatos secundários (D, H1, H2):** são reportados com a mesma métrica,
  mas não são adotados sem confirmação na rotulagem humana. Escolher o melhor
  entre vários na mesma amostra favorece o vencedor por sorte.
- **Confirmação:** quando a rotulagem humana estiver pronta, a mesma
  comparação é refeita. Se ela contrariar a decisão (IC da diferença incluir
  zero ou inverter), a decisão é revista e isso é reportado.

## O que acontece com os resultados já reportados

**Nada é substituído.** Os testes pré-registrados com o léxico continuam
valendo como estão.

**Robustez (pré-registrada agora).** Os testes abaixo rodam de novo com o
escore contínuo do FinBERT no lugar do léxico. Métodos, janelas e permutações
ficam idênticos. A versão com léxico roda junto, no mesmo computador e com os
mesmos dados, para a comparação ser justa.

- **R1:** família principal da fase causal (P1 a P9, Holm) e secundárias.
- **R2:** análise adicional A1 (P2 a P5, S4, S5).
- **R3:** resultado original do estudo: D−1, D+0 e D+1 por ativo, como em
  `congelar_resultados.py`.

R1 a R3 rodam **mesmo que a regra não adote o FinBERT**. Nesse caso, são
lidos como "medida alternativa, não melhor".

**Previsão (escrita antes de ver):**
- Se o ruído do léxico atenuava as correlações, com o FinBERT elas devem
  crescer em módulo, no mesmo sentido.
- A assimetria deve se manter: preço → notícia (P3/P5 e A1-P3/A1-P5)
  positivo, e notícia → preço (P1, P2, P4, P9) nulo.

**Leitura:**
- **"Conclusão mantida":** P8 continua positivo e significativo; na A1, P3
  ou P5 positivo com p < 0,05; e P2 e P4 sem significância.
- **"Conclusão muda":** P2 ou P4 positivo e significativo (Holm em R1, ou
  p < 0,05 na A1). Nesse caso, a relação passa a ser descrita como
  bidirecional, com a força de cada direção.

## O que não será feito

- Escolher a medida olhando a correlação com retorno. A escolha usa **só** a
  validação contra rótulos e é feita antes de R1 a R3.
- Trocar candidato, regra, métrica, limiar ou texto de entrada depois de ver
  os resultados.
- Esconder candidato que perdeu ou teste que deu nulo.
