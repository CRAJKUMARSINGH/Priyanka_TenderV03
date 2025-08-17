use std::path::PathBuf;
use tauri::{command, Window};
use serde::{Serialize, Deserialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct FileData {
    pub path: String,
    pub contents: Vec<u8>,
}

#[command]
pub async fn open_file_dialog(window: Window) -> Result<Option<String>, String> {
    let file_path = window.open_file_dialog(Some(tauri::FileDialogBuilder::new()
        .add_filter("Excel files", &["xlsx", "xls"])
    ))
    .await
    .ok_or_else(|| "No file selected".to_string())?;

    Ok(Some(file_path))
}

#[command]
pub async fn read_file(path: String) -> Result<FileData, String> {
    let path_buf = PathBuf::from(&path);
    
    // Check if file exists
    if !path_buf.exists() {
        return Err("File does not exist".to_string());
    }

    // Read file as binary
    let contents = std::fs::read(&path_buf)
        .map_err(|e| format!("Failed to read file: {}", e))?;

    Ok(FileData {
        path,
        contents,
    })
}

#[command]
pub async fn save_file(window: Window, contents: Vec<u8>, default_path: Option<String>) -> Result<String, String> {
    let path = if let Some(path) = default_path {
        PathBuf::from(path)
    } else {
        window.save_file_dialog(Some(tauri::FileDialogBuilder::new()
            .set_file_name("bill.pdf")
            .add_filter("PDF files", &["pdf"])
        ))
        .await
        .ok_or_else(|| "No file selected".to_string())?
    };

    std::fs::write(&path, contents)
        .map_err(|e| format!("Failed to save file: {}", e))?;

    path.to_string_lossy().to_string()
}
