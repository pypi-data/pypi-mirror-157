import {
  IRouter,
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

/**
 * Initialization data for the jupyterlab-reset-fixer extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyterlab-reset-fixer:plugin',
  autoStart: true,
  requires: [IRouter],
  activate: (app: JupyterFrontEnd, router: IRouter) => {
    console.log('JupyterLab extension jupyterlab-reset-fixer is activated!');

    router.register({
      command: 'apputils:reset-on-load',
      pattern: /(\?reset|\&reset)(=?)($|&)/,
      rank: 20 // High priority: 20:100.
    });
  }
};

export default plugin;
