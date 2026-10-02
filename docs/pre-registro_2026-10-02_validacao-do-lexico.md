# Pré-registro — validação do léxico de sentimento (Fase E)

**Data:** 02/10/2026, escrito antes de qualquer rótulo ser feito.

## Pergunta

O escore do léxico concorda com o sentimento que uma pessoa (ou um anotador
cuidadoso) atribuiria à manchete, do ponto de vista do acionista da empresa?

## Amostra

- **Estratificada por classe do léxico:** 100 manchetes "Positivo", 100
  "Negativo" e 100 "Neutro", sorteadas (semente 42) entre os pares únicos
  (ativo, manchete) de 2024-2026 dos 8 ativos.
- **Por que estratificar:** na população, 70% das manchetes são "Neutro".
  Uma amostra aleatória simples teria poucas positivas e negativas para medir
  a precisão dessas classes.
- **Estimativas da população:** são reponderadas pelos pesos reais das
  classes (Neutro 70,4%, Positivo 18,3%, Negativo 11,3%).
- **Ordem:** a planilha de rotulagem vem embaralhada e **sem** o escore do
  léxico.

## Anotadores

1. **Dois anotadores automáticos** (Claude, duas rodadas independentes, sem
   ver o escore e com o mesmo protocolo escrito). Isso **não substitui
   humanos**: é um terceiro avaliador e uma checagem preliminar.
2. **Leonardo e Maurício:** rotulam a mesma planilha, cada um no seu arquivo,
   sem ver os rótulos do outro nem os do Claude.

## Protocolo de rotulagem (igual para todos)

- **positivo:** a notícia é boa para os acionistas da empresa indicada.
- **negativo:** é ruim para os acionistas.
- **neutro:** é informativa sem direção clara, irrelevante para a empresa, ou
  ambígua.
- Julgar **só pelo texto da manchete**, sem usar conhecimento do que
  aconteceu com a ação depois.

## Métricas (fixadas agora)

- Concordância entre anotadores: kappa de Cohen, 3 classes.
- Léxico × consenso dos anotadores:
  - acurácia na amostra e reponderada para a população;
  - precisão de cada classe do léxico;
  - kappa de Cohen;
  - matriz de confusão;
  - correlação de Spearman entre o escore contínuo e o rótulo (−1, 0, +1).
- **Consenso:** quando os dois anotadores concordam. As discordâncias são
  reportadas e ficam fora da comparação principal. Sensibilidade: tratá-las
  como "neutro".

**Leitura do kappa** (Landis; Koch, 1977): < 0,20 fraca; 0,21-0,40 razoável;
0,41-0,60 moderada; 0,61-0,80 substancial; > 0,80 quase perfeita.

## O que não será feito

- Mudar o protocolo ou a amostra depois de ver os rótulos.
- Retirar manchetes "difíceis".
