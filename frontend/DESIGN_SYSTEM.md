# Design System - GLPI Dashboard

## Visão Geral

Este documento descreve o design system implementado no GLPI Dashboard, incluindo design tokens, componentes padronizados e diretrizes de acessibilidade.

## Design Tokens

### Cores

Nosso sistema de cores é baseado em variáveis CSS HSL para máxima flexibilidade e suporte a temas:

```css
/* Cores primárias */
--primary: 222.2 84% 4.9%
--primary-foreground: 210 40% 98%

/* Cores secundárias */
--secondary: 210 40% 96%
--secondary-foreground: 222.2 84% 4.9%

/* Cores de status */
--success: 142 76% 36%
--warning: 38 92% 50%
--error: 0 84% 60%
--info: 221 83% 53%
```

### Tipografia

Sistema de tipografia consistente baseado em escalas harmônicas:

```typescript
// Tamanhos de fonte
fontSizes: {
  xs: "0.75rem",    // 12px
  sm: "0.875rem",   // 14px
  base: "1rem",     // 16px
  lg: "1.125rem",   // 18px
  xl: "1.25rem",    // 20px
  "2xl": "1.5rem",  // 24px
  "3xl": "1.875rem", // 30px
  "4xl": "2.25rem",  // 36px
}

// Pesos de fonte
fontWeights: {
  light: "300",
  normal: "400",
  medium: "500",
  semibold: "600",
  bold: "700",
  extrabold: "800",
}
```

### Espaçamento

Sistema de espaçamento baseado em múltiplos de 4px:

```typescript
spacing: {
  0: "0",
  1: "0.25rem",  // 4px
  2: "0.5rem",   // 8px
  3: "0.75rem",  // 12px
  4: "1rem",     // 16px
  5: "1.25rem",  // 20px
  6: "1.5rem",   // 24px
  8: "2rem",     // 32px
  10: "2.5rem",  // 40px
  12: "3rem",    // 48px
  16: "4rem",    // 64px
  20: "5rem",    // 80px
  24: "6rem",    // 96px
}
```

## Componentes

### Button

Componente de botão com múltiplas variantes e estados:

```tsx
import { Button } from "@/components/ui/button";

// Variantes básicas
<Button variant="default">Botão Padrão</Button>
<Button variant="secondary">Botão Secundário</Button>
<Button variant="destructive">Botão Destrutivo</Button>
<Button variant="outline">Botão Outline</Button>
<Button variant="ghost">Botão Ghost</Button>
<Button variant="link">Botão Link</Button>

// Variantes de status
<Button variant="success">Sucesso</Button>
<Button variant="warning">Aviso</Button>

// Tamanhos
<Button size="sm">Pequeno</Button>
<Button size="default">Padrão</Button>
<Button size="lg">Grande</Button>
<Button size="xl">Extra Grande</Button>

// Com ícones
<Button icon={<CheckIcon />} iconPosition="left">
  Com Ícone
</Button>

// Estado de carregamento
<Button loading={true}>Carregando...</Button>
```

### Card

Componente de card flexível para exibir conteúdo:

```tsx
import { Card, CardHeader, CardTitle, CardContent, CardFooter, CardMetric } from "@/components/ui/card";

// Card básico
<Card>
  <CardHeader>
    <CardTitle>Título do Card</CardTitle>
  </CardHeader>
  <CardContent>
    <p>Conteúdo do card...</p>
  </CardContent>
</Card>

// Card com variantes
<Card variant="elevated" size="lg">
  <CardContent>
    Conteúdo elevado
  </CardContent>
</Card>

// Card de métrica
<CardMetric
  title="Total de Tickets"
  value={1234}
  trend="up"
  trendValue="+12%"
  description="Comparado ao mês anterior"
/>

// Card com status
<Card status="success">
  <CardContent>
    Card com status de sucesso
  </CardContent>
</Card>
```

### Badge

Componente para exibir status, categorias e informações concisas:

