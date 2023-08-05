use pyo3::prelude::*;
use sqlu::sqlu::parser::parse_sql_as_json_value;
use serde_json;
use pyo3::exceptions;

#[pyfunction]
fn parse(dialact: &str, sql: &str) -> PyResult<String> {
    let json = parse_sql_as_json_value(dialact, sql)
        .map(|value| serde_json::to_string(&value).unwrap());
    match json {
        Ok(json_string) => Ok(json_string),
        Err(e) => Err(exceptions::PyException::new_err(e.to_string()))
    }
}

#[pymodule]
fn sqlupy(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(parse, m)?)?;
    Ok(())
}
