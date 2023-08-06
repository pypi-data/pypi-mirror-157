// Distributed under the terms of the Modified BSD License.

import { JupyterFrontEndPlugin, JupyterFrontEnd } from '@jupyterlab/application';
import { ILatexTypesetter } from '@jupyterlab/rendermime';

import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { ICommandPalette } from '@jupyterlab/apputils';
import { IMainMenu } from '@jupyterlab/mainmenu';
import { PromiseDelegate, ReadonlyPartialJSONObject } from '@lumino/coreutils';

import { Setting } from './setting'

declare let window: any;

/**
 * The MathJax 3 Typesetter.
 */
export class MathJax3Typesetter implements ILatexTypesetter {

  /**
   * Only open the tex config access to the users.
   */
  private _texConfig: ReadonlyPartialJSONObject = null;
  private _typesetPromise: Promise<any> = null;
  private _initPromise = new PromiseDelegate<void>();
  private _url = "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js";

  /**
   * Typeset the math in a node.
   */
  public typeset(node: HTMLElement): void {
    window.MathJax.texReset([0])
    this._typesetPromise = this._typesetPromise.then(() => {
      return window.MathJax.typesetPromise([node]);
    })
  }

  set config(config: ReadonlyPartialJSONObject) {
    this._texConfig = config;
  }

  public load() {
    window.MathJax = {
      startup: {
        typeset: false
      }
    };
    window.MathJax.tex = this._texConfig;
    const head = document.getElementsByTagName('head')[0];
    const script = document.createElement('script');
    script.type = 'text/javascript';
    script.src = `${this._url}`;
    script.addEventListener('load', () => {
      this._initPromise.resolve();
    });
    this._typesetPromise = this._initPromise.promise;
    head.appendChild(script);
  }
}

/**
 * The MathJax 3 extension.
 */
const Mathjax3Plugin: JupyterFrontEndPlugin<ILatexTypesetter> = {
  id: 'jupyterlab-mathjax3-web:plugin',
  requires: [ISettingRegistry, ICommandPalette, IMainMenu],
  provides: ILatexTypesetter,
  autoStart: true,

  activate: async (
    app: JupyterFrontEnd,
    settings: ISettingRegistry,
    palette: ICommandPalette,
    menu: IMainMenu
  ) => {
    const { commands } = app;
    let plugin = new MathJax3Typesetter();

    await settings
      .load(Mathjax3Plugin.id)
      .then(setting => {
        plugin.config = setting.composite;
      })
      .catch(console.warn);

    commands.addCommand(Setting.editConfig, {
      label: 'Mathjax 3 Config...',
      execute: args => {
        commands.execute('settingeditor:open');
      }
    })

    // Settings menu
    menu.settingsMenu.addGroup([
      { command: Setting.editConfig }
    ], 50)

    // Palatte entry
    palette.addItem({
      command: Setting.editConfig,
      category: Setting.category
    });

    plugin.load();
    return plugin;
  }
};

export default Mathjax3Plugin;
