# fo2

## Fabril  Oxigenai

Projeto de **Intranet** desenvolvido para uma grande fábrica de roupas.

Boa parte das funcionalidades dessa intranet é agrupada como um subprojeto chamado "**Apoio ao ERP**", pois é exatamente isso, um complemento ao ERP utilizado pela empresa.
O objetivo desse "complemento" é facilitar, sempre que possível, a vida dos usuários desse ERP, que poderia/deveria ser mais amigável em muitos contextos.
O ERP roda sobre Oracle, e o "**Apoio ao ERP**" acessa esse banco de dados prioritáriamente utilizando "raw SQL", sendo comtabilizadas mais de 700 queries, utilizadas em todas as views criadas.

Rotinas auxiliares, funcionalidades totalmente separadas do ERP, que representam algo em torno de 25% do projeto todo, utilizam PostgreSQL.

Trata-se de um projeto monolítico no padrão MVC (Model-View-Controller), desenvolvido com Python e Django, HTML, CSS e um pouco de JavaScript puro.

Sobre a infraestrutura: O projeto era todo servido localmente, dentro da empresa: Aplicação e os dois bancos de dados. A partir de certo momento o banco de dados Oracle passou a ser hospedado na OracleCloud, por uma necessidade do ERP. A aplicação da intranet (com o Apoio ao ERP), assim como o banco de dados PostgreSQL, continuaram locais.