```tsx
import { Badge, useBadgeVariant } from "@/components/ui/badge";

// Variantes básicas
<Badge variant="default">Padrão</Badge>
<Badge variant="secondary">Secundário</Badge>
<Badge variant="destructive">Destrutivo</Badge>
<Badge variant="outline">Outline</Badge>

// Variantes de status
<Badge variant="success">Sucesso</Badge>
<Badge variant="warning">Aviso</Badge>
<Badge variant="error">Erro</Badge>
<Badge variant="info">Info</Badge>

// Variantes específicas para tickets
<Badge variant="open">Aberto</Badge>
<Badge variant="inProgress">Em Andamento</Badge>
<Badge variant="resolved">Resolvido</Badge>
<Badge variant="closed">Fechado</Badge>

// Variantes de prioridade
<Badge variant="low">Baixa</Badge>
<Badge variant="medium">Média</Badge>
<Badge variant="high">Alta</Badge>
<Badge variant="critical">Crítica</Badge>

// Com ícones
<Badge icon={<AlertIcon />} iconPosition="left">
  Com Ícone
</Badge>

// Dismissível
<Badge dismissible onDismiss={() => console.log("Removido")}>
  Removível
</Badge>

// Usando hook para mapear status
const badgeVariant = useBadgeVariant(ticketStatus, "status");
<Badge variant={badgeVariant}>{statusText}</Badge>
```

### Typography

Componente para texto consistente e acessível:

```tsx
import { Typography, MetricDisplay, KpiDisplay, StatusText } from "@/components/ui/typography";

// Headings
<Typography variant="h1">Título Principal</Typography>
<Typography variant="h2">Subtítulo</Typography>
<Typography variant="h3">Seção</Typography>

// Texto do corpo
<Typography variant="body">Texto normal</Typography>
<Typography variant="bodyLarge">Texto grande</Typography>
<Typography variant="bodySmall">Texto pequeno</Typography>

// Texto especializado
<Typography variant="lead">Texto de destaque</Typography>
<Typography variant="muted">Texto secundário</Typography>
<Typography variant="code">código</Typography>

// Para dashboards
<Typography variant="metric">1,234</Typography>
<Typography variant="metricLabel">Total de Tickets</Typography>
<Typography variant="kpi">98.5%</Typography>
<Typography variant="kpiLabel">Disponibilidade</Typography>

// Componentes especializados
<MetricDisplay
  value={1234}
  label="Total de Tickets"
  trend="up"
  trendValue="+12%"
/>

<KpiDisplay
  value="98.5%"
  label="Disponibilidade"
  description="Últimas 24 horas"
  status="success"
/>

<StatusText status="success" showIcon>
  Operação realizada com sucesso
</StatusText>
```

## Theme Provider

### Configuração

O ThemeProvider gerencia temas e design tokens:

```tsx
import { ThemeProvider, useTheme, useDesignTokens } from "@/lib/theme-provider";

// Envolver a aplicação
<ThemeProvider defaultTheme="system" storageKey="app-theme">
  <App />
</ThemeProvider>

// Usar em componentes
function MyComponent() {
  const { theme, setTheme } = useTheme();
  const tokens = useDesignTokens();
  
  return (
    <div style={{ color: tokens.colors.primary }}>
      Tema atual: {theme}
      <button onClick={() => setTheme("dark")}>Modo Escuro</button>
    </div>
  );
}
```

### Temas Disponíveis

- `light`: Tema claro
- `dark`: Tema escuro
- `system`: Segue a preferência do sistema

## Acessibilidade

### Validação Automática

Usamos axe-core para validação automática de acessibilidade:

```tsx
import { AccessibilityValidator, useAxeValidation } from "@/lib/accessibility";

// Wrapper para validação automática
<AccessibilityValidator name="meu-componente">
  <MeuComponente />
</AccessibilityValidator>

// Hook para validação manual
function MeuComponente() {
  const ref = useRef<HTMLDivElement>(null);
  useAxeValidation(ref);
  
  return <div ref={ref}>Conteúdo...</div>;
}
```

### Diretrizes de Acessibilidade

#### Contraste de Cores
- Todas as combinações de cores atendem ao padrão WCAG 2.1 AA
- Contraste mínimo de 4.5:1 para texto normal
- Contraste mínimo de 3:1 para texto grande

#### Navegação por Teclado
- Todos os elementos interativos são acessíveis via teclado
- Ordem de foco lógica e visível
- Suporte a teclas de atalho padrão

