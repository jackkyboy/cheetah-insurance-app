// /Users/apichet/Downloads/cheetah-insurance-app/src/utils/fieryCardRenderer.js
// /src/utils/fieryCardRenderer.js
import * as THREE from "three";

export function initFieryRenderer({ canvas, container }) {
  if (!canvas || !container) {
    console.warn("🔥 [FieryRenderer] Missing canvas or container.");
    return;
  }

  console.debug("🎨 [FieryRenderer] canvas:", canvas);
  console.debug("🎨 [FieryRenderer] container size:", container.offsetWidth, container.offsetHeight);

  const width = container.offsetWidth || 360;
  const height = container.offsetHeight || 360;

  const scene = new THREE.Scene();
  const camera = new THREE.OrthographicCamera(-width / 2, width / 2, height / 2, -height / 2, 1, 1000);
  camera.position.z = 10;

  const renderer = new THREE.WebGLRenderer({
    canvas,
    alpha: true,
    antialias: true,
  });

  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.setSize(width, height);
  renderer.setClearColor(0x000000, 0); // transparent background

  const uniforms = {
    time: { value: 0.0 },
    fireColorBase: { value: new THREE.Color(0xff5500) }, // 🔥 สีไฟแบบอบอุ่น
  };

  const geometry = new THREE.RingGeometry(60, 80, 64);
  const material = new THREE.ShaderMaterial({
    vertexShader: `
      varying vec2 vUv;
      void main() {
        vUv = uv;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: `
      uniform float time;
      uniform vec3 fireColorBase;
      varying vec2 vUv;

      void main() {
        float flicker = abs(sin(time + vUv.y * 10.0)) * 0.6 + 0.4;
        vec3 color = fireColorBase * flicker;
        gl_FragColor = vec4(color, 1.0);
      }
    `,
    uniforms,
    transparent: true,
    side: THREE.DoubleSide,
  });

  const fieryBandMesh = new THREE.Mesh(geometry, material);
  scene.add(fieryBandMesh);

  function animate() {
    uniforms.time.value += 0.02;
    renderer.render(scene, camera);
    requestAnimationFrame(animate);
  }

  animate();
}
