# Documentação Zomma Quant

Bem-vindo à documentação da Zomma Quant! Esta pasta contém toda a documentação do projeto organizada por área.

## Estrutura da Documentação

```
docs/
├── frontend/              # Documentação específica do frontend
│   ├── ARCHITECTURE.md   # Visão geral da arquitetura do frontend
│   ├── CONTRIBUTING.md   # Guia de contribuição para o frontend
│   ├── DEPLOYMENT.md     # Instruções de implantação
│   ├── access-control.md # Implementação de controle de acesso
│   └── ...
└── README.md             # Este arquivo
```

## Links Rápidos

### Para Novos Membros da Equipe
1. Comece com [Arquitetura do Frontend](frontend/ARCHITECTURE.pt-BR.md) para entender a estrutura do código
2. Leia o [Guia de Contribuição](frontend/CONTRIBUTING.pt-BR.md) para padrões de código e convenções
3. Revise o [Guia de Implantação](frontend/DEPLOYMENT.md) para procedimentos de deploy

### Tópicos Comuns

#### Desenvolvimento Frontend
- **Visão Geral da Arquitetura**: [frontend/ARCHITECTURE.pt-BR.md](frontend/ARCHITECTURE.pt-BR.md)
- **Diretrizes de Contribuição**: [frontend/CONTRIBUTING.pt-BR.md](frontend/CONTRIBUTING.pt-BR.md)
- **Implantação**: [frontend/DEPLOYMENT.md](frontend/DEPLOYMENT.md)

#### Recursos & Componentes
- **Estratégia Collar**: [frontend/COLLAR_APP_IMPROVEMENTS.md](frontend/COLLAR_APP_IMPROVEMENTS.md)
- **Calendário de Dividendos**: [frontend/DIVIDEND_CALENDAR_IMPROVEMENTS.md](frontend/DIVIDEND_CALENDAR_IMPROVEMENTS.md)
- **Melhorias do Dashboard**: [frontend/Dashboard_Enhancement_Suggestions.md](frontend/Dashboard_Enhancement_Suggestions.md)

#### Autenticação & Acesso
- **Autenticação por Username**: [frontend/username-authentication.md](frontend/username-authentication.md)
- **Controle de Acesso**: [frontend/access-control.md](frontend/access-control.md)

#### Integração
- **Stripe & Supabase**: [frontend/STRIPE_SUPABASE_INTEGRATION_DETAILED.md](frontend/STRIPE_SUPABASE_INTEGRATION_DETAILED.md)
- **Customização de Email**: [frontend/SUPABASE_EMAIL_CUSTOMIZATION_GUIDE.md](frontend/SUPABASE_EMAIL_CUSTOMIZATION_GUIDE.md)

#### Guias de Implementação
- **Guia Fase 1**: [frontend/PHASE1_IMPLEMENTATION_GUIDE.md](frontend/PHASE1_IMPLEMENTATION_GUIDE.md)

#### Solução de Problemas
- **Problemas de Cookie/Cache**: [frontend/COOKIE_CACHING_ISSUE_ANALYSIS.md](frontend/COOKIE_CACHING_ISSUE_ANALYSIS.md)
- **Erros de Browser**: [frontend/webbrosererror.md](frontend/webbrosererror.md)

## Principais Decisões Arquiteturais

### Por que Radix UI / shadcn/ui?
- Biblioteca de componentes padrão da indústria
- Abordagem de acessibilidade em primeiro lugar
- Controle total de customização
- Usado por equipes profissionais mundialmente

### Por que Next.js App Router?
- Framework React moderno com SSR
- Roteamento baseado em arquivos com convenções
- Otimização integrada
- Deploy sem complicações

### Por que Tailwind CSS?
- Framework CSS utility-first
- Sistema de design consistente
- Saída de build otimizada
- Produtividade do desenvolvedor

## Estrutura do Projeto

```
project-root/
├── backend/           # Backend Python/Flask
├── frontend/          # Frontend Next.js
├── supabase/          # Funções e migrações Supabase
├── docs/             # Documentação (você está aqui)
└── README.md         # README do projeto
```

## Contribuindo

Antes de contribuir para o projeto, por favor leia:
1. [Guia de Contribuição Frontend](frontend/CONTRIBUTING.pt-BR.md)
2. [Arquitetura Frontend](frontend/ARCHITECTURE.pt-BR.md)

## Refatoração Recente (Outubro 2024)

O frontend passou por uma grande refatoração para melhorar a qualidade e manutenibilidade do código:

✅ **Concluído:**
- Removidas imagens duplicadas e assets não utilizados (~50+ arquivos)
- Consolidada estrutura de pastas (docs e supabase na raiz)
- Adicionados comentários JSDoc aos serviços de API e hooks
- Criados guias abrangentes de arquitetura e contribuição
- Atualizados arquivos de config com comentários explicativos
- Padronizados caminhos de importação usando aliases @

📊 **Resultados:**
- Código mais limpo
- Melhor documentação
- Onboarding mais fácil para novos desenvolvedores
- Manutenibilidade aprimorada

## Obtendo Ajuda

- **Dúvidas?** Pergunte à equipe
- **Encontrou um bug?** Crie uma issue
- **Quer contribuir?** Leia o guia de contribuição

## Manutenção

Esta documentação deve ser atualizada conforme o projeto evolui. Ao fazer mudanças significativas:

1. Atualize os arquivos de documentação relevantes
2. Mantenha o guia de arquitetura atualizado
3. Adicione novos padrões ao guia de contribuição
4. Documente mudanças que quebram compatibilidade

---

**Última Atualização**: Outubro 2024  
**Mantido por**: Equipe Zomma Quant

