/**
 * Chen筱雪 Reborn - Tauri 桌面壳入口
 *
 * 负责启动 WebView 窗口，指向 Vite 开发的 React 前端。
 * 后端 FastAPI 作为独立进程运行（由外部或 Tauri sidecar 管理）。
 */

use tauri::Manager;

#[tauri::command]
fn greet(name: &str) -> String {
    format!("你好，{}！欢迎回到陈筱雪的世界 ✨", name)
}

/// 应用配置
#[derive(serde::Serialize)]
struct AppConfig {
    name: String,
    version: String,
    backend_url: String,
}

#[tauri::command]
fn get_app_config() -> AppConfig {
    AppConfig {
        name: "陈筱雪 Reborn".to_string(),
        version: "1.0.0".to_string(),
        backend_url: "http://localhost:8000".to_string(),
    }
}

pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .invoke_handler(tauri::generate_handler![greet, get_app_config])
        .setup(|app| {
            #[cfg(debug_assertions)]
            {
                let window = app.get_webview_window("main").unwrap();
                window.open_devtools();
            }
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("启动陈筱雪失败");
}
