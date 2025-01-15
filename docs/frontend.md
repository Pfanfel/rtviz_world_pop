# Frontend

## Overview

This React TypeScript application visualizes geospatial data using a Mapbox and Deck.gl integration. The application allows users to:

- Visualize raster data on a map.
- Adjust visualization parameters dynamically, including raster selection, color value normalization, detail level, height scaling, and opacity.

### Technology Stack
- **Frontend Framework:** React with TypeScript
- **Map Visualization:** Mapbox GL and Deck.gl
- **Geospatial Layers:** Deck.gl Geo-layers (`TileLayer` and `QuadkeyLayer`)

### Mapbox

Mapbox is used as the base map provider to render map tiles and manage the overall map interface. Its key roles include: Base Map rendering and navigation control.


### Deck.gl 

is used to add custom and advanced layers on top of the Mapbox base map. The TileLayer is configured to fetch raster data dynamically from a backend API. The layer manages loading and rendering of tiles efficiently. The QuadkeyLayer visualizes geospatial data by mapping quadkeys to colors and elevations. 
Deck.gl allows layers to be updated dynamically by passing new props.

Deck.gl is used like in this example:

```
const tileLayerQkey = new TileLayer<DataType>({
  data: [
    `http://127.0.0.1:8000/api/male/{z}/{y}/{x}/${selectedRaster}/${detailLevel}/${heightLevel}/${maxValue}`,
  ],
  renderSubLayers: (props) => [
    new QuadkeyLayer<DataType>({
      data: props.data,
      getQuadkey: (d) => d.quadkey,
      getFillColor: (d) => { /* Map data values to colors */ },
      getElevation: (d) => d.value,
    }),
  ],
});
```




**Color is set by binning the normalized data:**

```
 getFillColor: (d) => {
            const normalizedValue = normalizer(d.value);
            const opacity = opacityGui;
            const colArr = [
              [255, 255, 229, opacity],
              [255, 247, 188, opacity],
              [254, 227, 145, opacity],
              [254, 196, 79, opacity],
              [251, 154, 41, opacity],
              [236, 112, 20, opacity],
              [204, 76, 2, opacity],
              [153, 52, 4, opacity],
              [102, 37, 6, opacity]
            ];
            const bin = Math.round(Math.min(normalizedValue * 8, 8));
            return new Uint8ClampedArray(colArr[bin]);
          },
```

**Using the Normalizer**

The `maxValue` can be set by the user
```
 const normalizer = (value: number) => {
    const min = 0;
    return (value - min) / (maxValue - min);
  };
```
