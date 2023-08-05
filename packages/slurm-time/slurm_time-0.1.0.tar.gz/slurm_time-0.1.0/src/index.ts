import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { IStatusBar } from '@jupyterlab/statusbar';
import { Widget } from '@lumino/widgets';

import { requestAPI } from './handler';

function formatRemaining(timedelta: number): string {
  const td = new Date(Date.UTC(0, 0, 0, 0, 0, 0, timedelta));
  return td.toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
}

/**
 * Initialization data for the slurm-time extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'slurm-time:plugin',
  autoStart: true,
  requires: [IStatusBar],
  activate: (app: JupyterFrontEnd, statusBar: IStatusBar) => {
    console.log('JupyterLab extension slurm-time activated');

    requestAPI<{ data?: { remaining: number }; error?: string }>('get_time')
      .then(data => {
        if (!data.data) {
          console.log('Could not load slurm time remaining: ' + data.error);
          return;
        } else {
          const endTime = new Date();
          endTime.setSeconds(endTime.getSeconds() + data.data.remaining);

          const statusWidget = new Widget();

          setInterval(() => {
            const now = new Date();
            const delta = endTime.getTime() - now.getTime();
            statusWidget.node.textContent = `Time remaining: ${formatRemaining(
              delta
            )}`;
          }, 1000);

          statusBar.registerStatusItem('lab-status', {
            align: 'middle',
            item: statusWidget
          });

          console.log(`Session will end at ${endTime}`);
        }
      })
      .catch(reason => {
        console.error(
          `The slurm_time server extension appears to be missing.\n${reason}`
        );
      });
  }
};

export default plugin;
