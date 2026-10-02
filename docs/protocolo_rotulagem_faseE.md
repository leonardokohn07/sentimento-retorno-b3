# Protocolo de rotulagem de sentimento (Fase E)

Você vai classificar o sentimento de manchetes de notícias brasileiras **do
ponto de vista do acionista da empresa indicada** na coluna `empresa`.

Para cada linha:
- **positivo:** a notícia é BOA para quem tem ações da empresa (lucro alto,
  contrato novo, aprovação, alta da ação, recomendação de compra, expansão).
- **negativo:** a notícia é RUIM para o acionista (prejuízo, multa, processo,
  queda da ação, rebaixamento, acidente, crise, greve, investigação).
- **neutro:** a notícia não tem direção clara para o acionista: informativa,
  institucional, vagas de emprego, patrocínio, promoção de produto,
  irrelevante para a empresa, ou ambígua (coisas boas e ruins juntas, sem
  predominância).

Regras:
1. Julgue **apenas pelo texto da manchete**. Não use conhecimento do que
   aconteceu com a ação depois, nem notícias posteriores.
2. Se a manchete fala de várias empresas, julgue o efeito **para a empresa da
   coluna `empresa`**.
3. Na dúvida entre positivo/negativo e neutro, escolha **neutro**.
4. Não deixe nenhuma linha em branco.
