import React from 'react';
import {createRoot} from 'react-dom/client';

import DeckGL from '@deck.gl/react';
import {MapView, PickingInfo} from '@deck.gl/core';
import {TileLayer, QuadkeyLayer} from '@deck.gl/geo-layers';
import {BitmapLayer, PathLayer} from '@deck.gl/layers';

import type {Position, MapViewState} from '@deck.gl/core';
import type {TileLayerPickingInfo} from '@deck.gl/geo-layers';

const INITIAL_VIEW_STATE: MapViewState = {
  latitude: 47.65,
  longitude: 7,
  zoom: 4.5,
  maxZoom: 20,
  maxPitch: 89,
  bearing: 0
};

const COPYRIGHT_LICENSE_STYLE: React.CSSProperties = {
  position: 'absolute',
  right: 0,
  bottom: 0,
  backgroundColor: 'hsla(0,0%,100%,.5)',
  padding: '0 5px',
  font: '12px/20px Helvetica Neue,Arial,Helvetica,sans-serif'
};

const LINK_STYLE: React.CSSProperties = {
  textDecoration: 'none',
  color: 'rgba(0,0,0,.75)',
  cursor: 'grab'
};

type DataType = {
  quadkey: string;
  raster_1: number;
  raster_2: number;
  raster_3: number;
  raster_4: number;
  raster_5: number;
  raster_6: number;
  raster_7: number;
  raster_8: number;
  raster_9: number;
  raster_10: number;
  raster_11: number;
  raster_12: number;
  raster_13: number;
  raster_14: number;
  raster_15: number;
  raster_16: number;
  raster_17: number;
  raster_18: number;
  raster_19: number;
  raster_20: number;
  raster_21: number;
  raster_22: number;
  raster_23: number;
  raster_24: number;
  raster_25: number;
  raster_26: number;
  raster_27: number;
  raster_28: number;
  raster_29: number;
  raster_30: number;
};

/* global window */
const devicePixelRatio = (typeof window !== 'undefined' && window.devicePixelRatio) || 1;

function getTooltip({object}: PickingInfo<DataType>) {
  if (object) {
    const {quadkey, raster_1} = object;
    return `qqkey: ${quadkey} value: ${raster_1}`;
  }
  return null;
}

export default function App({
  showBorder = false,
  onTilesLoad
}: {
  showBorder?: boolean;
  onTilesLoad?: () => void;
}) {
  
  const tileLayerBitmap = new TileLayer<ImageBitmap>({
    // https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#Tile_servers
    data: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],

    // Since these OSM tiles support HTTP/2, we can make many concurrent requests
    // and we aren't limited by the browser to a certain number per domain.
    maxRequests: 20,

    pickable: true,
    onViewportLoad: onTilesLoad,
    highlightColor: [60, 60, 60, 40],
    // https://wiki.openstreetmap.org/wiki/Zoom_levels
    minZoom: 0,
    maxZoom: 14,
    tileSize: 256,
    zoomOffset: devicePixelRatio === 1 ? -1 : 0,
    renderSubLayers: props => {
      const [[west, south], [east, north]] = props.tile.boundingBox;
      const {data, ...otherProps} = props;
      console.log(props);

      return [
        new BitmapLayer(otherProps, {
          image: data,
          bounds: [west, south, east, north]
        })
      ];
    }
  });

  const tileLayerQkey = new TileLayer<DataType>({
    id: 'QuadkeyTileLayer',
    // https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#Tile_servers
    data: ['http://127.0.0.1:8000/api/male/{z}/{x}/{y}'],

    // Since these OSM tiles support HTTP/2, we can make many concurrent requests
    // and we aren't limited by the browser to a certain number per domain.
    maxRequests: 20,

    pickable: true,
    onViewportLoad: onTilesLoad,
    // https://wiki.openstreetmap.org/wiki/Zoom_levels
    minZoom: 0,
    maxZoom: 14,
    tileSize: 256,
    zoomOffset: devicePixelRatio === 1 ? -1 : 0,
    renderSubLayers: props => {
      const [[west, south], [east, north]] = props.tile.boundingBox;
      const {data, ...otherProps} = props;
      console.log(props);

      return [
        new QuadkeyLayer<DataType>({
          id: 'QuadkeyLayer',
          data: data,
          
          extruded: true,
          getQuadkey: (d: DataType) => d.quadkey,
          getFillColor: (d: DataType) => [d.raster_1 * 128, (1 - d.raster_1) * 255, (1 - d.raster_1) * 255, 180],
          getElevation: (d: DataType) => d.raster_1,
          elevationScale: 1000,
          pickable: true
        })
      ];
    }
  });

  return (
    <DeckGL
      layers={[tileLayerBitmap,tileLayerQkey]}
      views={new MapView({repeat: true})}
      initialViewState={INITIAL_VIEW_STATE}
      controller={true}
      getTooltip={getTooltip}
    >
      <div style={COPYRIGHT_LICENSE_STYLE}>
        {'© '}
        <a style={LINK_STYLE} href="http://www.openstreetmap.org/copyright" target="blank">
          OpenStreetMap contributors
        </a>
      </div>
    </DeckGL>
  );
}

export function renderToDOM(container: HTMLDivElement) {
  createRoot(container).render(<App />);
}
