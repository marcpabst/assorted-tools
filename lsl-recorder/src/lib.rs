use std::{
    io::{BufRead, Write},
    process::Child,
    sync::{Arc, Mutex},
};

use pyo3::{
    Bound, Py, PyAny, PyRef, PyRefMut, PyResult, Python,
    exceptions::PyRuntimeError,
    ffi::c_str,
    pyclass, pymethods, pymodule,
    types::{PyAnyMethods, PyModule, PyModuleMethods, PyType},
};

#[pyclass]
#[derive(Clone)]
pub struct LSLStreamRecorder {
    process: Arc<Mutex<Child>>,
}

impl LSLStreamRecorder {
    pub fn new(
        filename: &str,
        seearchstring: &str,
        timeout: std::time::Duration,
        cli_path: Option<&str>,
    ) -> Result<Self, std::io::Error> {
        // the recorder cli is in app/LabRecorderCLI

        let cli_path = cli_path.unwrap_or("app/LabRecorderCLI");
        let cli_path = std::path::Path::new(cli_path);

        let mut command = std::process::Command::new(cli_path);

        // wrap searchstring in single quotes
        let seearchstring = format!("'{}'", seearchstring);

        // run the command
        // hide stdout and stderr
        let mut child = command
            .arg(filename)
            .arg(seearchstring)
            .stdout(std::process::Stdio::piped())
            .stderr(std::process::Stdio::piped())
            .stdin(std::process::Stdio::piped())
            .spawn()
            .expect("Failed to start LabRecorderCLI");

        // read stdout until we find "Started data collection for stream"
        let start_time = std::time::Instant::now();
        while child.try_wait().is_ok() {
            // read stdout
            let mut buffer = String::new();
            if let Some(ref mut stdout) = child.stdout {
                let mut reader = std::io::BufReader::new(stdout);
                if reader.read_line(&mut buffer).is_ok() {
                    if buffer.contains("Started data collection for stream") {
                        break;
                    } else if buffer.contains("matched no stream!") {
                    }
                }
            }

            // check for timeout
            if start_time.elapsed() > timeout {
                return Err(std::io::Error::new(
                    std::io::ErrorKind::TimedOut,
                    "Timeout waiting for LSL stream to start",
                ));
            }
        }

        // return LSLStreamRecorder
        Ok(LSLStreamRecorder {
            process: Arc::new(Mutex::new(child)),
        })
    }

    pub fn stop(&mut self) -> Result<(), std::io::Error> {
        // send enter key to the process
        // this will stop the recording
        self.process
            .lock()
            .unwrap()
            .stdin
            .as_mut()
            .unwrap()
            .write_all(b"\n")?;
        // wait for process to finish
        self.process.lock().unwrap().wait()?;
        Ok(())
    }
}

#[pymethods]
impl LSLStreamRecorder {
    /// Create a new LSLStreamRecorder.
    #[new]
    fn py_new(filename: String, seearchstring: String, timeout: f64, py: Python) -> PyResult<Self> {
        let timeout = std::time::Duration::from_secs_f64(timeout);
        // read path of the package
        let module = PyModule::import(py, "lsl_recorder")?;
        let path = module.getattr("__file__")?.extract::<String>()?;
        // get the path of the package
        let path = std::path::Path::new(&path);
        // get the path of the cli
        let cli_path = path.parent().unwrap();
        // get the path of the cli
        let cli_path = cli_path.join("app");
        let cli_path = cli_path.join("LabRecorderCLI");
        // convert to string
        let cli_path = cli_path.to_str().unwrap();

        let recorder = LSLStreamRecorder::new(&filename, &seearchstring, timeout, Some(cli_path))
            .map_err(|e| {
            PyRuntimeError::new_err(format!("Failed to create recorder: {}", e))
        })?;
        Ok(recorder)
    }

    /// Stop the recording.
    #[pyo3(name = "stop")]
    fn py_stop(&mut self) -> PyResult<()> {
        self.stop()
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to stop recorder: {}", e)))?;
        Ok(())
    }

    fn __enter__(slf: PyRef<Self>) -> PyResult<Py<Self>> {
        // return self
        Ok(slf.into())
    }

    fn __exit__(
        mut slf: PyRefMut<Self>,
        exc_type: Bound<'_, PyAny>,
        exc_value: Bound<'_, PyAny>,
        traceback: Bound<'_, PyAny>,
    ) -> PyResult<()> {
        // stop the recorder
        slf.py_stop()?;
        Ok(())
    }
}

#[pymodule]
fn lsl_recorder(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<LSLStreamRecorder>()?;
    Ok(())
}
