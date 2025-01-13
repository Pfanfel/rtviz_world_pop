import React, { useState, useCallback } from 'react';
import { createRoot } from 'react-dom/client';
import { Map, NavigationControl, Popup, useControl } from 'react-map-gl';
import { MapboxOverlay as DeckOverlay, MapboxOverlayProps as DeckOverlayProps } from '@deck.gl/mapbox';
import 'mapbox-gl/dist/mapbox-gl.css';
import { TileLayer, QuadkeyLayer } from '@deck.gl/geo-layers';
import { RasterMapping } from './MaleRasterMappings';
/* global window */
const MAPBOX_TOKEN: string | undefined = "pk.eyJ1Ijoia3V0cSIsImEiOiJjbTQ3ODk3NzQwMzBuMm9zOXh2Z3kzZ2o1In0.UKsaCjiqJmRJkhxDZpC-CQ"; // eslint-disable-line

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

type DataType = {
  quadkey: string;
  value: number;
};

const devicePixelRatio = (typeof window !== 'undefined' && window.devicePixelRatio) || 1;

function Root() {
  const [selected, setSelected] = useState<DataType | null>(null);
  const [selectedRaster, setSelectedRaster] = useState<number>(1); // Default raster is 1
  const [maxValue, setMaxValue] = useState<number>(50); // Default max value for normalization
  const [detailLevel, setDetailLevel] = useState<number>(5); // Default detail level is 1
  const [heightLevel, setHeightLevel] = useState<number>(1); // Default height level is 2
  const [opacityGui, setOpacity] = useState<number>(120); // Default opacity is 120

  

  const normalizer = (value: number) => {
    const min = 0;
    return (value - min) / (maxValue - min);
  };

  const tileLayerQkey = new TileLayer<DataType>({
    data: [`http://127.0.0.1:8000/api/male/{z}/{y}/{x}/${selectedRaster}/${detailLevel}/${heightLevel}/${maxValue}`], // heightLevel, maxValue are only used for update it is stupid i know
    maxRequests: 20,
    pickable: true,
    minZoom: 0,
    maxZoom: 7,
    tileSize: 256,
    zoomOffset: devicePixelRatio === 1 ? -1 : 0,
    renderSubLayers: (props) => {
      console.log(props.tile.zoom , detailLevel)
      return [
        new QuadkeyLayer<DataType>({
          data: props.data,
          id: `QuadkeyLayer-${props.tile.id}`,
          extruded: true,
          updateTriggers: { // did not work sadly
            getFillColor: maxValue, // Trigger rerender when maxValue changes
            elevationScale: heightLevel, // Trigger rerender when heightLevel changes
          },
          getQuadkey: (d: DataType) => d.quadkey,
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
          getElevation: (d: DataType) => d.value,
          elevationScale: 1000 / (props.tile.zoom * heightLevel),
          pickable: true,
        
        })
      ];
    }
  });

  const layers: any[] = [tileLayerQkey];

  const handleRasterChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedRaster(parseInt(event.target.value, 10));
  };

  const handleMaxValueChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setMaxValue(parseFloat(event.target.value));
  };

  const handleOpacityChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setOpacity(parseFloat(event.target.value));
  };
  
  const handleHeightLevelChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setHeightLevel(parseFloat(event.target.value));
  };

  const handleDetailLevelChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setDetailLevel(parseInt(event.target.value, 10));
  };



  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      <header
        style={{ padding: "10px", backgroundColor: "#f0f0f0", zIndex: 10 }}
      >
        <label htmlFor="raster-select" style={{ marginRight: "10px" }}>Select Raster: </label>
        <select
          id="raster-select"
          value={selectedRaster}
          onChange={handleRasterChange}
          style={{ padding: "5px", fontSize: "16px", marginRight: "20px" }}
        >
          {RasterMapping.rasterDisplayNames.map((name, index) => (
            <option key={index + 1} value={index + 1}>
              {name}
            </option>
          ))}
        </select>

        <label htmlFor="max-value" style={{ marginRight: "10px" }}>Color Value: </label>
        <input
          id="max-value"
          type="number"
          value={maxValue}
          onChange={handleMaxValueChange}
          style={{ padding: "5px", fontSize: "16px", marginRight: "20px" }}
        />

      <label htmlFor="max-value" style={{ marginRight: "10px" }}>Opacity Value: </label>
        <input
          id="opacity-value"
          type="number"
          value={opacityGui}
          onChange={handleOpacityChange}
          style={{ padding: "5px", fontSize: "16px", marginRight: "20px" }}
        />
      
        <label htmlFor="detail-level" style={{ marginRight: "10px" }}>Detail Level: </label>
        <select
          id="detail-level"
          value={detailLevel}
          onChange={handleDetailLevelChange}
          style={{ padding: "5px", fontSize: "16px", marginRight: "20px" }}
        >
          {Array.from({ length: 7 }, (_, i) => i + 1).map((level) => (
            <option key={level} value={level}>
              {`Level ${level}`}
            </option>
          ))}
        </select>

        <label htmlFor="height-level" style={{ marginRight: "10px" }}>Height Level: </label>
        <input
          id="height-level"
          type="number"
          value={heightLevel}
          onChange={handleHeightLevelChange}
          style={{ padding: "5px", fontSize: "16px", marginRight: "20px" }}
        />

      </header>

      

      <Map
        initialViewState={INITIAL_VIEW_STATE}
        mapStyle={MAP_STYLE}
        mapboxAccessToken={MAPBOX_TOKEN}
      >
        <DeckGLOverlay layers={layers}/>
        <NavigationControl position="top-left" />
      </Map>
    </div>
  );
}

/* global document */
const container = document.body.appendChild(document.createElement('div'));
createRoot(container).render(<Root />);
