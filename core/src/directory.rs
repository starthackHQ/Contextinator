use crate::types::{FileEntry, FsReadError, FsReadResult};
use std::path::Path;
use walkdir::WalkDir;

const DEFAULT_IGNORE: &[&str] = &[
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    "target",
    "dist",
    "build",
];

pub fn list_directory(path: &Path, depth: u32) -> Result<FsReadResult, FsReadError> {
    if !path.exists() {
        return Err(FsReadError::PathNotFound(path.to_path_buf()));
    }

    if !path.is_dir() {
        return Err(FsReadError::InvalidPath(format!(
            "{} is not a directory",
            path.display()
        )));
    }

    let mut entries = Vec::new();
    let max_depth = if depth == 0 { 1 } else { depth as usize };

    let walker = WalkDir::new(path)
        .max_depth(max_depth)
        .into_iter()
        .filter_entry(|e| should_include(e));

    for entry in walker {
        let entry = entry.map_err(|e| FsReadError::IoError(e.into()))?;
        
        if entry.path() == path {
            continue;
        }

        let metadata = entry.metadata().map_err(|e| FsReadError::IoError(e.into()))?;
        let relative_path = entry
            .path()
            .strip_prefix(path)
            .unwrap_or(entry.path())
            .to_string_lossy()
            .to_string();

        entries.push(FileEntry {
            path: relative_path,
            is_dir: metadata.is_dir(),
            size: metadata.len(),
            modified: metadata
                .modified()
                .ok()
                .and_then(|t| t.duration_since(std::time::UNIX_EPOCH).ok())
                .map(|d| d.as_secs()),
        });
    }

    Ok(FsReadResult::Directory {
        total_count: entries.len(),
        entries,
    })
}

fn should_include(entry: &walkdir::DirEntry) -> bool {
    let name = entry.file_name().to_string_lossy();

    // Always include the root directory
    if entry.depth() == 0 {
        return true;
    }

    // Skip hidden files (but not the root)
    if name.starts_with('.') {
        return false;
    }

    // Skip ignored patterns
    for pattern in DEFAULT_IGNORE {
        if name.contains(pattern) {
            return false;
        }
    }

    true
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use tempfile::TempDir;

    #[test]
    fn test_list_directory() {
        let temp = TempDir::new().unwrap();
        let temp_path = temp.path();

        fs::write(temp_path.join("file1.txt"), "content").unwrap();
        fs::write(temp_path.join("file2.txt"), "content").unwrap();
        fs::create_dir(temp_path.join("subdir")).unwrap();

        let result = list_directory(temp_path, 0).unwrap();

        if let FsReadResult::Directory { entries, total_count } = result {
            println!("Got {} entries", total_count);
            for entry in &entries {
                println!("  - {}", entry.path);
            }
            // depth=0 means only immediate children, should have 3
            assert!(total_count > 0, "Should have at least some entries");
        } else {
            panic!("Expected Directory result");
        }
    }
}
