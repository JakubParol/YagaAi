# Coding Readiness Execution Plan

## Scope
Plan wykonawczy dla artefaktów wymaganych przez `2026-04-04-coding-kickoff-plan.md`.

## Delivery Phases
1. **Contracts freeze (v1)**
   - HTTP API, internal A2A, webhook callback, event bus.
   - Topic map i ownership producentów/konsumentów.
2. **Data & projections freeze (v1)**
   - SQL schema + migracje bazowe.
   - Projekcje read-model i reguły konfliktów.
3. **Implementation skeleton (v1)**
   - Struktura repo + granice modułów.
   - Interfejsy usług i DTO mapping boundaries.
4. **Quality, security, operations baseline (v1)**
   - Strategia testów i Definition of Done.
   - Security baseline.
   - Runbooki operacyjne.

## Sequencing
1. API Contract Pack
2. Data Model Spec
3. Event Bus Contract + Topic Map
4. Implementation Skeleton Spec
5. Thin vertical slice: ingress -> task -> event -> callback
6. Równolegle: testing + security + runbooks

## Definition of Complete
Artefakty uznajemy za gotowe, gdy:
- Wszystkie pliki v1 istnieją i mają ownera.
- Kontrakty mają przykłady payloadów oraz błędów.
- SQL schema ma klucze, indeksy i constraints.
- DoD definiuje bramki wymagane dla PR.
- Security i runbooki pokrywają minimum operacyjne.
