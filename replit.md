# Workspace

## Overview

pnpm workspace monorepo usando TypeScript. O projeto é o **TRAMPO** — plataforma brasileira de matchmaking de carreiras com IA.

## Stack

- **Monorepo tool**: pnpm workspaces
- **Node.js version**: 24
- **Package manager**: pnpm
- **TypeScript version**: 5.9
- **API framework**: Express 5
- **Database**: PostgreSQL + Drizzle ORM
- **Validation**: Zod (`zod/v4`), `drizzle-zod`
- **API codegen**: Orval (from OpenAPI spec)
- **Build**: esbuild (CJS bundle)
- **Frontend**: React + Vite + Tailwind CSS + shadcn/ui
- **Auth**: JWT (bcryptjs + jsonwebtoken)
- **Forms**: react-hook-form + zod
- **Animations**: framer-motion

## Structure

```text
artifacts-monorepo/
├── artifacts/
│   ├── trampo/             # Frontend React+Vite do TRAMPO
│   └── api-server/         # Express API server
├── lib/
│   ├── api-spec/           # OpenAPI spec + Orval codegen config
│   ├── api-client-react/   # Generated React Query hooks
│   ├── api-zod/            # Generated Zod schemas from OpenAPI
│   └── db/                 # Drizzle ORM schema + DB connection
├── pnpm-workspace.yaml
├── tsconfig.base.json
├── tsconfig.json
└── package.json
```

## TRAMPO — Plataforma de Carreiras com IA

### Páginas do Frontend (artifacts/trampo)
- `/` — Landing page com hero, features, CTA
- `/vagas` — Listagem de vagas com filtros
- `/vaga/:id` — Detalhe da vaga
- `/perfil` — Painel do candidato
- `/minhas-candidaturas` — Candidaturas do candidato
- `/recrutador` — Painel do recrutador
- `/premium` — Plano premium
- `/suporte` — Suporte
- `/admin` — Admin dashboard
- `/login`, `/cadastro`, `/esqueci-senha` — Auth

### API Routes (artifacts/api-server)
- `POST /api/auth/register` — Cadastro
- `POST /api/auth/login` — Login
- `GET /api/auth/me` — Dados do usuário
- `POST /api/auth/forgot-password` — Recuperar senha
- `POST /api/auth/reset-password` — Redefinir senha
- `GET/PUT /api/candidates/profile` — Perfil candidato
- `GET /api/candidates/applications` — Minhas candidaturas
- `GET/POST /api/jobs` — Listar/criar vagas
- `GET/PUT/DELETE /api/jobs/:id` — Vaga específica
- `GET/POST /api/applications` — Candidaturas
- `PUT /api/applications/:id` — Atualizar status
- `GET /api/payments/status` — Status premium
- `POST /api/payments/create-checkout` — Checkout Stripe
- `GET/POST /api/support/tickets` — Tickets de suporte
- `GET /api/admin/stats` — Estatísticas admin
- `GET /api/recruiters/jobs` — Vagas do recrutador

### Database Schema (lib/db/src/schema)
- `users` — Usuários (candidatos, recrutadores, admins)
- `candidate_profiles` — Perfis dos candidatos
- `jobs` — Vagas
- `applications` — Candidaturas com score de match
- `support_tickets` — Tickets de suporte

### Auth
- JWT salvo em localStorage (`trampo_token`, `trampo_user`)
- Header: `Authorization: Bearer <token>`
- Roles: candidate, recruiter, admin

## TypeScript & Composite Projects

Every package extends `tsconfig.base.json` which sets `composite: true`. The root `tsconfig.json` lists all packages as project references.

## Root Scripts

- `pnpm run build` — typecheck + build recursivo
- `pnpm run typecheck` — tsc --build --emitDeclarationOnly
- `pnpm --filter @workspace/api-spec run codegen` — gerar clients da API
- `pnpm --filter @workspace/db run push` — sincronizar schema com DB
