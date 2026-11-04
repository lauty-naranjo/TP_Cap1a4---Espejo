# Project Design System

Mode: deferred
Approval: deferred
Decision source: consigna del TP (docs/MiniTP_Cap1a4_Consigna.pdf) + knowledge-base/02_descripcion_general.md — el proyecto es una API REST sin frontend (la consigna marca explícitamente qué "queda afuera": auth y UI; el único cliente entregado es `cliente.py` aportado por la cátedra).
Date: 2026-11-03
Recorded by: active-orchestrator (fase design-system, flujo completo)

## Regla

No hay UI planificada para v1.0 de este TP, por lo que **no se crean** brand, tokens ni componentes.

La primera vez que surja un cambio visual real, revisar esta decisión **una sola vez**
y reemplazar `Mode: deferred` por uno de:

| Modo | Significado |
|---|---|
| `system-and-mockups` | Definir design system + mockup por cada cambio visual |
| `system-only` | Definir design system, sin mockup por cambio |
| `off` | Opt-out explícito, sin design system ni mockups |

`deferred` **no es un opt-out permanente**: es una postergación con re-evaluación en el primer cambio visual.
La elección quedó registrada en `.active-orchestrator-state.json → visual_design`.
