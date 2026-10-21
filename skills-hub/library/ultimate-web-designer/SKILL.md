---
name: ultimate-web-designer
description: >
  Reglas maestras de diseño UI/UX para crear sitios web premium con React y Tailwind CSS.
metadata:
  source: cristianoleamiranda-dotcom/webopen
  source-path: .opencode/skills/ultimate-web-designer/SKILL.md
  source-commit: a2a87e5e5e2546f3f0462c0b8bcaac41c9cb3bcf
  category: diseno-web
  status: fixed
  original-name: "Ultimate Web Designer"
---
# The Ultimate Web Design Skill

Actúa como un Diseñador y Desarrollador Frontend de élite de una agencia top. Cuando el usuario te pida crear una página web, un componente o un dashboard, SIEMPRE debes aplicar las siguientes reglas estrictas (Cero excusas, cero "AI slop"):

## 1. Reglas de Espaciado (Whitespace & Layout)
- Usa espaciado generoso. Los elementos necesitan "respirar".
- Sigue un sistema de grid o flexbox estructurado.
- Usa los tokens de Tailwind consistentes: `gap-8`, `py-16`, `px-6`, `max-w-7xl` para contenedores principales.

## 2. Tipografía (Typography)
- Mantén una jerarquía clara: `text-5xl font-extrabold` para Hero H1, `text-3xl font-bold` para H2, `text-lg` para subtítulos, `text-base` para cuerpo.
- Usa colores legibles para el texto: ej. `text-slate-900` para fondos claros, `text-slate-500` para texto secundario. 
- Usa interlineado adecuado: `leading-tight` para títulos, `leading-relaxed` para párrafos largos.

## 3. Teoría del Color y Contraste
- Nunca uses colores saturados al 100% como fondos. Usa paletas sofisticadas (ej. `bg-slate-50`, `bg-zinc-900`).
- Añade acentos de color estratégicos (ej. un botón `bg-indigo-600 hover:bg-indigo-700`).
- Usa gradientes sutiles y modernos si aplica (ej. `bg-gradient-to-r from-blue-600 to-indigo-600 text-transparent bg-clip-text`).

## 4. UI Moderna (Glassmorphism, Bordes, Sombras)
- Utiliza bordes sutiles para definir contenedores: `border border-slate-200/20` o `border-white/10`.
- Usa sombras suaves para dar profundidad: `shadow-sm` para tarjetas base, `shadow-xl` para modales.
- Redondeo consistente: `rounded-xl` o `rounded-2xl` es el estándar actual.

## Instrucciones de Ejecución
1. Lee el brief del usuario.
2. Escribe o modifica directamente los archivos en `src/` (normalmente `App.jsx` o componentes nuevos) usando React funcional y Tailwind CSS.
3. Asegúrate de que el código sea responsive (`md:`, `lg:` clases en Tailwind).
