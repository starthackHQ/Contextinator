use crate::types::{FsReadError, FsReadResult, SearchMatch};
use regex::Regex;
use std::fs::File;
use std::io::{BufRead, BufReader};
use std::path::Path;
use walkdir::WalkDir;

pub fn search_pattern(
    path: &Path,
    pattern: &str,
    context_lines: u32,
) -> Result<FsReadResult, FsReadError> {
    if !path.exists() {
        return Err(FsReadError::PathNotFound(path.to_path_buf()));
    }

    let regex = Regex::new(pattern).map_err(|e| FsReadError::InvalidPattern(e.to_string()))?;

    let mut matches = Vec::new();

    if path.is_file() {
        matches.extend(search_file(path, &regex, context_lines)?);
    } else {
        matches.extend(search_directory(path, &regex, context_lines)?);
    }

    Ok(FsReadResult::Search {
        total_matches: matches.len(),
        matches,
    })
}

fn search_file(
    path: &Path,
    regex: &Regex,
    context_lines: u32,
) -> Result<Vec<SearchMatch>, FsReadError> {
    let file = File::open(path)?;
    let reader = BufReader::new(file);
    let lines: Vec<String> = reader
        .lines()
        .collect::<Result<_, _>>()
        .map_err(FsReadError::IoError)?;

    let mut matches = Vec::new();

    for (line_num, line) in lines.iter().enumerate() {
        if regex.is_match(line) {
            let context_before = get_context_before(&lines, line_num, context_lines);
            let context_after = get_context_after(&lines, line_num, context_lines);

            matches.push(SearchMatch {
                file_path: path.to_string_lossy().to_string(),
                line_number: line_num + 1,
                line_content: line.clone(),
                context_before,
                context_after,
            });
        }
    }

    Ok(matches)
}

fn search_directory(
    path: &Path,
    regex: &Regex,
    context_lines: u32,
) -> Result<Vec<SearchMatch>, FsReadError> {
    let mut all_matches = Vec::new();

    for entry in WalkDir::new(path)
        .into_iter()
        .filter_map(|e| e.ok())
        .filter(|e| e.file_type().is_file())
    {
        if let Ok(matches) = search_file(entry.path(), regex, context_lines) {
            all_matches.extend(matches);
        }
    }

    Ok(all_matches)
}

fn get_context_before(lines: &[String], index: usize, count: u32) -> Vec<String> {
    let start = index.saturating_sub(count as usize);
    lines[start..index].to_vec()
}

fn get_context_after(lines: &[String], index: usize, count: u32) -> Vec<String> {
    let end = (index + 1 + count as usize).min(lines.len());
    lines[index + 1..end].to_vec()
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use tempfile::TempDir;

    #[test]
    fn test_search_file() {
        let temp = TempDir::new().unwrap();
        let file_path = temp.path().join("test.txt");
        fs::write(&file_path, "line 1\nTODO: fix this\nline 3\nTODO: another\nline 5").unwrap();

        let result = search_pattern(&file_path, "TODO", 1).unwrap();

        if let FsReadResult::Search { matches, total_matches } = result {
            assert_eq!(total_matches, 2);
            assert_eq!(matches[0].line_number, 2);
            assert_eq!(matches[1].line_number, 4);
        } else {
            panic!("Expected Search result");
        }
    }
}
