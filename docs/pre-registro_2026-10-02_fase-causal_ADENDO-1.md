# Adendo 1 ao pré-registro mestre — horários do WordPress

**Data:** 02/10/2026, escrito **antes** de ler qualquer resultado da rodada
principal (`scripts/25_fase_causal.py`, que já estava em execução).

## O que aconteceu

**A regra pré-registrada para o WordPress reprovou.** A validação contra as
horas do Google deu **79,7% dentro de 15 minutos** (n = 123), abaixo do corte
de 85%. **A análise principal segue o pré-registro e usa só as horas do
Google.** Isso não muda.

**Diagnóstico, só sobre horários (nenhum retorno envolvido):** os erros vêm de
casamentos com a matéria ERRADA. Um título igual ou parecido publicado em
outro dia, com diferenças de semanas a anos, concentrado em ocp.news, itforum
e cqcs. O coletor deveria ter exigido também que a data batesse. Isso fazia
parte da intenção original do desenho, mas não foi implementado.

**Filtro de data:**
- notícia com hora real: o dia no WordPress (horário de Brasília) tem que ser
  o mesmo;
- notícia só com data (fuso do Pacífico): o dia tem que ser o mesmo ou o
  seguinte.

Restam **4.127 horários** (97% dos casamentos). A validação sobe para **94,0%
dentro de 15 minutos** (n = 100).

**Observação:** nos 6 desencontros que sobraram, o Google costuma registrar a
notícia DEPOIS do site (de 23 minutos a 8 horas). A hora do Google às vezes é a
hora de indexação. Isso empurra os testes com hora do Google para o lado do
"relato" (a reação aparece antes da hora registrada) e precisa ser lido como
limitação.

## Análise adicional A1 (desvio declarado)

- **O que roda:** P2, P3, P4 e P5, o controle positivo S4, a falsificação S5 e
  o perfil S7.
- **Horários usados:** a hora do Google quando existe; senão, a hora do
  WordPress filtrada.
- **Métodos:** exatamente os do pré-registro.
- **Status:**
  - fora da família de Holm;
  - reportada ao lado da principal, sem substituí-la;
  - se concordar em direção com a principal, acrescenta poder;
  - se discordar, a principal governa a conclusão.

Saída: `resultados/fase_causal_A1_<data>.txt`
