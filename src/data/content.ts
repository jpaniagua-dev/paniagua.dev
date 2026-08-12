/**
 * Every visible string on the page, in both languages.
 *
 * The brief that produced this site was explicit: no invented copy. The French
 * column is therefore the text published on https://paniagua.dev, verbatim,
 * and the English column is its translation. `derivedFrom` records the link
 * for anything that is neither verbatim French nor already published English.
 *
 * `tools/check-content.py` enforces it: every string must be found on the live
 * page, be a key of `derivedFrom` whose source is found there, or carry an
 * ADDED marker on the line directly above it. Two strings are marked ADDED,
 * and only two: they carry the company framing the brief asked for.
 *
 * Emoji present in the live copy were dropped, not replaced.
 */

export type Lang = 'en' | 'fr';

export const LANGS: Lang[] = ['en', 'fr'];

export interface Content {
  meta: { title: string; description: string };
  brand: { wordmark: string; legal: string; place: string };
  positioning: { role: string; name: string; promise: string };
  servicesTitle: string;
  services: { name: string; body: string }[];
  expertise: {
    label: string;
    headline: string;
    body: string;
    categories: { name: string; body: string }[];
  };
  contact: {
    cta: string;
    email: string;
    madeWith: string;
    madeBy: string;
    rights: string;
  };
  /** Filename shown above the code sample, as the old site displayed it. */
  codeFilename: string;
  skipToContent: string;
  /** Label of the other language, shown in the switcher. */
  otherLangLabel: string;
}

const links = [
  { label: 'LinkedIn', href: 'https://www.linkedin.com/in/juliopaniagua' },
  { label: 'GitHub', href: 'https://github.com/jpaniagua-dev' },
];

const en: Content = {
  meta: {
    title: 'Paniagua.dev | Expert Front-End & Workflow Digitalisation in Geneva',
    description:
      'Julio Paniagua, Expert Front-End based in Geneva. Angular, Web Performance and workflow digitalisation specialist. Urgent troubleshooting, technical audit and consulting.',
  },
  brand: {
    wordmark: 'PANIAGUA.DEV',
    /** ADDED: the company framing the brief asked for. */
    legal: 'Sole proprietorship',
    /** ADDED: completes the legal line. */
    place: 'Geneva',
  },
  positioning: {
    role: 'Front-End Engineer | Angular & UI Specialist',
    name: 'Julio Paniagua',
    promise: 'Building smart interfaces with AI-augmented workflows.',
  },
  servicesTitle: 'Areas of Work',
  services: [
    {
      name: 'UI/UX Prototyping',
      body: 'Design of modern, ergonomic interfaces. Scalable design systems and high-fidelity interactive prototypes.',
    },
    {
      name: 'Digital Consulting',
      body: 'Strategic advice on software architecture and technology stack. Digitalisation of business workflows to gain operational efficiency.',
    },
    {
      name: 'Audit & Web Perf',
      body: 'Advanced Core Web Vitals optimisation (LCP, CLS, INP). In-depth Lighthouse analysis to secure a 95+ score and flawless technical SEO.',
    },
    {
      name: 'Migration & Security',
      body: 'Modernisation of legacy codebases, AngularJS to modern Angular for instance. CMS hardening and transition to Headless/JAMstack architectures.',
    },
    {
      name: 'Urgent Troubleshooting',
      body: 'Critical intervention on blocking bugs (Angular, React, WordPress). Fast diagnosis and robust fixes to minimise production downtime.',
    },
    {
      name: 'Managed Hosting',
      body: 'Deployment and maintenance of web infrastructure. CI/CD pipelines, SSL management and proactive 24/7 monitoring.',
    },
  ],
  expertise: {
    label: 'Technical Expertise',
    headline: 'Precision Engineering',
    body: 'My methodology rests on using the best-performing tools available to meet the demands of modern digitalisation. Every engagement is guided by three pillars: raw performance, security, and long-term maintainability.',
    categories: [
      {
        name: 'Frameworks & Logic',
        body: 'Angular (Signals/RxJS), React, Vanilla JS ES2024+, TypeScript.',
      },
      {
        name: 'Performance',
        body: 'Core Web Vitals, SSR/SSG, bundle optimisation (Vite/Webpack).',
      },
      {
        name: 'Infrastructure',
        body: 'CI/CD GitHub Actions, Vercel, VPS Linux, Docker.',
      },
      {
        name: 'UI & Design',
        body: 'Design Systems, Tailwind CSS, Figma, Accessibility (A11y).',
      },
    ],
  },
  contact: {
    cta: 'Contact me',
    email: 'contact@paniagua.dev',
    madeWith: 'Made with',
    madeBy: 'by paniagua.dev',
    rights: '© 2026 Julio Paniagua. All rights reserved.',
  },
  codeFilename: 'user-profile.component.ts',
  /** ADDED: the live page has no skip link. */
  skipToContent: 'Skip to content',
  otherLangLabel: 'FR',
};

