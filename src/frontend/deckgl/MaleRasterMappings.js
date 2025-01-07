// RasterMapping.js

export class RasterMapping {
    static rasterDisplayNames = [
      "Male Population Density",
      "Male Population Density Ages 0 To 4",
      "Male Population Density Ages 5 To 9",
      "Male Population Density Ages 10 To 14",
      "Male Population Density Ages 15 To 19",
      "Male Population Density Ages 20 To 24",
      "Male Population Density Ages 25 To 29",
      "Male Population Density Ages 30 To 34",
      "Male Population Density Ages 35 To 39",
      "Male Population Density Ages 40 To 44",
      "Male Population Density Ages 45 To 49",
      "Male Population Density Ages 50 To 54",
      "Male Population Density Ages 55 To 59",
      "Male Population Density Ages 60 To 64",
      "Male Population Density Ages 65 And Over",
      "Data Context",
      "Mean Administrative Unit Area",
      "Water Mask",
      "Land Area",
      "Water Area",
      "National Identifier Grid",
      "Data Code",
      "Input Data Year",
      "Input Data Level",
      "Input Sex Data Level",
      "Input Age Data Level",
      "Growth Rate Start Year",
      "Growth Rate End Year",
      "Growth Rate Administrative Level",
      "Year Of Most Recent Census"
    ];
  
    static getDisplayName(index) {
      return this.rasterDisplayNames[index - 1] || `Raster ${index}`;
    }
  }
  