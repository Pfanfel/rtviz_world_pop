import * as THREE from "three";
import {
  nodeObject,
  uniform,
  cubeTexture,
  Vector2,
  CylinderGeometry,
} from "three/tsl";

import { OrbitControls } from "three/addons/controls/OrbitControls.js";

import { TeapotGeometry } from "three/addons/geometries/TeapotGeometry.js";

import Stats from "three/addons/libs/stats.module.js";

class InstanceUniformNode extends THREE.Node {
  constructor() {
    super("vec3");

    this.updateType = THREE.NodeUpdateType.OBJECT;

    this.uniformNode = uniform(new THREE.Color());
  }

  update(frame) {
    const mesh = frame.object;

    const meshColor = mesh.color;

    this.uniformNode.value.copy(meshColor);
  }

  setup(/*builder*/) {
    return this.uniformNode;
  }
}

let stats;

let camera, scene, renderer;
let controls;

const objects = [];
const MAX_HEIGHT = 3;

init();

function init() {
  const container = document.createElement("div");
  document.body.appendChild(container);

  camera = new THREE.PerspectiveCamera(
    45,
    window.innerWidth / window.innerHeight,
    1,
    4000
  );
  camera.position.set(0, 0, 50);

  scene = new THREE.Scene();

  // Grid

  const helper = new THREE.GridHelper(1000, 40, 0x303030, 0x303030);
  helper.position.y = -75;
  scene.add(helper);

  // CubeMap

  const path = "textures/cube/SwedishRoyalCastle/";
  const format = ".jpg";
  const urls = [
    path + "px" + format,
    path + "nx" + format,
    path + "py" + format,
    path + "ny" + format,
    path + "pz" + format,
    path + "nz" + format,
  ];

  const cTexture = new THREE.CubeTextureLoader().load(urls);

  // Materials

  const instanceUniform = nodeObject(new InstanceUniformNode());
  const cubeTextureNode = cubeTexture(cTexture);

  const material = new THREE.MeshBasicNodeMaterial();
  material.colorNode = instanceUniform.add(cubeTextureNode);
  material.emissiveNode = instanceUniform.mul(cubeTextureNode);

  // Geometry

  //const geometry = new TeapotGeometry(50, 18);

  function hexGeometry(height, position) {
    let geo = new CylinderGeometry(1, 1, height, 6, 1, false);
    geo.translate(position.x, height * 0.5, position.y);

    return geo;
  }

  function tileToPosition(tileX, tileY) {
    return new Vector2((tileX + (tileY % 2) * 0.5) * 1.77, tileY * 1.535);
  }

  for (let i = 0, l = 20; i < l; i++) {
    for (let j = 0, l = 20; j < l; j++) {
      let position = tileToPosition(i, j);
      const geometry = new hexGeometry(MAX_HEIGHT, position);
      addMesh(geometry, material);
    }
  }

  //

  renderer = new THREE.WebGPURenderer({ antialias: true });
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setAnimationLoop(animate);
  container.appendChild(renderer.domElement);

  //

  controls = new OrbitControls(camera, renderer.domElement);
  controls.target.set(0, 0, 0);
  controls.minDistance = 1;
  controls.maxDistance = 1000;

  //

  stats = new Stats();
  container.appendChild(stats.dom);

  //

  window.addEventListener("resize", onWindowResize);
}

function addMesh(geometry, material) {
  const mesh = new THREE.Mesh(geometry, material);

  mesh.color = new THREE.Color(Math.random() * 0xffffff);
  /*   mesh.position.x = (objects.length % 4) * 200 - 300;
  mesh.position.z = Math.floor(objects.length / 4) * 200 - 200;

  mesh.rotation.x = Math.random() * 200 - 100;
  mesh.rotation.y = Math.random() * 200 - 100;
  mesh.rotation.z = Math.random() * 200 - 100; */

  objects.push(mesh);

  scene.add(mesh);
}

function onWindowResize() {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();

  renderer.setSize(window.innerWidth, window.innerHeight);
}

//

function animate() {
  /*   for (let i = 0, l = objects.length; i < l; i++) {
    const object = objects[i];

    object.rotation.x += 0.01;
    object.rotation.y += 0.005;
  } */
  // controls.update(); Do we need this?
  renderer.render(scene, camera);

  stats.update();
}
