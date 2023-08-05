// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.

import { JupyterFrontEndPlugin } from '@jupyterlab/application';
import { ILatexTypesetter } from '@jupyterlab/rendermime';
import { PromiseDelegate } from '@lumino/coreutils';

declare let window: any;

/**
 * The MathJax 3 Typesetter.
 */
export class MathJax3Typesetter implements ILatexTypesetter {

  constructor() {
    this._init();
  }

  /**
   * Typeset the math in a node.
   */
  typeset(node: HTMLElement): void {

    void this._initPromise.promise.then(() => window.MathJax.typesetPromise([node]));
  }

  private _init() {
    window.MathJax = {
      tex: {
        inlineMath: [
          ['$', '$'],
          ['\\(', '\\)']
        ],
        displayMath: [
          ['$$', '$$'],
          ['\\[', '\\]']
        ],
        processEscapes: true,
        processEnvironments: true
      },
      startup: {
        typeset: false
      }
    };
    const head = document.getElementsByTagName('head')[0];
    const script = document.createElement('script');
    script.type = 'text/javascript';
    script.src = `${this._url}`;
    script.addEventListener('load', () => {
      this._initPromise.resolve();
    });
    head.appendChild(script);
  }

  private _initPromise = new PromiseDelegate<void>();
  private _url = "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js";
}

/**
 * The MathJax 3 extension.
 */
const mathJax3Plugin: JupyterFrontEndPlugin<ILatexTypesetter> = {
  id: 'jupyterlab-mathjax3-web:plugin',
  requires: [],
  provides: ILatexTypesetter,
  activate: () => new MathJax3Typesetter(),
  autoStart: true,
};

export default mathJax3Plugin;
