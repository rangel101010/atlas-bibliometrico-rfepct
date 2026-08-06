# Atlas Bibliométrico RFEPCT

Site estático compatível com GitHub Pages e atualização mensal pela API da OpenAlex.

## Publicação inicial

1. Envie **o conteúdo desta pasta** para a raiz do repositório (não envie a pasta externa nem o ZIP fechado).
2. No GitHub, abra **Settings → Pages**.
3. Em **Build and deployment**, escolha **Deploy from a branch**.
4. Selecione `main` e `/(root)` e salve.

Endereço esperado: `https://rangel101010.github.io/atlas-bibliometrico-rfepct/`.

## Ativação da atualização automática

1. Crie uma chave gratuita no painel da OpenAlex.
2. No repositório, abra **Settings → Secrets and variables → Actions**.
3. Em **Secrets**, crie `OPENALEX_API_KEY` e cole a chave.
4. Em **Variables**, crie `OPENALEX_MAILTO` com o e-mail de contato do projeto.
5. Abra **Actions → Atualizar Atlas OpenAlex → Run workflow** para a primeira sincronização.

Depois disso, a ação será executada no primeiro dia de cada mês. O período bibliométrico inicial está fixado em 2021–2025 para manter comparabilidade com a Avaliação Temática. Para incluir anos futuros, altere `YEARS` e o filtro de datas em `scripts/update_openalex.py`.

## Regra de qualidade

O arquivo `data/works.json` possui dois conjuntos: `works` (confirmados e exibidos no Atlas) e `review` (correspondências ambíguas). Casos em revisão não entram nos indicadores até que a regra de identificação seja aprimorada ou validada manualmente.
