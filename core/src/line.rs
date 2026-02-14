use crate::types::{FsReadError, FsReadResult};
use std::fs::File;
use std::io::{BufRead, BufReader};
use std::path::Path;

pub fn read_lines(
    path: &Path,
    start_line: Option<i32>,
    end_line: Option<i32>,
) -> Result<FsReadResult, FsReadError> {
    if !path.exists() {
        return Err(FsReadError::PathNotFound(path.to_path_buf()));
    }

    if !path.is_file() {
        return Err(FsReadError::InvalidPath(format!(
            "{} is not a file",
            path.display()
        )));
    }

    let file = File::open(path)?;
    let reader = BufReader::new(file);
    let lines: Vec<String> = reader
        .lines()
        .collect::<Result<_, _>>()
        .map_err(FsReadError::IoError)?;

    let total_lines = lines.len();
    let (start_idx, end_idx) = resolve_line_range(start_line, end_line, total_lines)?;

    let selected_lines: Vec<String> = lines[start_idx..end_idx].to_vec();
    let content = selected_lines.join("\n");

    Ok(FsReadResult::Line {
        content,
        total_lines,
        lines_returned: selected_lines.len(),
    })
}

fn resolve_line_range(
    start: Option<i32>,
    end: Option<i32>,
    total_lines: usize,
) -> Result<(usize, usize), FsReadError> {
    let start_idx = match start {
        None => 0,
        Some(n) if n >= 0 => {
            // Convert 1-based line number to 0-based index
            let idx = if n == 0 { 0 } else { (n - 1) as usize };
            idx.min(total_lines)
        }
        Some(n) => {
            // Negative indexing from end
            let abs = n.unsigned_abs() as usize;
            total_lines.saturating_sub(abs)
        }
    };

    let end_idx = match end {
        None => total_lines,
        Some(n) if n >= 0 => {
            // Convert 1-based line number to 0-based index (inclusive end)
            (n as usize).min(total_lines)
        }
        Some(n) => {
            // Negative indexing from end
            let abs = n.unsigned_abs() as usize;
            if abs > total_lines {
                0
            } else {
                total_lines - abs + 1
            }
        }
    };

    if start_idx > end_idx {
        return Err(FsReadError::InvalidLineRange(
            start.unwrap_or(0),
            end.unwrap_or(0),
        ));
    }

    Ok((start_idx, end_idx))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_resolve_line_range_positive() {
        assert_eq!(resolve_line_range(Some(0), Some(10), 100).unwrap(), (0, 10));
        assert_eq!(resolve_line_range(Some(5), Some(15), 100).unwrap(), (5, 15));
    }

    #[test]
    fn test_resolve_line_range_negative() {
        assert_eq!(resolve_line_range(Some(-10), Some(-1), 100).unwrap(), (90, 100));
        assert_eq!(resolve_line_range(Some(-5), None, 100).unwrap(), (95, 100));
    }

    #[test]
    fn test_resolve_line_range_none() {
        assert_eq!(resolve_line_range(None, None, 100).unwrap(), (0, 100));
        assert_eq!(resolve_line_range(None, Some(50), 100).unwrap(), (0, 50));
    }
}
