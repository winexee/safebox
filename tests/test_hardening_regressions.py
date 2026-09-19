import pathlib
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
CORE = (REPO_ROOT / "usr/bin/safebox-core").read_text(encoding="utf-8")
SETUP = (REPO_ROOT / "usr/bin/safebox-setup").read_text(encoding="utf-8")
GUI = (REPO_ROOT / "usr/share/safebox/safebox_gui.py").read_text(encoding="utf-8")


class HardeningRegressionTests(unittest.TestCase):
    def test_core_defaults_are_opt_in_for_audio_and_gpu(self):
        self.assertIn('AUDIO="${5:-0}"', CORE)
        self.assertIn('GPU="${7:-0}"', CORE)

    def test_core_records_payload_pid_for_doctor(self):
        self.assertIn('SANDBOX_PID_FILE="/tmp/safebox-sandbox.pid"', CORE)
        self.assertIn('echo "$$" > "$1"; shift; exec "$@"', CORE)
        self.assertIn('echo "$SANDBOX_PID" > "$SANDBOX_PID_FILE"', CORE)

    def test_setup_uses_atomic_backup_swap_and_rollback(self):
        self.assertIn('ROOTFS_BACKUP="${ROOTFS_DIR}.backup"', SETUP)
        self.assertIn('mv "$ROOTFS_DIR" "$ROOTFS_BACKUP"', SETUP)
        self.assertIn('if mv "$ROOTFS_TMP" "$ROOTFS_DIR"; then', SETUP)
        self.assertIn('mv "$ROOTFS_BACKUP" "$ROOTFS_DIR"', SETUP)

    def test_setup_marker_has_versioned_metadata(self):
        self.assertIn("format_version=${ROOTFS_MARKER_VERSION}", SETUP)
        self.assertIn("distro=${DISTRO}", SETUP)
        self.assertIn("created_at=", SETUP)

    def test_gui_doctor_uses_payload_pid_and_mode(self):
        self.assertIn('sandbox_pid_file = "/tmp/safebox-sandbox.pid"', GUI)
        self.assertIn('session_mode_file = "/tmp/safebox-session.mode"', GUI)
        self.assertIn('if run_mode == "scope":', GUI)
        self.assertIn('cgroup_path = subprocess.run(["cat", f"/proc/{sandbox_pid}/cgroup"]', GUI)

    def test_gui_gpu_checkbox_and_engine_arg(self):
        self.assertIn("self.chk_gpu = Gtk.CheckButton", GUI)
        self.assertIn("self.chk_gpu.set_active(False)", GUI)
        self.assertIn('cmd = [engine_path, ram, cpu, res, share, audio, net, gpu]', GUI)


if __name__ == "__main__":
    unittest.main()
