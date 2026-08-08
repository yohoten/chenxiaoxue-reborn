/**
 * 梦境信使 v2 — 深度融合 Messenger 球形探索玩法
 * WASD 行走 · 球形重力 · 第三人称相机 · NPC 对话 · 送信任务
 */
import { useEffect, useRef, useState, useCallback } from 'react';
import * as THREE from 'three';
import { PixelButton } from '../Common/PixelButton';

interface Quest { id: string; symbol: string; emoji: string; letter: string; target_npc: string; score: number; completed: boolean; }
interface NPC { id: string; name: string; emoji: string; role: string; position: [number, number, number]; }
interface GameWorld { planet: { radius: number; segments: number }; colors: { land: string; water: string; sky: string }; mood: string; objects: any[]; npcs: NPC[]; quests: Quest[]; game_mode: string; total_score: number; }

interface Props { dreamText?: string; symbols?: Array<{ symbol: string }>; }

export function DreamMessenger({ dreamText, symbols }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [world, setWorld] = useState<GameWorld | null>(null);
  const [score, setScore] = useState(0); const [delivered, setDelivered] = useState(0);
  const [activeQuest, setActiveQuest] = useState<Quest | null>(null);
  const [dialogue, setDialogue] = useState<string | null>(null);
  const [message, setMessage] = useState('WASD 移动 · E 与 NPC 对话 · 点击符号送达');
  const [gameOver, setGameOver] = useState(false); const [loading, setLoading] = useState(true);
  const keysRef = useRef<Set<string>>(new Set());

  useEffect(() => {
    import('../../services/api').then(({ generateMessengerWorld }) => {
      generateMessengerWorld(dreamText || '', symbols || [])
        .then(data => { setWorld(data); setLoading(false); })
        .catch(() => setLoading(false));
    });
  }, [dreamText]);

  const generateGradientMap = useCallback(() => {
    const canvas = document.createElement('canvas'); canvas.width = 4; canvas.height = 1;
    const ctx = canvas.getContext('2d')!;
    const gradient = ctx.createLinearGradient(0, 0, 4, 0);
    gradient.addColorStop(0, '#1a3a5c'); gradient.addColorStop(0.4, '#4a8a6c');
    gradient.addColorStop(0.7, '#8aca7c'); gradient.addColorStop(1, '#c8e8c0');
    ctx.fillStyle = gradient; ctx.fillRect(0, 0, 4, 1);
    const tex = new THREE.CanvasTexture(canvas); tex.minFilter = THREE.NearestFilter; tex.magFilter = THREE.NearestFilter;
    return tex;
  }, []);

  useEffect(() => {
    if (!world || !containerRef.current) return;
    const container = containerRef.current;
    const w = container.clientWidth || 500; const h = container.clientHeight || 450;
    const gradientMap = generateGradientMap();

    // ── 场景 ──
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(world.colors.sky);
    scene.fog = new THREE.Fog(world.colors.sky, 10, 30);

    const camera = new THREE.PerspectiveCamera(55, w / h, 0.5, 60);
    camera.position.set(0, 7, 10);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(w, h); renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    container.appendChild(renderer.domElement);

    // ── 光照 ──
    scene.add(new THREE.AmbientLight(0x8899cc, 0.9));
    const sun = new THREE.DirectionalLight(0xffeedd, 1.8);
    sun.position.set(15, 20, 8); sun.castShadow = true;
    scene.add(sun);

    // ── 星球 ──
    const R = world.planet.radius;
    const planetGeo = new THREE.IcosahedronGeometry(R, 4);
    const planetMat = new THREE.MeshToonMaterial({ color: new THREE.Color(world.colors.land), gradientMap });
    const planet = new THREE.Mesh(planetGeo, planetMat);
    planet.castShadow = true; planet.receiveShadow = true;
    scene.add(planet);

    // 水面
    const waterGeo = new THREE.IcosahedronGeometry(R + 0.06, 4);
    const water = new THREE.Mesh(waterGeo, new THREE.MeshPhongMaterial({ color: new THREE.Color(world.colors.water), transparent: true, opacity: 0.25, shininess: 90 }));
    scene.add(water);

    // ── 装饰：树木和小房子 ──
    const decorGroup = new THREE.Group();
    for (let i = 0; i < 40; i++) {
      const phi = Math.acos(2 * Math.random() - 1);
      const theta = Math.random() * Math.PI * 2;
      const sx = R * Math.sin(phi) * Math.cos(theta);
      const sy = R * Math.sin(phi) * Math.sin(theta);
      const sz = R * Math.cos(phi);

      // 树干
      const trunkH = 0.15 + Math.random() * 0.2;
      const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.05, trunkH, 6), new THREE.MeshToonMaterial({ color: 0x5a3a2a }));
      trunk.position.set(sx * 1.02, sy * 1.02, sz * 1.02);
      const normal = new THREE.Vector3(sx, sy, sz).normalize();
      trunk.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), normal);
      decorGroup.add(trunk);

      // 树冠
      const crownR = 0.08 + Math.random() * 0.12;
      const crownColor = Math.random() > 0.5 ? 0x4a8c3a : 0x6aaa4a;
      const crown = new THREE.Mesh(new THREE.ConeGeometry(crownR, 0.2, 8), new THREE.MeshToonMaterial({ color: crownColor }));
      crown.position.set(sx * 1.04, sy * 1.04 + trunkH, sz * 1.04);
      crown.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), normal);
      decorGroup.add(crown);
    }
    // 小房子
    for (let i = 0; i < 8; i++) {
      const phi = Math.acos(2 * Math.random() - 1);
      const theta = Math.random() * Math.PI * 2;
      const hx = R * Math.sin(phi) * Math.cos(theta);
      const hy = R * Math.sin(phi) * Math.sin(theta);
      const hz = R * Math.cos(phi);
      const normal = new THREE.Vector3(hx, hy, hz).normalize();

      const house = new THREE.Group();
      const body = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.18, 0.2), new THREE.MeshToonMaterial({ color: 0xddbb88 }));
      body.position.y = 0.09;
      house.add(body);
      const roof = new THREE.Mesh(new THREE.ConeGeometry(0.16, 0.12, 4), new THREE.MeshToonMaterial({ color: 0xcc6644 }));
      roof.position.y = 0.22;
      roof.rotation.y = Math.PI / 4;
      house.add(roof);
      house.position.set(hx * 1.03, hy * 1.03, hz * 1.03);
      house.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), normal);
      decorGroup.add(house);
    }
    scene.add(decorGroup);

    // ── NPC 居民 ──
    const npcMeshes: THREE.Mesh[] = [];
    const npcMap = new Map<THREE.Mesh, NPC>();
    world.npcs.forEach(npc => {
      const [x, y, z] = npc.position;
      const normal = new THREE.Vector3(x, y, z).normalize();
      const bodyGeo = new THREE.CapsuleGeometry(0.15, 0.35, 4, 8);
      const mat = new THREE.MeshToonMaterial({ color: npc.role === '解析中心' ? 0x4488ff : npc.role === '信使助手' ? 0x44ff88 : 0xff8844 });
      const mesh = new THREE.Mesh(bodyGeo, mat);
      mesh.position.copy(normal.clone().multiplyScalar(R + 0.35));
      mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), normal);
      mesh.castShadow = true;

      // 任务标记（三角形）
      const markGeo = new THREE.ConeGeometry(0.1, 0.15, 3);
      const mark = new THREE.Mesh(markGeo, new THREE.MeshBasicMaterial({ color: 0xffdd44 }));
      mark.position.copy(normal.clone().multiplyScalar(R + 0.65));
      mark.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), normal);
      scene.add(mark);
      (mesh as any).marker = mark;

      scene.add(mesh);
      npcMeshes.push(mesh);
      npcMap.set(mesh, npc);
    });

    // ── 符号对象 ──
    const symbolMeshes: THREE.Mesh[] = [];
    const symbolMap = new Map<THREE.Mesh, any>();
    world.objects.forEach(obj => {
      const [x, y, z] = obj.position;
      const normal = new THREE.Vector3(x, y, z).normalize();
      const geo = new THREE.SphereGeometry(obj.size, 12, 8);
      const mesh = new THREE.Mesh(geo, new THREE.MeshToonMaterial({ color: 0xffdd55 }));
      mesh.position.copy(normal.clone().multiplyScalar(R + 0.15));
      scene.add(mesh);
      symbolMeshes.push(mesh);
      symbolMap.set(mesh, obj);

      const ringGeo = new THREE.TorusGeometry(obj.size + 0.12, 0.03, 8, 16);
      const ring = new THREE.Mesh(ringGeo, new THREE.MeshBasicMaterial({ color: 0xffaa33, transparent: true, opacity: 0.6 }));
      ring.position.copy(mesh.position);
      ring.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), normal);
      scene.add(ring);
      (mesh as any).ring = ring;
    });

    // ── 玩家 ──
    const playerGroup = new THREE.Group();
    const playerBody = new THREE.Mesh(new THREE.CapsuleGeometry(0.12, 0.25, 4, 8), new THREE.MeshToonMaterial({ color: 0xffcc88 }));
    playerBody.position.y = 0.2;
    playerGroup.add(playerBody);
    const playerHead = new THREE.Mesh(new THREE.SphereGeometry(0.1, 8, 6), new THREE.MeshToonMaterial({ color: 0xffcc88 }));
    playerHead.position.y = 0.45;
    playerGroup.add(playerHead);
    // 初始位置：北极上方
    const playerPos = new THREE.Vector3(0, R + 0.5, 0);
    const playerNormal = new THREE.Vector3(0, 1, 0);
    playerGroup.position.copy(playerPos);
    playerGroup.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), playerNormal);
    scene.add(playerGroup);

    // ── 星空 ──
    const starsGeo = new THREE.BufferGeometry();
    const starsArr = new Float32Array(400 * 3);
    for (let i = 0; i < 400; i++) { starsArr[i * 3] = (Math.random() - 0.5) * 25; starsArr[i * 3 + 1] = (Math.random() - 0.5) * 25; starsArr[i * 3 + 2] = (Math.random() - 0.5) * 25; }
    starsGeo.setAttribute('position', new THREE.BufferAttribute(starsArr, 3));
    scene.add(new THREE.Points(starsGeo, new THREE.PointsMaterial({ color: 0xffffff, size: 0.05 })));

    // ── 键盘输入 ──
    const keys = keysRef.current;
    const onKeyDown = (e: KeyboardEvent) => { keys.add(e.key.toLowerCase()); if (e.key === 'e' || e.key === 'E') handleInteract(); };
    const onKeyUp = (e: KeyboardEvent) => keys.delete(e.key.toLowerCase());
    window.addEventListener('keydown', onKeyDown);
    window.addEventListener('keyup', onKeyUp);

    // ── NPC 交互 ──
    const handleInteract = () => {
      const pPos = playerGroup.position.clone().normalize().multiplyScalar(R + 0.4);
      for (const [mesh, npc] of npcMap) {
        if (mesh.position.distanceTo(pPos) < 0.7) {
          if (npc.role === '解析中心') {
            const pending = world.quests.filter(q => !q.completed);
            if (pending.length > 0) {
              const q = pending[Math.floor(Math.random() * pending.length)];
              setActiveQuest(q);
              setDialogue(`【${npc.name}】请把这封信送给 ${q.emoji} ${q.symbol}：${q.letter.slice(0, 40)}...`);
            } else { setDialogue(`【${npc.name}】所有信件都已送达！`); setGameOver(true); }
          } else {
            setDialogue(`【${npc.name}】你好，旅行者！我是${npc.role}。`);
          }
          return;
        }
      }
      // 检测符号送达
      if (activeQuest) {
        for (const [mesh, obj] of symbolMap) {
          if (mesh.position.distanceTo(pPos) < 0.5 && obj.symbol === activeQuest.symbol) {
            const q = world.quests.find(qq => qq.id === activeQuest.id);
            if (q) q.completed = true;
            const ns = score + activeQuest.score;
            setScore(ns); setDelivered(d => d + 1); setActiveQuest(null);
            setDialogue(`✅ 成功送达 ${obj.emoji} ${obj.symbol}！+${activeQuest.score} 分`);
            (mesh.material as THREE.MeshToonMaterial).color.set(0x44ff44);
            if ((mesh as any).ring) ((mesh as any).ring as THREE.Mesh).material = new THREE.MeshBasicMaterial({ color: 0x44ff44 });
            setTimeout(() => {
              const rem = world.quests.filter(qq => !qq.completed);
              if (rem.length === 0) { setGameOver(true); setDialogue(`🎉 全部送达！总分: ${ns}`); }
              else setDialogue(`还有 ${rem.length} 封待送，靠近 NPC 领取`);
            }, 2000);
            return;
          }
        }
      }
    };

    // ── 动画循环 ──
    let animId: number;
    const clock = new THREE.Clock();
    const animate = () => {
      animId = requestAnimationFrame(animate);
      const dt = Math.min(clock.getDelta(), 0.1);
      const speed = 2.5;
      let moved = false;

      // 玩家移动（球形重力）
      const moveDir = new THREE.Vector3();
      const camForward = new THREE.Vector3();
      camera.getWorldDirection(camForward);
      camForward.y = 0; camForward.normalize();
      const camRight = new THREE.Vector3().crossVectors(camForward, new THREE.Vector3(0, 1, 0)).normalize();

      if (keys.has('w') || keys.has('arrowup')) { moveDir.add(camForward); moved = true; }
      if (keys.has('s') || keys.has('arrowdown')) { moveDir.sub(camForward); moved = true; }
      if (keys.has('a') || keys.has('arrowleft')) { moveDir.sub(camRight); moved = true; }
      if (keys.has('d') || keys.has('arrowright')) { moveDir.add(camRight); moved = true; }

      if (moved) {
        moveDir.normalize();
        const angle = speed * dt / R;
        const axis = new THREE.Vector3().crossVectors(playerPos.clone().normalize(), moveDir).normalize();
        playerPos.applyAxisAngle(axis, angle);
        if (playerPos.y < -R * 0.95) playerPos.applyAxisAngle(new THREE.Vector3(1, 0, 0), angle); // 南极保护
        const newNormal = playerPos.clone().normalize();
        playerPos.copy(newNormal.clone().multiplyScalar(R + 0.5));
        playerGroup.position.copy(playerPos);
        playerGroup.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), newNormal);
      }

      // 第三人称相机
      const camTarget = playerPos.clone();
      const camOffset = playerPos.clone().normalize().multiplyScalar(4);
      camera.position.lerp(camTarget.clone().add(camOffset), 3 * dt);
      camera.lookAt(camTarget);

      // 缓慢自转
      planet.rotation.y += 0.001;
      water.rotation.y += 0.0012;
      decorGroup.rotation.y += 0.001;
      npcMeshes.forEach(m => { if ((m as any).marker) (m as any).marker.position.y += Math.sin(Date.now() * 0.003) * 0.002; });

      renderer.render(scene, camera);
    };
    animate();

    const onResize = () => { const cw = container.clientWidth; const ch = container.clientHeight; camera.aspect = cw / ch; camera.updateProjectionMatrix(); renderer.setSize(cw, ch); };
    window.addEventListener('resize', onResize);

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener('keydown', onKeyDown);
      window.removeEventListener('keyup', onKeyUp);
      window.removeEventListener('resize', onResize);
      container.removeChild(renderer.domElement);
      renderer.dispose(); scene.clear();
    };
  }, [world, score, delivered, activeQuest, gameOver, generateGradientMap]);

  if (loading) return <div style={{ padding: 40, textAlign: 'center', color: '#888' }}>生成梦境信使世界...</div>;
  if (!world) return <div style={{ padding: 40, textAlign: 'center', color: '#888' }}>请先解析梦境</div>;

  return (
    <div style={{ position: 'relative' }}>
      <div ref={containerRef} style={{ width: '100%', height: 420, borderRadius: 8, overflow: 'hidden', outline: 'none' }} tabIndex={0} />

      {/* HUD */}
      <div style={{ position: 'absolute', top: 0, left: 0, right: 0, background: 'linear-gradient(180deg, rgba(0,0,0,0.7), transparent)', padding: '6px 12px', display: 'flex', justifyContent: 'space-between', pointerEvents: 'none' }}>
        <span style={{ fontSize: 10, color: '#ccc' }}>🎯 {score}分 · ✉️ {delivered}/{world.quests.length}</span>
        <span style={{ fontSize: 9, color: '#888' }}>WASD 移动 · E 交互</span>
      </div>

      {/* 对话 */}
      {dialogue && (
        <div style={{ position: 'absolute', bottom: 50, left: '50%', transform: 'translateX(-50%)', background: 'rgba(10,10,30,0.95)', border: '2px solid #4a77c5', padding: '10px 20px', fontSize: 10, color: '#ccc', maxWidth: 380, textAlign: 'center', zIndex: 10, cursor: 'pointer' }} onClick={() => setDialogue(null)}>
          {dialogue}
          <div style={{ fontSize: 8, color: '#666', marginTop: 4 }}>点击关闭</div>
        </div>
      )}

      {/* 底部控制栏 */}
      <div style={{ position: 'absolute', bottom: 8, left: 8, right: 8, display: 'flex', justifyContent: 'center', gap: 8 }}>
        <PixelButton variant="nav" onClick={() => { setGameOver(false); setScore(0); setDelivered(0); setActiveQuest(null); setDialogue(null); world.quests.forEach(q => q.completed = false); }} style={{ fontSize: 9, padding: '3px 10px', minWidth: 0 }}>
          🔄 重置
        </PixelButton>
      </div>

      {gameOver && (
        <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 20 }}>
          <div style={{ background: '#1a1a2e', border: '3px solid #ffaa44', padding: 24, textAlign: 'center', maxWidth: 300 }}>
            <div style={{ fontSize: 36, marginBottom: 8 }}>🎉</div>
            <h3 style={{ fontSize: 14, color: '#ffaa44', marginBottom: 12 }}>全部信件已送达！</h3>
            <p style={{ fontSize: 11, color: '#ccc' }}>得分: {score} · 送达 {delivered} 封</p>
            <p style={{ fontSize: 10, color: '#888', margin: '8px 0 16px' }}>{score >= 60 ? '🌟 梦境大师' : score >= 30 ? '📬 资深信使' : '🌱 初入梦境'}</p>
            <PixelButton variant="primary" onClick={() => { setGameOver(false); setScore(0); setDelivered(0); world.quests.forEach(q => q.completed = false); }} style={{ fontSize: 10, padding: '6px 16px' }}>再来一局</PixelButton>
          </div>
        </div>
      )}
    </div>
  );
}

export default DreamMessenger;
