---
name: sender-motion-scroll
description: >
  Reglas de motion scroll-driven para sitios Sender: todo movimiento nace del scroll (scrub), lerp
  propio para video, un movimiento firma por sitio, rAF solo cuando el elemento es visible y
  apagado total con reduced-motion. Úsala al implementar o revisar animaciones ligadas al scroll.
metadata:
  source: cristianoleamiranda-dotcom/sender-design-ops
  source-path: sender-design-ops/skills/SKILL-motion.md
  source-commit: 639aed9b21eb54a0c8a1a007d0d21d1a6512bd91
  category: motion
  status: fixed
---
# SKILL · Motion scroll-driven
1. Todo movimiento principal nace del scroll (scrub), no del tiempo: film, stacks, track, dial.
2. Lerp propio para video: cur += (tgt-cur)*.12 → sin tirones aunque el scrub de GSAP sea brusco.
3. Un movimiento firma por sitio (knob) con 3 inputs: drag, teclado, scroll.
4. rAF solo cuando el elemento es visible (IntersectionObserver) — batería/CPU.
5. Reduced-motion apaga TODO (lenis, reveals, scrub a instant, marquee, hint).
6. Duraciones: reveals .95s power3; intros 1.1s power4 stagger .05–.08; transiciones UI .25–.4s.
