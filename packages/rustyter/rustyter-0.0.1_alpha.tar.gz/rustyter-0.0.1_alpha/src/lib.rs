use pyo3::prelude::*;
use pyo3::types::PyIterator;
use pyo3::PyIterProtocol;

#[pyclass]
struct It {
    iter: Py<PyIterator>,
}

#[pymethods]
impl It {
    #[new]
    fn new(iter: &PyIterator) -> Self {
        It { iter: iter.into() }
    }
    #[getter]
    fn iter(&self) -> PyResult<Py<PyIterator>> {
        Ok(self.iter.clone())
    }

    fn count(slf: PyRefMut<Self>) -> PyResult<usize> {
        Ok(slf.iter.as_ref(slf.py()).count())
    }
}

#[pyproto]
impl PyIterProtocol for It {
    fn __iter__(slf: PyRef<Self>) -> PyRef<Self> {
        slf
    }

    fn __next__(slf: PyRefMut<Self>) -> Option<PyObject> {
        let mut iter: &PyIterator = slf.iter.clone().into_ref(slf.py());
        match iter.next() {
            Some(value) => return Some(value.unwrap().into()),
            None => return None,
        }
    }
}

/// A Python module implemented in Rust.
#[pymodule]
fn rustyter(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_class::<It>()?;

    Ok(())
}
