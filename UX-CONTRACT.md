# LightSQL UX Contract

## Product context and sources

Simplified Chinese internal business analysis and data administration. Target WCAG 2.2 AA. Preserve domain timezones rather than converting stored dates. No billing, regulated-market, or Japanese-language changes are part of this redesign.

| Scope | Source | UI consequence |
|---|---|---|
| Data preparation and navigation | `docs/前端体验优化.md` | Connection → catalog → topic → ask; retain `source` and `topic` context |
| Access and publication | `backend/app/api/routes/topics.py`, `backend/app/api/deps.py` | Hide administrator navigation for members; only ready authorized topics can start analysis |
| Conversation lifecycle | `backend/app/api/routes/assistant.py` | Keep 24-hour session behavior; deletion is explicit and unavailable during planning |
| Query safety | `docs/M04查询计划与安全执行.md` | Preserve plan review, read-only checks, and execution permission controls |
| Feedback retention | `docs/M07质量评测与运维交付.md` | Conversation deletion does not promise removal of retained quality records |
| Visual system | `DESIGN.md` | Runtime canonical tokens: `frontend/src/index.css` → Tailwind → shared components |

## Canonical UI Map

| Capability | Canonical owner | Source of truth | Allowed variants | Verification |
|---|---|---|---|---|
| Select/Listbox | Native select in semantic forms; `frontend/src/components/ui/select.tsx` for authored selects | Existing field contracts | Native OS popup accepted for business scope and catalog choices; Radix for authored dropdowns | Native selection, keyboard and open popup |
| Form | RHF/Zod for account forms; `ui/validated-form.tsx` with `Semantic/shared.tsx` Field for domain forms | API constraints, field metadata | Create/edit inline validation; retained draft on failure | First invalid focus, error text, successful create |
| Scrollbar | `frontend/src/index.css` | DESIGN.md | Global baseline; local geometry only | Computed colors, overflow, reduced motion |
| Toast | Sonner via `frontend/src/components/ui/sonner.tsx` and `useCustomToast` | Existing notification provider | Success/error; critical failures also inline | Browser status/error checks |
| CRUD | Generated service client + React Query + TanStack routes | API and preparation guide | Create topic enters workspace; source editor stays on list; draft stays in workspace | `scripts/tests/frontend_ux.cjs` |
| Search | `frontend/src/components/ui/search-input.tsx` | Local filtering contract | Immediate local filtering, explicit clear, focus return | `scripts/tests/design_ux.cjs` |
| Dialog | `frontend/src/components/ui/dialog.tsx` | Radix focus and overlay contract | Edit, confirm, destructive | Escape, focus trap/return, narrow viewport |

## Flow ledger

| Operation | Pending | Success | Failure / cancel |
|---|---|---|---|
| Create topic | Block duplicate submit; keep label geometry | Enter topic workspace | Keep dialog and values; show inline error; focus missing field |
| Save topic draft | Disable concurrent save | Stay in workspace, invalidate query | Preserve local draft and existing conflict handling |
| Save table scope | Retain editor while saving | Save then optionally sync | Distinguish saved scope from failed synchronization |
| Delete conversation | Confirm with Cancel initially focused; block while deleting | Remove cached conversation and return to topic's new-session view | Keep confirmation open and display error for retry |
| Search | Immediate, in-memory; no remote calls during composition | Filter visible records | Clear immediately and restore input focus |

## State and navigation policy

- Source, topic, and conversation identity stay in existing URL parameters. Local text search stays transient because names, questions, and feedback may contain sensitive internal data; do not add these to URLs or persistent storage.
- Preserve existing dataset APIs. Topic cards use explicit incremental display; source tables use bounded client pages. Existing catalog and result tables retain their established bounded/internal-scroll strategies.
- Empty, loading, no-results, and errors must be distinguishable. Counts show a dash while unavailable. Error messages retain a retry or correction action.
- Quality evaluation imports accept raw inputs or the existing `definition` export envelope. Dataset reimport creates a new record; run imports preserve the original dataset ID/digest and switch to that dataset/split only after success. Local format errors have actionable Chinese messages. `Quality/RunDiagnostics.tsx` owns failure-only filtering and 20-case pages; filter changes reset paging, historical summaries display an explicit missing-diagnostics message. Summary diagnostics never contain result cells.
- Mutation requests remain pessimistic. Do not automatically retry non-idempotent writes or automatically execute model calls for a visual interaction. Existing request IDs and revision checks stay intact.
- Sidebar is keyboard accessible, marks the active route, and closes after mobile navigation. Its shortcut ignores text inputs and IME composition. Provide a skip link to the main content.
- Search results and forms remain scrollable on a narrow screen. Shared shell heights must not constrain table siblings or longer forms.
- Modal overlays use Radix focus trap, inert background, Escape, and restored focus. Destructive controls are distinct from safe actions. Unsaved topic drafts retain the established router blocker.
- Account forms use app-owned validation. New domain validation must associate an error with the field and focus the first invalid control.

## Migration and verification

This refactor updates shared tokens/navigation and completes the topic, ask, connection, and login entry flows. Specialized query execution, semantic publication, integration, and quality workflows keep their domain logic while inheriting shared visual tokens. Existing handwritten domain forms now use the shared validation adapter; backend revision, permission, and publication validation remains authoritative.

Browser fixtures must intercept every API request. Test create/edit navigation, sync failures/conflicts, member access, dark mode, 390px layout, login validation, search clearing, dialog focus, and deletion retry. Runtime evidence lives in `.local/ux-review/` and `.local/design-review/`; checks never write production data or call configured models.
