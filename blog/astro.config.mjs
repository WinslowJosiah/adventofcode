// @ts-check
import { rehypeHeadingIds } from "@astrojs/markdown-remark";
import mdx from "@astrojs/mdx";
import { defineConfig } from "astro/config";
import astroExpressiveCode from "astro-expressive-code";
import { pluginCollapsibleSections } from "@expressive-code/plugin-collapsible-sections";
import rehypeAutolinkHeadings from "rehype-autolink-headings";
// import rehypeMathjax from "rehype-mathjax";
import remarkDirective from "remark-directive";
import remarkDirectiveRehype from "remark-directive-rehype";
import remarkDirectiveSugar from "remark-directive-sugar";
import remarkMath from "remark-math";

import { pluginFrames as pluginFramesWithDelSuppress } from "./src/plugins/plugin-frames-with-del-suppress";
import { remarkAdmonitions } from "./src/plugins/remark-admonitions";
import rehypeMathjaxCopySvg from "./src/plugins/rehype-mathjax-copy-svg";

// https://astro.build/config
export default defineConfig({
  site: "https://aoc.winslowjosiah.com",
  integrations: [
    astroExpressiveCode({
      plugins: [
        // HACK I have a PR open to add this feature to Expressive Code, but
        // it's not been merged yet.
        pluginFramesWithDelSuppress({
          removeDeletedTextWhenCopying: true,
        }),
        pluginCollapsibleSections(),
      ],
      defaultProps: {
        collapseStyle: "collapsible-auto",
      },
      frames: false,
      styleOverrides: {
        codeFontFamily: (
          "'Fira Code', ui-monospace, SFMono-Regular, Menlo, Monaco, "
          + "Consolas, 'Liberation Mono', 'Courier New', monospace"
        ),
        codeFontSize: "0.75rem",
        uiFontSize: "0.85rem",
      },
      themes: ["one-dark-pro", "one-light"],
    }),
    mdx(),
  ],
  markdown: {
    gfm: true,
    remarkPlugins: [
      remarkDirective,
      // @ts-ignore: This plugin isn't typed correctly
      remarkDirectiveRehype,
      remarkDirectiveSugar,
      remarkAdmonitions,
      remarkMath,
    ],
    rehypePlugins: [
      rehypeHeadingIds,
      [
        rehypeAutolinkHeadings,
        {
          behavior: "wrap",
        },
      ],
      // HACK I want to be able to copy the LaTeX source from the SVGs that
      // MathJax renders. Copying their plugin and changing one part seems to be
      // the only way to do this without including the MathJax source on the
      // page and having the MathJax script render it on the client.
      rehypeMathjaxCopySvg,
    ],
  },
});