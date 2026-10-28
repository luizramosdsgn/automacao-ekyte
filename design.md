# 🎨 Design System — Robô eKyte

> Guia visual completo do projeto. Todas as decisões de cor, tipografia, espaçamento e componentes estão documentadas aqui.

---

## 1. Filosofia Visual

O design segue o conceito de **Dashboard Moderno** inspirado em painéis de controle SaaS profissionais:

- **Sidebar fixa** com gradiente azul (cor primária) concentra configurações
- **Área principal** em fundo escuro profundo abriga dados e terminal
- **Cantos arredondados generosos** e **sombras suaves** criam profundidade
- **Tipografia limpa** com hierarquia clara (Inter / Segoe UI)
- **Glassmorphism sutil** nos inputs da sidebar (blur + transparência)

---

## 2. Paleta de Cores

### Cores Primárias

| Token            | Hex                    | Uso                                 |
| ---------------- | ---------------------- | ----------------------------------- |
| `--accent`       | `#3179FF`              | Botões principais, links, progresso |
| `--accent-hover` | `#2562d4`              | Hover do accent                     |
| `--accent-light` | `rgba(49,121,255,.12)` | Backgrounds sutis de destaque       |
| `--accent-glow`  | `rgba(49,121,255,.25)` | Sombra de foco nos inputs           |

### Cores Secundárias

| Token           | Hex       | Uso                                    |
| --------------- | --------- | -------------------------------------- |
| `--green`       | `#10b981` | Botões de ação secundária (Padronizar) |
| `--green-hover` | `#059669` | Hover do green                         |
| `--red`         | `#ef4444` | Botão de parar / danger                |
| `--red-hover`   | `#dc2626` | Hover do danger                        |
| `--yellow`      | `#f59e0b` | Alertas e avisos (reservado)           |

### Cores de Superfície (Dark Theme)

| Token             | Hex       | Uso                                |
| ----------------- | --------- | ---------------------------------- |
| `--bg-body`       | `#1a1a2e` | Fundo geral da página              |
| `--bg-shell`      | `#16162a` | Container principal / terminal bg  |
| `--bg-card`       | `#22223a` | Área de conteúdo principal         |
| `--bg-card-alt`   | `#2a2a48` | Cards internos (reservado)         |
| `--bg-input`      | `#2e2e4a` | Fundo dos inputs na área principal |
| `--border-subtle` | `#3a3a5c` | Bordas suaves entre seções         |
| `--border-input`  | `#444466` | Bordas dos inputs                  |

### Cores de Texto

| Token              | Hex       | Uso                              |
| ------------------ | --------- | -------------------------------- |
| `--text-primary`   | `#f0f0f8` | Texto principal / títulos        |
| `--text-secondary` | `#a0a0c0` | Labels, texto de apoio           |
| `--text-muted`     | `#6b6b8d` | Placeholders, texto desabilitado |

---

## 3. Tipografia

| Elemento        | Família                            | Peso    | Tamanho |
| --------------- | ---------------------------------- | ------- | ------- |
| Corpo geral     | Inter, Segoe UI, system-ui         | 400     | 13px    |
| Labels sidebar  | Inter                              | 600     | 11px    |
| Títulos (h2)    | Inter                              | 700-800 | 14-18px |
| Terminal log    | Cascadia Code, Fira Code, Consolas | 400     | 12px    |
| Botão principal | Inter                              | 700     | 14px    |
| Texto progresso | Inter                              | 700     | 12px    |

### Regras tipográficas

- Labels da sidebar são **UPPERCASE** com `letter-spacing: 0.6px`
- Títulos usam `letter-spacing: -0.3px` para compactação visual
- Terminal usa fonte monospace com `line-height: 1.7` para leitura confortável
- Números no progresso usam `font-variant-numeric: tabular-nums` para não "dançar"

---

## 4. Espaçamento e Layout

### Grid Principal

```
┌─────────────────────────────────────────────────┐
│  ┌──────────┬─────────────────────────────────┐  │
│  │          │                                 │  │
│  │ SIDEBAR  │        MAIN CONTENT             │  │
│  │  260px   │          flex: 1                │  │
│  │          │                                 │  │
│  │ gradient │  bg-card (#22223a)              │  │
│  │  blue    │                                 │  │
│  │          │                                 │  │
│  └──────────┴─────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
  bg-shell (#16162a) — border-radius: 28px
```

