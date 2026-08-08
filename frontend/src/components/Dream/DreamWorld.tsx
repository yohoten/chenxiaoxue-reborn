/**
 * 梦境世界 3D 组件
 * 球形低多边形星球 + 梦境符号对象 + 可旋转探索
 * 参考 Messenger 的球形世界设计
 */
import { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';

interface WorldObject {
  id: number;
  symbol: string;
  emoji: string;
  interpretation: string;
  position: [number, number, number];
  size: number;
}

interface WorldData {
  planet: { radius: number; segments: number };
  colors: { land: string; water: string; sky: string };
  mood: string;
  objects: WorldObject[];
}

interface Props {
  dreamText?: string;
  symbols?: Array<{ symbol: string }>;
  worldData?: WorldData | null;
  onLoadWorld?: () => Promise<WorldData | null>;
}

export function DreamWorld({ dreamText, symbols, worldData: initialData }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [worldData, setWorldData] = useState<WorldData | null>(initialData || null);
  const [selectedObject, setSelectedObject] = useState<WorldObject | null>(null);
  const [loading, setLoading] = useState(!initialData);

  // 从 API 加载世界数据
  useEffect(() => {
    if (initialData || !dreamText) return;
    setLoading(true);
    import('../../services/api').then(({ generateDreamWorld }) => {
      generateDreamWorld(dreamText, symbols || [])
        .then(data => { setWorldData(data); setLoading(false); })
        .catch(() => setLoading(false));
    });
  }, [dreamText]);

  // Three.js 渲染
  useEffect(() => {
    if (!worldData || !containerRef.current) return;

    const container = containerRef.current;
    const width = container.clientWidth || 500;
    const height = container.clientHeight || 400;

    // 场景
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(worldData.colors.sky);
    scene.fog = new THREE.Fog(worldData.colors.sky, 8, 25);

    // 相机
    const camera = new THREE.PerspectiveCamera(50, width / height, 0.5, 50);
    camera.position.set(0, 6, 8);
    camera.lookAt(0, 0, 0);

    // 渲染器
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    container.appendChild(renderer.domElement);

    // 光照
    const ambientLight = new THREE.AmbientLight(0x404060, 1.2);
    scene.add(ambientLight);
    const directionalLight = new THREE.DirectionalLight(0xffffff, 1.5);
    directionalLight.position.set(10, 15, 5);
    directionalLight.castShadow = true;
    scene.add(directionalLight);

    // 星球
    const planetGeo = new THREE.IcosahedronGeometry(worldData.planet.radius, 3);
    const planetMat = new THREE.MeshToonMaterial({
      color: new THREE.Color(worldData.colors.land),
      gradientMap: null,
    });
    const planet = new THREE.Mesh(planetGeo, planetMat);
    planet.castShadow = true;
    planet.receiveShadow = true;
    scene.add(planet);

    // 水面层（稍大半透明）
    const waterGeo = new THREE.IcosahedronGeometry(worldData.planet.radius + 0.05, 3);
    const waterMat = new THREE.MeshPhongMaterial({
      color: new THREE.Color(worldData.colors.water),
      transparent: true,
      opacity: 0.3,
      shininess: 90,
    });
    const water = new THREE.Mesh(waterGeo, waterMat);
    scene.add(water);

    // 符号对象
    const symbolMeshes: THREE.Mesh[] = [];
    const objectMap = new Map<THREE.Mesh, WorldObject>();

    worldData.objects.forEach(obj => {
      const geo = new THREE.SphereGeometry(obj.size, 12, 8);
      const mat = new THREE.MeshToonMaterial({ color: 0xffdd55 });
      const mesh = new THREE.Mesh(geo, mat);

      const [x, y, z] = obj.position;
      mesh.position.set(x, y, z);
      mesh.castShadow = true;
      mesh.userData = obj;
      objectMap.set(mesh, obj);

      // 浮动光环
      const ringGeo = new THREE.TorusGeometry(obj.size + 0.15, 0.04, 8, 16);
      const ringMat = new THREE.MeshBasicMaterial({ color: 0xffaa33, transparent: true, opacity: 0.6 });
      const ring = new THREE.Mesh(ringGeo, ringMat);
      ring.position.copy(mesh.position);
      ring.userData = { floatOffset: Math.random() * Math.PI * 2 };
      scene.add(ring);
      (mesh as any).ring = ring;

      scene.add(mesh);
      symbolMeshes.push(mesh);
    });

    // 粒子星空
    const starsGeo = new THREE.BufferGeometry();
    const starsCount = 300;
    const starsPos = new Float32Array(starsCount * 3);
    for (let i = 0; i < starsCount; i++) {
      starsPos[i * 3] = (Math.random() - 0.5) * 20;
      starsPos[i * 3 + 1] = (Math.random() - 0.5) * 20;
      starsPos[i * 3 + 2] = (Math.random() - 0.5) * 20;
    }
    starsGeo.setAttribute('position', new THREE.BufferAttribute(starsPos, 3));
    const starsMat = new THREE.PointsMaterial({ color: 0xffffff, size: 0.05, transparent: true, opacity: 0.7 });
    const stars = new THREE.Points(starsGeo, starsMat);
    scene.add(stars);

    // 射线检测（点击符号对象）
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();
    const onPointerDown = (e: MouseEvent) => {
      const rect = container.getBoundingClientRect();
      mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(symbolMeshes);
      if (intersects.length > 0) {
        const obj = objectMap.get(intersects[0].object as THREE.Mesh);
        if (obj) setSelectedObject(obj);
      }
    };
    renderer.domElement.addEventListener('pointerdown', onPointerDown);

    // 拖拽旋转
    let isDragging = false;
    let prevX = 0;
    let prevY = 0;
    let rotY = 0;
    let rotX = 0;

    const onPointerMove = (e: MouseEvent) => {
      if (!isDragging) return;
      const dx = (e.clientX - prevX) * 0.005;
      const dy = (e.clientY - prevY) * 0.005;
      planet.rotation.y += dx;
      planet.rotation.x = Math.max(-Math.PI / 4, Math.min(Math.PI / 4, planet.rotation.x + dy));
      water.rotation.copy(planet.rotation);
      symbolMeshes.forEach(m => {
        // 符号跟随星球旋转
        const orig = objectMap.get(m);
        if (orig) {
          const pos = new THREE.Vector3(...orig.position);
          pos.applyAxisAngle(new THREE.Vector3(0, 1, 0), dx);
          m.position.copy(pos);
          if ((m as any).ring) (m as any).ring.position.copy(pos);
        }
      });
      prevX = e.clientX;
      prevY = e.clientY;
    };

    renderer.domElement.addEventListener('pointermove', onPointerMove);
    renderer.domElement.addEventListener('pointerdown', (e) => {
      isDragging = true;
      prevX = e.clientX;
      prevY = e.clientY;
    });
    renderer.domElement.addEventListener('pointerup', () => { isDragging = false; });
    renderer.domElement.style.cursor = 'grab';

    // 动画循环
    let animId: number;
    const animate = () => {
      animId = requestAnimationFrame(animate);

      // 缓慢自转
      planet.rotation.y += 0.002;
      water.rotation.y += 0.0025;

      // 符号浮动动画
      symbolMeshes.forEach(m => {
        const ring = (m as any).ring;
        if (ring) {
          ring.rotation.z += 0.01;
          ring.position.y += Math.sin(Date.now() * 0.002 + ring.userData.floatOffset) * 0.002;
        }
      });

      stars.rotation.y += 0.0003;
      renderer.render(scene, camera);
    };
    animate();

    // 窗口调整
    const onResize = () => {
      const w = container.clientWidth || 500;
      const h = container.clientHeight || 400;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener('resize', onResize);

    return () => {
      cancelAnimationFrame(animId);
      renderer.domElement.removeEventListener('pointerdown', onPointerDown);
      window.removeEventListener('resize', onResize);
      container.removeChild(renderer.domElement);
      renderer.dispose();
      scene.clear();
    };
  }, [worldData]);

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 400, color: '#888', fontSize: 12 }}>
        生成梦境世界中...
      </div>
    );
  }

  if (!worldData) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 400, color: '#888', fontSize: 11, textAlign: 'center' }}>
        请先解析梦境以生成 3D 梦境世界
      </div>
    );
  }

  return (
    <div style={{ position: 'relative' }}>
      {/* 3D 画布 */}
      <div ref={containerRef} style={{ width: '100%', height: 400, borderRadius: 8, overflow: 'hidden' }} />

      {/* 提示 */}
      <div style={{ position: 'absolute', top: 8, left: 12, fontSize: 9, color: '#888', pointerEvents: 'none' }}>
        🖱 拖拽旋转星球 · 点击符号查看解读
      </div>

      {/* 情绪标签 */}
      <div style={{
        position: 'absolute', bottom: 8, right: 12,
        background: 'rgba(0,0,0,0.5)', padding: '4px 10px',
        fontSize: 10, color: '#ccc', borderRadius: 4, pointerEvents: 'none',
      }}>
        🌍 {worldData.mood} · {worldData.objects.length} 个符号
      </div>

      {/* 符号详情弹窗 */}
      {selectedObject && (
        <div style={{
          position: 'absolute', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.6)', display: 'flex', alignItems: 'center', justifyContent: 'center',
        }} onClick={() => setSelectedObject(null)}>
          <div style={{
            background: '#1a1a2e', border: '3px solid #4a77c5',
            padding: 20, maxWidth: 320, width: '90%',
          }} onClick={e => e.stopPropagation()}>
            <div style={{ fontSize: 36, textAlign: 'center', marginBottom: 8 }}>
              {selectedObject.emoji}
            </div>
            <h4 style={{ textAlign: 'center', fontSize: 13, marginBottom: 12, color: '#3a7bd5' }}>
              {selectedObject.symbol}
            </h4>
            <p style={{ fontSize: 11, lineHeight: 1.8, color: '#ccc' }}>
              {selectedObject.interpretation}
            </p>
            <button
              className="pixel-btn"
              onClick={() => setSelectedObject(null)}
              style={{ width: '100%', marginTop: 14, fontSize: 10 }}
            >
              关闭
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default DreamWorld;
