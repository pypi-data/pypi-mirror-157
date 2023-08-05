use pyo3::prelude::*;
use sqlu::sqlu::parser::parse_sql_as_json_value;
use pyo3::exceptions;
use pyo3::Python;
use pythonize::pythonize;


#[pyfunction]
fn parse(dialact: &str, sql: &str) -> PyResult<Py<PyAny>> {
    parse_sql_as_json_value(dialact, sql)
        .map(|value| {
            let gil = Python::acquire_gil();
            let py = gil.python();
            let obj = pythonize(py, &value).unwrap();
            obj
        })
        .or_else(|e| Err(exceptions::PyException::new_err(e.to_string())))
}

#[pymodule]
fn sqlupy(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(parse, m)?)?;
    Ok(())
}
