// vite.config.js

import { defineConfig } from "vite";
import topLevelAwait from "vite-plugin-top-level-await";

export default defineConfig({
  resolve: {
    alias: {
      "three/examples/jsm": "three/examples/jsm",
      "three/addons": "three/examples/jsm",
      "three/tsl": "three/webgpu",
      three: "three/webgpu",
    },
  },
  // Apply the top-level await plugin to our vite.config.js
  plugins: [
    topLevelAwait({
      promiseExportName: "__tla",
      promiseImportName: (i) => `__tla_${i}`,
    }),
  ],
});
