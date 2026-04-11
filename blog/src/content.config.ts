import { defineCollection } from "astro:content";
import { glob } from "astro/loaders";
import { z } from "astro/zod";

const isProdBuild = import.meta.env.PROD;
const prodOnlyRule = (c: boolean) => (isProdBuild ? c : true);

const solutions = defineCollection({
  loader: glob({ pattern: "**/[^_]*.{md,mdx}", base: "./src/content/solutions" }),
  schema: z.object({
    title: z.string().refine(t => prodOnlyRule(t !== ""), {
      message: "Missing post title during production build",
    }),
    day: z.number().gte(1).lte(25),
    year: z.number().gte(2015),
    pub_date: z.iso.date().optional(),
    concepts: z.array(z.string()).optional(),
  }),
});

const concepts = defineCollection({
  loader: glob({ pattern: "**/[^_]*.{md,mdx}", base: "./src/content/concepts" }),
  schema: z.object({
    title: z.string(),
    category: z.string().optional(),
  }),
});

export const collections = { solutions, concepts };