### Escala de espaçamento

| Nome | Valor | Uso                     |
| ---- | ----- | ----------------------- |
| `xs` | 4px   | Gap entre label e input |
| `sm` | 12px  | Gap entre cards/seções  |
| `md` | 16px  | Gap sidebar             |
| `lg` | 24px  | Padding do main content |
| `xl` | 28px  | Padding da sidebar      |

### Border Radius

| Token         | Valor | Uso                       |
| ------------- | ----- | ------------------------- |
| `--radius-sm` | 8px   | Inputs, botões menores    |
| `--radius-md` | 14px  | Textareas, botão primário |
| `--radius-lg` | 20px  | Responsivo                |
| `--radius-xl` | 28px  | Container principal       |

---

## 5. Componentes

### 5.1 Sidebar

- **Background:** Gradiente linear de `#3179FF` → `#254ebd`
- **Overlay escuro:** `rgba(0,0,0,.12)` para profundidade
- **Inputs:** Background `rgba(255,255,255,.12)` com `backdrop-filter: blur(4px)`
- **Botão primário:** Fundo branco com texto azul (inversão intencional para contraste máximo na sidebar)

### 5.2 Inputs

- **Na sidebar:** Estilo glassmorphism (transparente com blur)
- **Na área principal:** Fundo sólido `--bg-input` com borda `--border-input`
- **Foco:** Borda muda para `--accent` + sombra `--accent-glow`
- **Transição:** `0.25s cubic-bezier(.4,0,.2,1)`

### 5.3 Botões

| Variante  | Background              | Cor texto | Contexto           |
| --------- | ----------------------- | --------- | ------------------ |
| Primary   | `#ffffff`               | `#3179FF` | Iniciar automação  |
| Secondary | `rgba(255,255,255,.14)` | `#fff`    | Escolher diretório |
| Warning   | `#10b981`               | `#fff`    | Padronizar texto   |
| Danger    | `#ef4444`               | `#fff`    | Parar automação    |

### 5.4 Barra de Progresso

- **Track:** `--border-subtle` com `border-radius: 20px`
- **Fill:** Gradiente de `--accent` → `#5a9aff`
- **Animação shimmer:** Efeito de brilho deslizante (2s infinite)
- **Altura:** 10px

### 5.5 Terminal de Log

- **Background:** `--bg-shell` (o tom mais escuro)
- **Texto:** `--accent` (azul, simulando terminal colorido)
- **Fonte:** Monospace (Cascadia Code > Fira Code > Consolas)
- **Borda:** `--border-subtle`

---

## 6. Efeitos e Transições

| Efeito               | Aplicação           | Detalhes                                     |
| -------------------- | ------------------- | -------------------------------------------- |
| **Glassmorphism**    | Inputs da sidebar   | `backdrop-filter: blur(4px)` + transparência |
| **Shadow elevation** | Container principal | `0 4px 24px rgba(0,0,0,.35)` + glow azul     |
| **Hover lift**       | Botão primário      | `translateY(-1px)` + shadow aumentada        |
| **Shimmer**          | Barra de progresso  | Brilho linear animado 2s                     |
| **Glow ring**        | Focus nos inputs    | `box-shadow: 0 0 0 3px accent-glow`          |

---

## 7. Scrollbar Customizada

```css
width: 6px
track: transparent
thumb: var(--border-subtle) → var(--text-muted) no hover
border-radius: 10px
```

---

## 8. Responsividade

- **Breakpoint:** `700px`
- **Abaixo de 700px:** Layout empilha verticalmente (sidebar em cima, conteúdo embaixo)
- **Sidebar:** Passa de `width: 260px` para `width: 100%` com `border-radius` ajustado para topo

---

## 9. Acessibilidade

- `:focus-visible` com outline de 2px `--accent`
- `role="log"` e `aria-live="polite"` no terminal
- `aria-valuenow`, `aria-valuemin`, `aria-valuemax` na barra de progresso
- Labels associados via `for`/`id` e `aria-labelledby`
- Contraste mínimo WCAG AA em todos os textos sobre seus backgrounds
