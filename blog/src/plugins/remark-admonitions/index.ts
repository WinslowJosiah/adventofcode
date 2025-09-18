import { type Properties } from "@expressive-code/core/hast";
import type {
  BlockContent,
  DefinitionContent,
  ParagraphData,
  PhrasingContent,
  Root,
} from "mdast";
import { type Directives } from "mdast-util-directive";
import { visit } from "unist-util-visit";

export interface RemarkAdmonitionsOptions {
  defaultElement?: string
  defaultProperties?: Properties
  types?: Map<string, Admonition>
}

export type Admonition = {
  defaultLabel?: string
  element?: string
  properties?: Properties
}

const DEFAULT_ADMONITION_TYPES = new Map<string, Admonition>([
  ["admonition", { defaultLabel: "Admonition" }],
  ["attention", { defaultLabel: "Attention" }],
  ["caution", { defaultLabel: "Caution" }],
  ["danger", { defaultLabel: "Danger" }],
  ["error", { defaultLabel: "Error" }],
  ["hint", { defaultLabel: "Hint" }],
  ["important", { defaultLabel: "Important" }],
  ["note", { defaultLabel: "Note" }],
  ["tip", { defaultLabel: "Tip" }],
  ["warning", { defaultLabel: "Warning" }],
]);

export function remarkAdmonitions(options: RemarkAdmonitionsOptions = {}) {
  const {
    defaultElement = "div",
    defaultProperties = {},
    types = DEFAULT_ADMONITION_TYPES,
  } = options;
  return (tree: Root) => {
    visit(tree, "containerDirective", (directive: Directives) => {
      const { name, data = {}, children } = directive;
      const type = types.get(name);
      if (!type) return;

      const [labelChild, contentChildren] =
        (children[0]?.data as ParagraphData)?.directiveLabel
        ? [children[0], children.slice(1)]
        : [
          {
            type: "paragraph",
            children: [
              { type: "text", value: type.defaultLabel },
            ],
          },
          children,
        ];

      directive.data = Object.assign(data, {
        hName: type.element ?? defaultElement,
        hProperties: {
          "data-admonition": name,
          ...defaultProperties,
          ...type.properties,
        },
      });
      directive.children = [
        labelChild,
        ...contentChildren,
      ] as (BlockContent | DefinitionContent)[] | PhrasingContent[];
    });
  };
};