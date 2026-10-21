// Configuración curada del hub. Cada entrada apunta a un repo público del
// perfil y describe cómo importar una skill: ruta, slug final, categoría y
// etiquetas. Los `description` son solo para archivos que no traen frontmatter.

export const OWNER = 'cristianoleamiranda-dotcom';
export const LIBRARY_VERSION = 1;

export const CATEGORIES = {
  'diseno-web': 'Diseño y construcción de sitios inmersivos',
  motion: 'Motion design y animación',
  pixijs: 'PixiJS v8 (WebGL/WebGPU)',
  video: 'Video, imagen y ffmpeg',
  'reverse-engineering': 'Ingeniería inversa y evidencia (REA)',
  'flujo-trabajo': 'Flujo de trabajo con agentes',
};

const senderTags = ['scroll', 'gsap', 'threejs', 'editorial', 'awwwards'];
const pixiTags = ['pixijs', 'webgl', 'webgpu', 'canvas'];
const reaTags = ['rea', 'reverse-engineering', 'evidencia'];

export const REPOS = [
  {
    repo: 'sender-motion-kit',
    branch: 'main',
    // El SKILL.md referencia CHECKLIST.md, WORKFLOW.md, patterns.md, etc.:
    // se copia el repo completo como payload de la skill.
    payload: 'repo',
    skills: [
      {
        source: 'SKILL.md',
        slug: 'sender-immersive-web-department',
        category: 'diseno-web',
        tags: ['departamento', 'inmersivo', ...senderTags],
      },
    ],
  },
  {
    repo: 'sender-design-ops',
    branch: 'main',
    skills: [
      {
        source: 'sender-design-ops/skills/SKILL-design-system.md',
        slug: 'sender-design-system',
        category: 'diseno-web',
        tags: ['design-system', 'tokens', 'editorial'],
        description:
          'Sistema de diseño «Broadcast Editorial» para landings premium: tokens antes que componentes, ritmo de actos papel/oscuro, hairlines en vez de sombras, mono para metadatos y paleta innegociable. Úsala al definir o auditar la capa visual de un sitio Sender.',
      },
      {
        source: 'sender-design-ops/skills/SKILL-motion.md',
        slug: 'sender-motion-scroll',
        category: 'motion',
        tags: ['scroll', 'scrub', 'lerp', 'reduced-motion'],
        description:
          'Reglas de motion scroll-driven para sitios Sender: todo movimiento nace del scroll (scrub), lerp propio para video, un movimiento firma por sitio, rAF solo cuando el elemento es visible y apagado total con reduced-motion. Úsala al implementar o revisar animaciones ligadas al scroll.',
      },
      {
        source: 'sender-design-ops/skills/SKILL-qa-verify.md',
        slug: 'sender-qa-verify',
        category: 'diseno-web',
        tags: ['qa', 'lighthouse', 'ci', 'verificacion'],
        description:
          'Protocolo de QA duro antes de publicar: curl a producción con tag BUILD, conteo de marcadores, parse check de JS, rescates git sin force-push y CI con html-validate + Lighthouse. Úsala antes de anunciar o empujar un cambio.',
      },
      {
        source: 'sender-design-ops/skills/SKILL-video-pipeline.md',
        slug: 'sender-video-pipeline',
        category: 'video',
        tags: ['ffmpeg', 'scrub', 'gop', 'video'],
        description:
          'Pipeline ffmpeg para video e imagen web: GOP corto y faststart para que el scrub sea barato, presupuestos de peso por tipo de video, Ken Burns desde foto real y verificación con probe. Úsala al preparar backs de video, loops o derivados de imagen.',
      },
      {
        source: 'AGENTS.md',
        slug: 'scrollcraft-arena',
        category: 'diseno-web',
        tags: ['scrollcraft', 'entrevista', 'landing', 'scroll'],
        description:
          'Flujo ScrollCraft-Arena para construir landings premium scroll-driven/3D: entrevista obligatoria antes de codificar, principios anti-template, scroll como interfaz, assets reales, verificación previa a entregar y feedback por rondas. Úsala al iniciar un sitio nuevo o un rediseño inmersivo.',
      },
    ],
  },
  {
    repo: 'Rae',
    branch: 'main',
    discover: { root: 'agent/skills', file: 'SKILL.md' },
    classify(slug) {
      if (slug.startsWith('pixijs')) return { category: 'pixijs', tags: pixiTags };
      if (slug === 'motion-design') return { category: 'motion', tags: ['motion', 'ui', 'animacion'] };
      if (slug === 'text-to-lottie') return { category: 'motion', tags: ['lottie', 'animacion', 'svg'] };
      return { category: 'reverse-engineering', tags: reaTags };
    },
  },
  {
    repo: 'abysstattoo',
    branch: 'main',
    skills: [
      {
        source: '.agents/skills/abyss-video-image-studio',
        slug: 'abyss-video-image-studio',
        category: 'video',
        tags: ['video', 'color', 'ffmpeg', 'abyss'],
      },
    ],
    // Copias idénticas de Rae: se registran como duplicados, no se importan.
    skip: [
      '.agents/skills/reverse-engineer-anything',
      '.agents/skills/rea-changelog-update',
      '.agents/skills/rea-tool-design',
    ],
  },
  {
    repo: 'webopen',
    branch: 'main',
    skills: [
      {
        source: '.opencode/skills/design-sync/SKILL.md',
        slug: 'open-design-sync',
        category: 'flujo-trabajo',
        tags: ['open-design', 'tokens', 'componentes'],
        status: 'fixed',
      },
      {
        source: '.opencode/skills/git-workflow/SKILL.md',
        slug: 'multi-git-workflow',
        category: 'flujo-trabajo',
        tags: ['git', 'github', 'gitlab', 'commits'],
        status: 'fixed',
      },
      {
        source: '.opencode/skills/ultimate-web-designer/SKILL.md',
        slug: 'ultimate-web-designer',
        category: 'diseno-web',
        tags: ['ui', 'ux', 'tailwind', 'react'],
        status: 'fixed',
      },
    ],
  },
  {
    repo: 'scroll-craft',
    branch: 'main',
    // El repo se describe como «agent skill» pero no incluye SKILL.md.
    // Esta skill se redactó desde docs/ y los scripts del propio repo.
    curated: 'curated/scroll-craft',
    source: null,
    slug: 'scroll-craft',
    category: 'diseno-web',
    tags: ['scroll', 'gsap', 'lenis', 'threejs', 'i18n'],
    status: 'generated',
  },
];

export const INSTALL_TARGETS = {
  claude: '.claude/skills',
  agents: '.agents/skills',
  cursor: '.cursor/skills',
  opencode: '.opencode/skills',
  openclaw: 'skills',
};
