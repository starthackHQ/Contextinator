use serde::{Deserialize, Serialize};
use std::path::PathBuf;

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "mode", rename_all = "PascalCase")]
pub enum FsReadMode {
    Line {
        #[serde(skip_serializing_if = "Option::is_none")]
        start_line: Option<i32>,
        #[serde(skip_serializing_if = "Option::is_none")]
        end_line: Option<i32>,
    },
    Directory {
        #[serde(default)]
        depth: u32,
    },
    Search {
        pattern: String,
        #[serde(default = "default_context_lines")]
        context_lines: u32,
    },
}

fn default_context_lines() -> u32 {
    2
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FsReadParams {
    pub path: PathBuf,
    #[serde(flatten)]
    pub mode: FsReadMode,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "type", rename_all = "lowercase")]
pub enum FsReadResult {
    Line {
        content: String,
        total_lines: usize,
        lines_returned: usize,
    },
    Directory {
        entries: Vec<FileEntry>,
        total_count: usize,
    },
    Search {
        matches: Vec<SearchMatch>,
        total_matches: usize,
    },
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FileEntry {
    pub path: String,
    pub is_dir: bool,
    pub size: u64,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub modified: Option<u64>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SearchMatch {
    pub file_path: String,
    pub line_number: usize,
    pub line_content: String,
    pub context_before: Vec<String>,
    pub context_after: Vec<String>,
}

#[derive(Debug)]
pub enum FsReadError {
    PathNotFound(PathBuf),
    PermissionDenied(PathBuf),
    InvalidPath(String),
    IoError(std::io::Error),
    InvalidLineRange(i32, i32),
    InvalidPattern(String),
}

impl std::fmt::Display for FsReadError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::PathNotFound(p) => write!(f, "Path not found: {}", p.display()),
            Self::PermissionDenied(p) => write!(f, "Permission denied: {}", p.display()),
            Self::InvalidPath(s) => write!(f, "Invalid path: {}", s),
            Self::IoError(e) => write!(f, "IO error: {}", e),
            Self::InvalidLineRange(s, e) => write!(f, "Invalid line range: {} to {}", s, e),
            Self::InvalidPattern(s) => write!(f, "Invalid pattern: {}", s),
        }
    }
}

impl std::error::Error for FsReadError {}

impl From<std::io::Error> for FsReadError {
    fn from(err: std::io::Error) -> Self {
        Self::IoError(err)
    }
}
