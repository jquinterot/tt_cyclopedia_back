# Frontend Domain Agent Practices

## Scope
React/TypeScript frontend: component quality, TypeScript types, UX polish, test coverage, performance.

## Practices

### Component Design
- Keep components small and focused (Single Responsibility).
- Extract reusable logic into custom hooks in `src/hooks/`.
- Use TypeScript strict mode. Define explicit prop interfaces.
- Never use `any`. Use `unknown` with type guards when types are uncertain.
- Co-locate tests with components: `Component.test.tsx` or `Component.cy.tsx`.

### Testing
- Run `npm run unit:test -- --run` before push.
- Test user interactions, not implementation details.
- Mock API calls with MSW (Mock Service Worker) or jest mocks.
- Target: >70% coverage for hooks and utility functions.

### UX Polish
- Add loading skeletons for async data instead of blank screens.
- Use error boundaries to catch render errors gracefully.
- Add optimistic updates for likes/posts to feel snappy.
- Lazy load images and below-the-fold components.
- Ensure responsive design works on mobile (320px+).

### State Management
- Use React Query (TanStack Query) for server state.
- Use Zustand or Context for client-only state.
- Avoid prop drilling >2 levels deep.

### Accessibility
- Use semantic HTML elements.
- Add `aria-label` to icon-only buttons.
- Ensure color contrast meets WCAG AA.

## Verification Checklist
- [ ] Unit tests pass: `npm run unit:test -- --run`
- [ ] No TypeScript errors: `npx tsc --noEmit`
- [ ] New tests added for changed code
- [ ] Components are accessible (keyboard navigation, screen readers)
- [ ] Responsive on mobile viewport
