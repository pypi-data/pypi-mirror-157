use pyo3::prelude::*;
use kami_parser::syntax;

/// Formats the sum of two numbers as string.
#[pyfunction]
fn parse(a: String) -> PyResult<String> {
    Ok(syntax::parse(&a))
}

/// A Python module implemented in Rust.
#[pymodule]
fn pykami(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(parse, m)?)?;
    Ok(())
}
