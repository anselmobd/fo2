# fo2

## Fabril Oxigenai

Projeto de **Intranet** desenvolvido para uma grande fábrica de roupas.

A maior parte das funcionalidades dessa intranet está agrupada em um subprojeto chamado "**Apoio ao ERP**", pois tem exatamente esse propósito: complementar o ERP utilizado pela empresa. O objetivo é tornar o uso do ERP mais simples e amigável, especialmente em cenários onde sua interface nativa apresenta limitações.

O ERP roda sobre Oracle, e o "**Apoio ao ERP**" acessa esse banco de dados principalmente por meio de raw SQL. São mais de 700 queries utilizadas nas diversas views da aplicação.

Além disso, cerca de 25% do sistema é composto por rotinas auxiliares e funcionalidades independentes do ERP, que utilizam PostgreSQL como banco de dados.

O projeto é monolítico, seguindo o padrão arquitetural **MVC (Model-View-Controller)**, e foi desenvolvido com **Python (Django)**, **HTML**, **CSS**, e um pouco de **JavaScript puro**.

### Infraestrutura

Inicialmente, toda a aplicação e os bancos de dados eram hospedados localmente na empresa. Em um determinado momento, o banco Oracle foi migrado para a **Oracle Cloud**, por demanda do ERP. No entanto, a aplicação da intranet (incluindo o Apoio ao ERP) e o banco PostgreSQL permaneceram em servidores locais.
