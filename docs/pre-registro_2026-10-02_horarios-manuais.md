# Pré-registro — desenho do teste com horários conferidos à mão

**Data:** 02/10/2026, escrito **antes** de qualquer horário ser coletado.
Ideia sugerida por uma avaliadora da FEICIT.

## Pergunta

Separando as notícias pelo horário real de publicação, o sentimento das
notícias publicadas **antes** do pregão se associa ao retorno do dia? E o das
publicadas **depois** do fechamento?

- Notícia publicada antes da abertura só pode **causar** o movimento do dia.
- Notícia publicada depois do fechamento só pode **relatar** o movimento do
  dia.

## Grupos (horário de Brasília, dias úteis)

- **Pré-abertura:** depois das 17h do pregão anterior e antes das 10h do dia D.
- **Pós-fechamento:** das 17h às 23h59 do dia D.
- Notícias publicadas durante o pregão (10h às 17h) ficam fora do teste
  principal, porque são ambíguas.

## Hipóteses

- **H0-C:** a correlação entre o sentimento pré-abertura e o retorno de D é
  igual a zero.
- **H0-D (controle):** a correlação entre o sentimento pós-fechamento e o
  retorno de D é igual a zero.

Mesmo método do teste de fim de semana: z dentro do ativo, Pearson agrupado,
permutação em blocos de data, 10.000 permutações, semente 42, α = 5%, e
Steiger para comparar C e D.

**Leitura:** C significativo e D não → notícia → preço. D significativo → a
imprensa relata o pregão. Os dois significativos → comparar por Steiger.

## Tamanho de amostra (definido agora)

Para detectar r = 0,13 com 80% de poder, são necessários cerca de **460
pares ativo-dia por grupo**. Hoje há 817 notícias com hora real, das quais
cerca de 26% são pré-abertura e 25% pós-fechamento. É insuficiente.

Meta: conferir à mão até **1.500 notícias**, na ordem sorteada da planilha
`dados/horarios_manuais.xlsx`.

## Regra de parada (fixada agora, para não espiar)

Parar quando os dois grupos atingirem 460 pares ativo-dia **ou** em
31/10/2026, o que vier primeiro. O teste roda **uma única vez**, depois da
parada. Ninguém calcula correlação com dados parciais.

A planilha está em ordem aleatória (semente 42). Parar em qualquer ponto
mantém a amostra aleatória, **desde que nenhuma linha seja pulada**.

## Controle de qualidade

Quarenta linhas da planilha já têm a hora real conhecida, misturadas às
outras sem identificação. A concordância entre a hora digitada e a hora
conhecida mede o erro da conferência manual. Essas 40 linhas não entram no
teste.
