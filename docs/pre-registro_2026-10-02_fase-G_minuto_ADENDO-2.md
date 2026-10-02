# Adendo 2 ao pré-registro da Fase G — janelas curtas (até 5 minutos)

**Data:** 02/10/2026, escrito **antes** de calcular qualquer retorno em
janelas menores que 15 minutos.

**O que já se sabia ao escrever:**
- o piloto deu nulo nas janelas de 30 minutos (M1 r = −0,011; M2
  r = −0,029) e nas de 15 minutos;
- o perfil descritivo por barra de 5 minutos só tinha sido olhado em três
  agregados (a hora antes, a barra da publicação e a hora depois).
- Nenhuma janela de 1 a 10 minutos foi calculada.
- Contagens, sem retorno: há barras de 1 minuto dos 8 ativos em 20 pregões
  (03/09 a 01/10/2026) e 470 eventos (ativo, minuto) entre 10h10 e 16h45.

## Por que (ideia do Leonardo)

Se a reação acontece em poucos minutos, somar 30 minutos mistura o sinal com
25 minutos de ruído. Exemplo: se toda a reação está nos primeiros 5
minutos, a janela de 30 minutos tem 6 vezes mais ruído, e a correlação
medida cai para cerca de 40% da verdadeira (1/√6 ≈ 0,41).

**O problema da barra de 5 minutos:** a barra da publicação fica de fora,
porque mistura o antes e o depois. Uma reação nos primeiros minutos pode
cair justamente dentro dela.

Para olhar "no máximo 5 minutos depois", é preciso barra de **1 minuto**. O
Yahoo só guarda 30 dias dela.

## Testes (família própria, Holm sobre os 4, α = 5%, bicaudais)

| | Barras | Pergunta | Retorno usado |
|---|---|---|---|
| **C1** | 1 min (20 pregões) | a notícia prevê os 5 minutos seguintes? | minutos +1 a +5 (o minuto da publicação fica de fora) |
| **C2** | 1 min | a notícia vem depois dos 5 minutos anteriores? | minutos −5 a −1 |
| **C3** | 5 min (60 pregões) | a notícia prevê a barra seguinte? | a barra de 5 min logo depois da barra da publicação |
| **C4** | 5 min | a notícia vem depois da barra anterior? | a barra de 5 min logo antes |

- **Eventos:**
  - C1 e C2: dia útil entre 10h10 e 16h45;
  - C3 e C4: entre 10h30 e 16h20, os mesmos eventos do piloto.
  - Horário exato, com a prioridade do pré-registro (Google real >
    WordPress filtrado). A mesma manchete do mesmo ativo conta uma vez.
- **Retorno anormal:** ativo menos a média dos outros 7, como no piloto.
- **Estatística:** a do `teste_horario`.
- **p-valor:** permutação, 10.000, semente 42. O evento recebe o retorno do
  **mesmo minuto** (C1/C2) ou da **mesma faixa de 5 min** (C3/C4) em outro
  dia sorteado.
- **Medida:** o léxico, pela regra da Fase F. O FinBERT entra como
  secundário.
- **Menor r detectável:** ≈ 0,13 em C1/C2 (n ≈ 470) e ≈ 0,11 em C3/C4
  (n ≈ 666).

## Secundárias (sem correção)

- **C-S1:** janelas de 1, 2 e 3 minutos depois e antes (formato da reação).
- **C-S2:** contra erro de horário, pula o minuto vizinho: minutos +2 a +6
  e −6 a −2.
- **C-S3:** C1 a C4 com o FinBERT.
- **C-S4, controle positivo:** manchetes de relato contra os 5 minutos
  anteriores.
- **C-S5, perfil minuto a minuto:** de −15 a +15 minutos, para os terços
  mais positivo e mais negativo. Descritivo; vira gráfico.

## Status

- **Exploratório (piloto):** o n é pequeno, só 20 pregões de barras de 1
  minuto. Este adendo **não** muda nenhuma conclusão já escrita.
- **Coleta prospectiva:** na análise confirmatória da Fase G (regra de
  parada: 1.500 eventos ou 30/06/2027), **C1 e C2 entram na família junto
  com M1 e M2**, com Holm sobre os 4. Isso foi escrito antes de existir
  qualquer dado da amostra confirmatória, que começa em 03/10/2026. O
  coletor diário já guarda as barras de 1 minuto.

## Leitura (fixada agora)

- **C1 > 0 e significativo:** reação rápida (notícia → preço em minutos).
- **C2 > 0 e significativo:** o preço anda nos minutos antes da notícia.
- **Nulos com poder baixo:** inconclusivo, sem leitura de ausência de efeito.
