mod types;
mod line;
mod directory;
mod search;

pub use types::{FsReadError, FsReadMode, FsReadParams, FsReadResult};

use pyo3::prelude::*;
use std::path::PathBuf;

pub fn fs_read(params: FsReadParams) -> Result<FsReadResult, FsReadError> {
    match params.mode {
        FsReadMode::Line { start_line, end_line } => {
            line::read_lines(&params.path, start_line, end_line)
        }
        FsReadMode::Directory { depth } => {
            directory::list_directory(&params.path, depth)
        }
        FsReadMode::Search { pattern, context_lines } => {
            search::search_pattern(&params.path, &pattern, context_lines)
        }
    }
}

#[pyfunction]
fn fs_read_py(
    path: String,
    mode: String,
    start_line: Option<i32>,
    end_line: Option<i32>,
    depth: Option<u32>,
    pattern: Option<String>,
    context_lines: Option<u32>,
) -> PyResult<String> {
    let path_buf = PathBuf::from(path);
    
    let fs_mode = match mode.as_str() {
        "Line" => FsReadMode::Line { start_line, end_line },
        "Directory" => FsReadMode::Directory { depth: depth.unwrap_or(0) },
        "Search" => FsReadMode::Search {
            pattern: pattern.ok_or_else(|| {
                PyErr::new::<pyo3::exceptions::PyValueError, _>("pattern required for Search mode")
            })?,
            context_lines: context_lines.unwrap_or(2),
        },
        _ => return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
            format!("Invalid mode: {}", mode)
        )),
    };

    let params = FsReadParams {
        path: path_buf,
        mode: fs_mode,
    };

    let result = fs_read(params).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string())
    })?;

    serde_json::to_string(&result).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string())
    })
}

#[pyfunction]
fn fs_read_batch_py(operations: Vec<String>) -> PyResult<Vec<String>> {
    let mut results = Vec::new();

    for op_json in operations {
        let params: FsReadParams = serde_json::from_str(&op_json).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string())
        })?;

        let result = fs_read(params).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string())
        })?;

        let result_json = serde_json::to_string(&result).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string())
        })?;

        results.push(result_json);
    }

    Ok(results)
}

#[pymodule]
fn contextinator_core(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(fs_read_py, m)?)?;
    m.add_function(wrap_pyfunction!(fs_read_batch_py, m)?)?;
    Ok(())
}
