# Resumo v4 — de onde sai cada frase

Regra usada: só entrou no resumo o que tem uma fonte que dá para abrir e
conferir. Os números vêm das saídas que o verificador reproduz
(`verificacao/referencia/E??/`), que são idênticas às de `resultados/`.

| # | Frase (resumida) | Fonte |
|---|---|---|
| 1 | Objetivo: associação e direção (notícia → preço ou preço → notícia) | `docs/pre-registro_2026-10-02_fase-causal.md` |
| 2 | 19.410 notícias, 8 ações, 7 setores, jan/2024 a set/2026 | `resultados/congelado_*.txt` ("19410 noticias"); setores nos comentários de `CARTEIRA_ESTUDO` em `modulos/coleta/precos.py`; datas: 01/01/2024 a 06/09/2026 em `dados/noticias_com_sentimento.csv` |
| 2 | 7.291 notícias de out/2021 a dez/2023 | linhas de `dados/noticias_2021_2023.csv` (01/10/2021 a 01/01/2024) |
| 2 | 1.160 notícias de 8 ações de menor liquidez | `resultados/fase_H_smallcaps_lexico_2026-10-02.txt` ("Notícias (até 06/09/2026): 1160") |
| 3 | Léxico + modelo de linguagem como verificação | `docs/pre-registro_2026-10-02_fase-F_modelo-de-linguagem.md`; FinBERT-PT-BR (SANTOS; BIANCHI; COSTA, 2023) |
| 4 | Pearson, permutação com 10.000 repetições, Holm | estudo original: `resultados/resultado_permutacao.txt` (10.000 por ativo; p clássico e de permutação concordam nos 8 ativos); fases novas: `modulos/analise/causal.py` (`teste_parcial`, `teste_horario`, `holm`), n_perm = 10.000 nos scripts 25, 37, 38 e 40 |
| 5 | Mínimo de 60 observações por análise de poder | `modulos/analise/hipotese.py` (`MIN_OBSERVACOES = 60`); poder teórico de 80,3% com 60 em `scripts/7_curvas_de_deteccao.py` (etapa E02) |
| 5 | 1.000 séries simuladas, 5,0% de falsos positivos | saída de `scripts/1_validar_modulo_estatistico.py` (etapa E01): "H0 rejeitada em 5.0% dos casos" |
| 6 | Pré-registro datado a partir de set/2026; todos os resultados reportados | `docs/pre-registro_2026-09-28_*` e seguintes; `verificacao/registro_de_testes.csv` (279 linhas) |
| 7 | D+0 rejeitada em 6 de 8; r de 0,10 a 0,20 | `resultados/congelado_*.txt` (BBDC4 0,1006 a VALE3 0,1965) |
| 8 | Permanece após descontar o Ibovespa | `resultados/teste3_retorno_anormal_*.txt` (r = 0,1094; p = 0,0001) |
| 8 | Maior com a própria empresa | `resultados/teste2_placebo_entre_empresas_*.txt` (própria − cruzada, p = 0,0001) |
| 8 | Repetiu-se em 2021-2023 | `resultados/fase_causal_*.txt`, P8 (r = 0,0768; p de Holm = 0,0018) |
| 8 | Repetiu-se nas de menor liquidez | `resultados/fase_H_smallcaps_lexico_*.txt`, H1 (r = 0,2128; p de Holm = 0,0004) |
| 9 | 4.998 notícias com horário exato (sites e agregador) | `resultados/fase_causal_A1_*.txt` ("4998 (fontes: wordpress_filtrado 4047, google 951)") |
| 9 | Abertura e barras de 60, 5 e 1 minuto | `dados/intradiario/` (60 min), `dados/minuto/` (5 e 1 min), `dados/cache_precos/` (abertura) |
| 10 | Noite ← pregão encerrado (r = 0,083; p = 0,001) | `resultados/fase_causal_A1_*.txt`, A1_P3 (r = 0,0827; p = 0,0010) |
| 10 | Pregão ← hora anterior (r = 0,091; p = 0,003) | mesmo arquivo, A1_P5 (r = 0,0908; p = 0,0031) |
| 11 | Sem associação com abertura seguinte, hora seguinte e 5 min seguintes | P1 (r = 0,011; p = 0,48) e A1_P2 (p = 0,59); A1_P4 (p = 0,23); C1 em `resultados/fase_G_janelas_curtas_lexico_*.txt` (r = −0,023; p = 0,62) |
| 12 | Conclusões mantidas com o modelo de linguagem | `resultados/fase_F_robustez_comparacao_2026-10-02.txt` (P8 com FinBERT: p de Holm 0,0054; A1_P3: p 0,0117; P2 e P4 nulos) |
| 13 | Dados congelados com SHA-256; verificador reproduz em Linux e Windows | `verificacao/manifesto_dados_congelados_2026-10-02.sha256`; `verificacao/relatorio_verificacao_linux_servidor.txt` e `relatorio_verificacao_windows.txt` (99 de 99) |
| 14 | Conclusão; eficiência de mercado semiforte | FAMA (1970); síntese no `docs/diario_causalidade.md`, seção 9 |
| 15 | Limitações: menor efeito detectável; validação preliminar | menor r detectável impresso em cada teste ("r detectável ~"); `resultados/fase_F_validacao_modelos_preliminar_claude_*.txt` |
| 16 | Coleta diária com regra de parada | `docs/pre-registro_2026-10-02_fase-G_minuto.md` e ADENDO-2 (1.500 eventos ou 30/06/2027) |

## O que saiu do resumo antigo (v2) por não ter fonte reproduzível

| Frase do v2 | Problema | O que foi feito |
|---|---|---|
| "poder de 82,7% para o efeito esperado" | Só existe num comentário de `hipotese.py`, de uma rodada antiga do script 7. Hoje o script 7 não reproduz esse número (diário, seção 21) | Trocado por "definido por análise de poder"; o valor reproduzível é o teórico, 80,3% |
| "registrados por escrito antes de cada rodada de testes" | Não há documento datado da rodada original no repositório | Trocado por "a partir de setembro de 2026" |
| "detectou 100% dos efeitos implantados" | Verdade, mas para um efeito implantado (r ≈ 0,36) três vezes maior que o real | Removido; ficou só a taxa de falsos positivos |
| "imprecisão do horário de publicação em 95,7%" | Superada: 4.998 notícias agora têm horário exato | Removido |

## Regras do resumo (conferidas no site da MOSTRATEC)

- De 250 a 500 palavras, parágrafo único. **Este tem 475.**
- Precisa ter objetivo, procedimentos, resultados e conclusões.
- **Não pode** ter nome de orientador, mentor, supervisor nem instituição.
  Este não tem.
- Fonte: https://mostratec.liberato.com.br/resumo/ (acesso em 02/10/2026).
