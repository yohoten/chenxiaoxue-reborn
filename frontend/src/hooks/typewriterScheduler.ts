/**
 * 全局打字机调度器 — 单 rAF 驱动所有活跃气泡
 * 替代每气泡独立的 setInterval，避免 N 个定时器同时运行
 */

type TickFn = () => boolean; // 返回 true = 已完成，可从调度器移除

class TypewriterScheduler {
  private tasks = new Set<TickFn>();
  private rafId = 0;
  private lastTick = 0;
  private readonly interval = 30; // ms

  add(fn: TickFn) {
    this.tasks.add(fn);
    if (!this.rafId) this.start();
  }

  remove(fn: TickFn) {
    this.tasks.delete(fn);
    if (this.tasks.size === 0) this.stop();
  }

  private start() {
    const loop = (now: number) => {
      if (now - this.lastTick >= this.interval) {
        this.lastTick = now;
        for (const fn of [...this.tasks]) {
          if (fn()) this.tasks.delete(fn);
        }
        if (this.tasks.size === 0) { this.stop(); return; }
      }
      this.rafId = requestAnimationFrame(loop);
    };
    this.rafId = requestAnimationFrame(loop);
  }

  private stop() {
    cancelAnimationFrame(this.rafId);
    this.rafId = 0;
  }
}

export const typewriterScheduler = new TypewriterScheduler();
