import { defineCollection, z } from "astro:content";

const isProdBuild = import.meta.env.PROD;
const prodOnlyRule = (c: boolean) => (isProdBuild ? c : true);

const solutions = defineCollection({
  type: "content",
  schema: z.object({
    title: z.string().refine(t => prodOnlyRule(t !== ""), {
      message: "Missing post title during production build",
    }),
    day: z.number().gte(1).lte(25),
    year: z.number().gte(2015),
    pub_date: z.string().date().optional(),
    concepts: z.array(z.string()).optional(),
  }),
});

const concepts = defineCollection({
  type: "content",
  schema: z.object({
    title: z.string(),
    category: z.string().optional(),
  }),
});

export const collections = { solutions, concepts };