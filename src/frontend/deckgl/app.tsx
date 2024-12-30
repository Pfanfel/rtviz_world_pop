import React, { useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Map, NavigationControl, Popup, useControl } from 'react-map-gl';
import { MapboxOverlay as DeckOverlay, MapboxOverlayProps as DeckOverlayProps } from '@deck.gl/mapbox';
import 'mapbox-gl/dist/mapbox-gl.css';
import {TileLayer, QuadkeyLayer} from '@deck.gl/geo-layers';
import type {TileLayerPickingInfo} from '@deck.gl/geo-layers';






// Set your Mapbox token here or via environment variable
const MAPBOX_TOKEN: string | undefined = process.env.MapboxAccessToken; // eslint-disable-line

const INITIAL_VIEW_STATE = {
  latitude: 51.47,
  longitude: 0.45,
  zoom: 4,
  bearing: 0,
  pitch: 30
};


const MAP_STYLE = 'mapbox://styles/mapbox/light-v9';

interface DeckGLOverlayProps extends DeckOverlayProps {}

function DeckGLOverlay(props: DeckGLOverlayProps) {
  const overlay = useControl(() => new DeckOverlay(props));
  overlay.setProps(props);
  return null;
}

interface SelectedFeature {
  properties: {
    name: string;
    abbrev: string;
  };
  geometry: {
    coordinates: [number, number];
  };
}

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


const onTilesLoad = () => {
  console.log('Tiles loaded');
}


const tileLayerQkey = new TileLayer<DataType>({
    // https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#Tile_servers
    data: ['http://127.0.0.1:8000/api/male/{z}/{y}/{x}'],

    // Since these OSM tiles support HTTP/2, we can make many concurrent requests
    // and we aren't limited by the browser to a certain number per domain.
    maxRequests: 5,

    pickable: true,
    onViewportLoad: onTilesLoad,
    // https://wiki.openstreetmap.org/wiki/Zoom_levels
    minZoom: 0,
    maxZoom: 8,
    tileSize: 256,
    zoomOffset: devicePixelRatio === 1 ? -1 : 0,
    renderSubLayers: props => {
      const [[west, south], [east, north]] = props.tile.boundingBox;
      const {data, ...otherProps} = props;
      console.log(props.tile.zoom);

      return [
        new QuadkeyLayer<DataType>({
          data: data,
          id: `QuadkeyLayer-${props.tile.id}`, // Unique id for each layer
          extruded: true,
          getQuadkey: (d: DataType) => d.quadkey,
          getFillColor: (d: DataType) => [d.raster_1 * 128, (1 - d.raster_1) * 255, (1 - d.raster_1) * 255, 180],
          getElevation: (d: DataType) => d.raster_1,
          elevationScale: 1*props.tile.zoom,
          pickable: true
        })
      ];
    }
  });


function Root() {
  const [selected, setSelected] = useState<SelectedFeature | null>(null);

  const layers: any[] = [tileLayerQkey];

  return (
    <Map
      initialViewState={INITIAL_VIEW_STATE}
      mapStyle={MAP_STYLE}
      mapboxAccessToken={MAPBOX_TOKEN}
    >
      {selected && (
        <Popup
          key={selected.properties.name}
          anchor="bottom"
          style={{ zIndex: 10 }} /* position above deck.gl canvas */
          longitude={selected.geometry.coordinates[0]}
          latitude={selected.geometry.coordinates[1]}
        >
          {selected.properties.name} ({selected.properties.abbrev})
        </Popup>
      )}
      <DeckGLOverlay layers={layers} /* interleaved*/ />
      <NavigationControl position="top-left" />
    </Map>
  );
}

/* global document */
const container = document.body.appendChild(document.createElement('div'));
createRoot(container).render(<Root />);