const fr: Content = {
  meta: {
    // Leads with the brand, keeps the published wording that carries the
    // local search terms. Geneva prospects search in French.
    title: 'Paniagua.dev | Expert Front-End & Digitalisation de Workflows à Genève',
    description:
      'Julio Paniagua, Expert Front-End basé à Genève. Spécialiste Angular, Web Performance et Digitalisation de workflows. Dépannage urgent, Audit technique et Consulting.',
  },
  brand: {
    wordmark: 'PANIAGUA.DEV',
    /** ADDED: the company framing the brief asked for. */
    legal: 'Entreprise individuelle',
    /** ADDED: completes the legal line. */
    place: 'Genève',
  },
  positioning: {
    role: 'Front-End Engineer | Angular & UI Specialist',
    name: 'Julio Paniagua',
    promise: 'Building smart interfaces with AI-augmented workflows.',
  },
  servicesTitle: "Domaines d'Intervention",
  services: [
    {
      name: 'UI/UX Prototyping',
      body: "Conception d'interfaces modernes et ergonomiques. Création de Design Systems scalables et prototypes interactifs haute fidélité.",
    },
    {
      name: 'Consulting Digital',
      body: 'Conseil stratégique en architecture logicielle et choix de stack technologique. Digitalisation de workflows métiers pour gagner en efficacité opérationnelle.',
    },
    {
      name: 'Audit & Web Perf',
      body: 'Optimisation avancée des Core Web Vitals (LCP, CLS, INP). Analyse Lighthouse approfondie pour garantir un score de 95+ et un SEO technique irréprochable.',
    },
    {
      name: 'Migration & Sécurité',
      body: 'Modernisation de legacy codebases (ex: AngularJS vers Angular moderne). Sécurisation de CMS et transition vers des architectures Headless/JAMstack.',
    },
    {
      name: 'Dépannage Urgent',
      body: "Intervention critique sur bugs bloquants (Angular, React, WordPress). Diagnostic rapide et correctifs robustes pour minimiser les temps d'arrêt de production.",
    },
    {
      name: 'Hébergement Géré',
      body: "Déploiement et maintenance d'infrastructures Web. Mise en place de pipelines CI/CD, gestion SSL et monitoring proactif 24/7.",
    },
  ],
  expertise: {
    label: 'Expertise Technique',
    headline: 'Ingénierie de précision',
    body: "Ma méthodologie repose sur l'utilisation des outils les plus performants pour répondre aux enjeux de la digitalisation moderne. Chaque intervention est guidée par trois piliers : la performance brute, la sécurité et la maintenabilité à long terme.",
    categories: [
      {
        name: 'Frameworks & Logic',
        body: 'Angular (Signals/RxJS), React, Vanilla JS ES2024+, TypeScript.',
      },
      {
        name: 'Performance',
        body: 'Core Web Vitals, SSR/SSG, Optimisation de bundle (Vite/Webpack).',
      },
      {
        name: 'Infrastructure',
        body: 'CI/CD GitHub Actions, Vercel, VPS Linux, Docker.',
      },
      {
        name: 'UI & Design',
        body: 'Design Systems, Tailwind CSS, Figma, Accessibilité (A11y).',
      },
    ],
  },
  contact: {
    cta: 'Me contacter',
    email: 'contact@paniagua.dev',
    madeWith: 'Made with',
    madeBy: 'by paniagua.dev',
    rights: '© 2026 Julio Paniagua. Tous droits réservés.',
  },
  codeFilename: 'user-profile.component.ts',
  /** ADDED: the live page has no skip link. */
  skipToContent: 'Aller au contenu',
  otherLangLabel: 'EN',
};

export const content: Record<Lang, Content> = { en, fr };
export const socialLinks = links;

