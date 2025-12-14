use lsl_recorder::LSLStreamRecorder;

fn main() {
    // Example usage
    let mut recorder =
        LSLStreamRecorder::new("example.xdf", "type=eeg", std::time::Duration::from_secs(2))
            .unwrap();
    println!("Recording to example.xdf...");
    // wait 10 seconds
    std::thread::sleep(std::time::Duration::from_secs(10));

    println!("Stopping the recorder...");

    // stop the recorder
    recorder.stop().unwrap();
}
