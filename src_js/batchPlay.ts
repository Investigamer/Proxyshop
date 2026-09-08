import { action, core } from "photoshop";
import { ActionDescriptor } from "photoshop/dom/CoreModules";

const data: ActionDescriptor[] = [];

async function doBatchPlay() {
  return await action.batchPlay(data, {});
}
core.executeAsModal(doBatchPlay, {
  commandName: "Programmatic Batch Play",
});