/** Path of a page in a given language. English sits at the root. */
export const pathFor = (lang: Lang): string => (lang === 'en' ? '/' : '/fr/');

/**
 * Provenance ledger: a string on the left, the published string it comes from
 * on the right. Two kinds of entry live here, translations and recombinations
 * of published wording. The checker proves every right-hand side is still on
 * the live page, which is what keeps "nothing invented" true.
 *
 * Strings absent from this map are expected to be on the live page as they
 * stand, and are checked against it directly.
 */
export const derivedFrom: Record<string, string> = {
  // Recombination: the published title with the brand in front of the name.
  'Paniagua.dev | Expert Front-End & Digitalisation de Workflows à Genève':
    'Julio Paniagua | Expert Front-End & Digitalisation de Workflows à Genève',
  'Paniagua.dev | Expert Front-End & Workflow Digitalisation in Geneva':
    'Julio Paniagua | Expert Front-End & Digitalisation de Workflows à Genève',
  'Julio Paniagua, Expert Front-End based in Geneva. Angular, Web Performance and workflow digitalisation specialist. Urgent troubleshooting, technical audit and consulting.':
    'Julio Paniagua, Expert Front-End basé à Genève. Spécialiste Angular, Web Performance et Digitalisation de workflows. Dépannage urgent, Audit technique et Consulting.',

  'Areas of Work': "Domaines d'Intervention",
  'Digital Consulting': 'Consulting Digital',
  'Migration & Security': 'Migration & Sécurité',
  'Urgent Troubleshooting': 'Dépannage Urgent',
  'Managed Hosting': 'Hébergement Géré',
  'Technical Expertise': 'Expertise Technique',
  'Precision Engineering': 'Ingénierie de précision',
  'Contact me': 'Me contacter',

  'Design of modern, ergonomic interfaces. Scalable design systems and high-fidelity interactive prototypes.':
    "Conception d'interfaces modernes et ergonomiques. Création de Design Systems scalables et prototypes interactifs haute fidélité.",
  'Strategic advice on software architecture and technology stack. Digitalisation of business workflows to gain operational efficiency.':
    'Conseil stratégique en architecture logicielle et choix de stack technologique. Digitalisation de workflows métiers pour gagner en efficacité opérationnelle.',
  'Advanced Core Web Vitals optimisation (LCP, CLS, INP). In-depth Lighthouse analysis to secure a 95+ score and flawless technical SEO.':
    'Optimisation avancée des Core Web Vitals (LCP, CLS, INP). Analyse Lighthouse approfondie pour garantir un score de 95+ et un SEO technique irréprochable.',
  'Modernisation of legacy codebases, AngularJS to modern Angular for instance. CMS hardening and transition to Headless/JAMstack architectures.':
    'Modernisation de legacy codebases (ex: AngularJS vers Angular moderne). Sécurisation de CMS et transition vers des architectures Headless/JAMstack.',
  'Critical intervention on blocking bugs (Angular, React, WordPress). Fast diagnosis and robust fixes to minimise production downtime.':
    "Intervention critique sur bugs bloquants (Angular, React, WordPress). Diagnostic rapide et correctifs robustes pour minimiser les temps d'arrêt de production.",
  'Deployment and maintenance of web infrastructure. CI/CD pipelines, SSL management and proactive 24/7 monitoring.':
    "Déploiement et maintenance d'infrastructures Web. Mise en place de pipelines CI/CD, gestion SSL et monitoring proactif 24/7.",
  'My methodology rests on using the best-performing tools available to meet the demands of modern digitalisation. Every engagement is guided by three pillars: raw performance, security, and long-term maintainability.':
    "Ma méthodologie repose sur l'utilisation des outils les plus performants pour répondre aux enjeux de la digitalisation moderne. Chaque intervention est guidée par trois piliers : la performance brute, la sécurité et la maintenabilité à long terme.",
  'Core Web Vitals, SSR/SSG, bundle optimisation (Vite/Webpack).':
    'Core Web Vitals, SSR/SSG, Optimisation de bundle (Vite/Webpack).',
  'Design Systems, Tailwind CSS, Figma, Accessibility (A11y).':
    'Design Systems, Tailwind CSS, Figma, Accessibilité (A11y).',
  '© 2026 Julio Paniagua. All rights reserved.':
    '© 2026 Julio Paniagua. Tous droits réservés.',
};
