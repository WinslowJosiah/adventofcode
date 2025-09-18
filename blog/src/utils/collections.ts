import { getCollection, type CollectionEntry } from "astro:content";

export type Solution = CollectionEntry<"solutions">;

const isProdBuild = import.meta.env.PROD;

export const isPublished = ({ data : { pub_date } }: Solution) =>
  isProdBuild ? Boolean(pub_date) : true;

// Show everything in dev; show only published solutions in prod
export const getPublishedSolutions = async () =>
  getCollection("solutions", isPublished);

export const getSolutionsByYear = async () => {
  const solutions = await getPublishedSolutions();

  return solutions.reduce((result, solution) => {
    if (!result.has(solution.data.year)) {
      result.set(solution.data.year, []);
    }
    result.get(solution.data.year)?.push(solution);
    return result;
  }, new Map<number, Solution[]>());
};

export type Concept = CollectionEntry<"concepts">;

export const getConcepts = async () => 
  getCollection("concepts");
