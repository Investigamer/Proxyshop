import "photoshop/dom/Document";
import type { Layer } from "photoshop/dom/Layer";

declare module "photoshop/dom/Document" {
  export interface Document {
    /**
     * @minVersion set 26.9
     */
    set activeLayers(layers: Layer[]);
  }
}
