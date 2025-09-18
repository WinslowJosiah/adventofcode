import {SVG as Svg} from 'mathjax-full/js/output/svg.js'
import {createPlugin} from './create-plugin.js'
import {createRenderer} from './create-renderer.js'

/**
 * Render elements with a `language-math` (or `math-display`, `math-inline`)
 * class with MathJax using SVG.
 *
 * @param [options]
 *   Configuration (optional).
 * @returns
 *   Transform.
 */
const rehypeMathJaxSvg = createPlugin(function (options) {
  Svg.prototype.toDOM = function(math, node, html = null) {
    this.setDocument(html);
    this.math = math;
    this.pxPerEm = math.metrics.ex / this.font.params.x_height;
    math.root.setTeXclass(null);
    this.setScale(node);
    this.nodeMap = new Map();
    this.container = node;
    this.processMath(math.root, node);

    // HACK Append copyable version of SVG
    var [startDelim, endDelim] = math.display ? ["$$\n", "\n$$"] : ["$", "$"];
    var text = this.html(
      "mjx-copytext",
      {"aria-hidden": true, style: {"white-space": "pre-wrap"}},
      [this.text(startDelim + this.math.math + endDelim)],
    );
    this.adaptor.append(this.container, text);

    this.nodeMap = null;
    this.executeFilters(this.postFilters, math, html, node);
  };

  // MathJax types do not allow `null`.
  return createRenderer(options, new Svg(options.svg || undefined))
})

export default rehypeMathJaxSvg