#### Leitores de Tela
- Elementos semânticos apropriados
- Labels e descrições ARIA
- Anúncios de mudanças de estado

#### Responsividade
- Suporte a zoom até 200%
- Layout flexível para diferentes tamanhos de tela
- Texto redimensionável

## Testes de Acessibilidade

### Execução Manual

```typescript
import { runFullAccessibilityAudit } from "@/lib/accessibility";

// Executar auditoria completa
const audit = await runFullAccessibilityAudit();
console.log(audit.summary);

if (!audit.passed) {
  console.error("Issues encontradas:", audit.violations);
}
```

### Testes Automatizados

```typescript
import { testAccessibility } from "@/lib/accessibility";
import { render } from "@testing-library/react";

test("componente deve ser acessível", async () => {
  const { container } = render(<MeuComponente />);
  await testAccessibility(container);
});
```

## Exemplos de Uso

### Dashboard Card

```tsx
function TicketSummaryCard() {
  return (
    <Card variant="elevated" size="lg">
      <CardHeader>
        <CardTitle>Resumo de Tickets</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <MetricDisplay
          value={1234}
          label="Total de Tickets"
          trend="up"
          trendValue="+5.2%"
        />
        
        <div className="flex gap-2">
          <Badge variant="open">123 Abertos</Badge>
          <Badge variant="inProgress">45 Em Andamento</Badge>
          <Badge variant="resolved">89 Resolvidos</Badge>
        </div>
      </CardContent>
    </Card>
  );
}
```

### Status Indicator

```tsx
function SystemStatus({ status }: { status: "online" | "offline" | "maintenance" }) {
  const statusConfig = {
    online: { variant: "success" as const, text: "Sistema Online" },
    offline: { variant: "error" as const, text: "Sistema Offline" },
    maintenance: { variant: "warning" as const, text: "Em Manutenção" },
  };
  
  const config = statusConfig[status];
  
  return (
    <div className="flex items-center gap-2">
      <Badge variant={config.variant}>{config.text}</Badge>
      <StatusText status={config.variant} showIcon>
        {config.text}
      </StatusText>
    </div>
  );
}
```

### Formulário Acessível

```tsx
function AccessibleForm() {
  return (
    <AccessibilityValidator name="contact-form">
      <form className="space-y-4">
        <div>
          <Typography as="label" variant="small" htmlFor="name">
            Nome *
          </Typography>
          <input
            id="name"
            type="text"
            required
            aria-describedby="name-help"
            className="w-full p-2 border rounded"
          />
          <Typography id="name-help" variant="muted" className="text-xs">
            Digite seu nome completo
          </Typography>
        </div>
        
        <Button type="submit" variant="default">
          Enviar
        </Button>
      </form>
    </AccessibilityValidator>
  );
}
```

## Checklist de Implementação

### Design Tokens 
- [x] Cores padronizadas
- [x] Tipografia consistente
- [x] Espaçamento harmônico
- [x] Raios de borda
- [x] Sombras
- [x] Transições

### Componentes 
- [x] Button com variantes e acessibilidade
- [x] Card flexível e responsivo
- [x] Badge para status e categorias
- [x] Typography semântica

### Theme Provider 
- [x] Gerenciamento de temas
- [x] Suporte a modo escuro/claro
- [x] Persistência de preferências
- [x] Hooks para acesso aos tokens

### Acessibilidade 
- [x] Integração com axe-core
- [x] Validação automática
- [x] Componentes acessíveis
- [x] Testes automatizados

### Documentação 
- [x] Guia de uso dos componentes
- [x] Exemplos práticos
- [x] Diretrizes de acessibilidade
- [x] Checklist de implementação

## Próximos Passos

1. **Migração Gradual**: Atualizar componentes existentes para usar o design system
2. **Testes Visuais**: Implementar testes de regressão visual
3. **Storybook**: Criar documentação interativa dos componentes
4. **Performance**: Otimizar carregamento de tokens e temas
5. **Expansão**: Adicionar mais componentes conforme necessário

## Suporte

Para dúvidas ou sugestões sobre o design system:
- Consulte a documentação dos componentes
- Execute testes de acessibilidade regularmente
- Mantenha consistência visual em novos componentes
- Reporte issues de acessibilidade imediatamente
