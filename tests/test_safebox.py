#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Automated test suite for SafeBox."""

import configparser
import ctypes
import errno
import glob
import os
import py_compile
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHARE_DIR = os.path.join(REPO_ROOT, "usr", "share", "safebox")
if SHARE_DIR not in sys.path:
    sys.path.insert(0, SHARE_DIR)

import seccomp_filter  # noqa: E402


class TestSafeBoxStaticAndPackaging(unittest.TestCase):
    def test_bash_syntax(self):
        scripts = [
            "usr/bin/safebox",
            "usr/bin/safebox-core",
            "usr/bin/safebox-setup",
            "usr/share/safebox/guest-init",
            "usr/share/safebox/safebox-guest-blocker",
        ]
        for rel in scripts:
            path = os.path.join(REPO_ROOT, rel)
            res = subprocess.run(["bash", "-n", path], capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, f"bash -n failed for {rel}: {res.stderr}")

    def test_python_compile(self):
        py_files = [
            "usr/share/safebox/safebox_gui.py",
            "usr/share/safebox/seccomp_filter.py",
            "usr/share/safebox/welcome.py",
        ]
        for rel in py_files:
            path = os.path.join(REPO_ROOT, rel)
            py_compile.compile(path, doraise=True)

    def test_executable_permissions(self):
        exec_files = [
            "usr/bin/safebox",
            "usr/bin/safebox-core",
            "usr/bin/safebox-setup",
            "usr/share/safebox/guest-init",
            "usr/share/safebox/safebox-guest-blocker",
            "usr/share/safebox/safebox_gui.py",
            "usr/share/safebox/seccomp_filter.py",
            "usr/share/safebox/welcome.py",
            "debian/rules",
        ]
        for rel in exec_files:
            path = os.path.join(REPO_ROOT, rel)
            self.assertTrue(os.access(path, os.X_OK), f"{rel} should be executable")

    def test_debian_install_no_nested_dirs(self):
        with open(os.path.join(REPO_ROOT, "debian", "install"), encoding="utf-8") as fh:
            lines = [line.strip() for line in fh if line.strip() and not line.strip().startswith("#")]
        self.assertIn("usr/share/safebox/seccomp_filter.py /usr/share/safebox/", lines)
        for line in lines:
            src, dst = line.split()
            if os.path.isdir(os.path.join(REPO_ROOT, src.rstrip("/"))):
                base = os.path.basename(src.rstrip("/"))
                self.assertNotEqual(
                    dst.rstrip("/").split("/")[-1],
                    base,
                    f"dh_install directory nesting bug in line: {line}",
                )

    def test_debian_control_dependencies(self):
        with open(os.path.join(REPO_ROOT, "debian", "control"), encoding="utf-8") as fh:
            content = fh.read()
        self.assertIn("pkexec | policykit-1", content)
        self.assertIn("x11-utils", content)
        self.assertIn("libseccomp2", content)

    def test_desktop_svg_and_metainfo(self):
        desktop_files = glob.glob(os.path.join(REPO_ROOT, "usr", "share", "**", "*.desktop"), recursive=True)
        self.assertGreaterEqual(len(desktop_files), 7)
        for path in desktop_files:
            cp = configparser.ConfigParser(interpolation=None)
            cp.read(path, encoding="utf-8")
            self.assertIn("Desktop Entry", cp, f"Missing Desktop Entry in {path}")
            self.assertTrue(cp["Desktop Entry"].get("Exec"), f"Missing Exec in {path}")

        ET.parse(os.path.join(REPO_ROOT, "usr", "share", "icons", "hicolor", "scalable", "apps", "safebox.svg"))
        ET.parse(os.path.join(REPO_ROOT, "usr", "share", "metainfo", "com.winexe.safebox.metainfo.xml"))

        if shutil.which("appstreamcli"):
            res = subprocess.run(
                [
                    "appstreamcli",
                    "validate",
                    os.path.join(REPO_ROOT, "usr", "share", "metainfo", "com.winexe.safebox.metainfo.xml"),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(res.returncode, 0, f"appstreamcli validate failed:\n{res.stdout}\n{res.stderr}")

    def test_version_sync(self):
        with open(os.path.join(REPO_ROOT, "debian", "changelog"), encoding="utf-8") as fh:
            first_line = fh.readline().strip()
        match = re.match(r"safebox \((\d+\.\d+\.\d+)-", first_line)
        self.assertIsNotNone(match)
        expected_ver = match.group(1)

        with open(os.path.join(REPO_ROOT, "snap", "snapcraft.yaml"), encoding="utf-8") as fh:
            snap_text = fh.read()
        self.assertIn(f"version: '{expected_ver}'", snap_text)
        self.assertIn("confinement: classic", snap_text)
        self.assertNotIn("extensions:", snap_text)
        self.assertNotIn("plugs:", snap_text)

        with open(os.path.join(REPO_ROOT, "README.md"), encoding="utf-8") as fh:
            self.assertIn(f"Release-v{expected_ver}", fh.read())

    def test_runtime_safety_invariants(self):
        with open(os.path.join(REPO_ROOT, "usr", "bin", "safebox-core"), encoding="utf-8") as fh:
            core_text = fh.read()
        self.assertIn("--unshare-cgroup-try", core_text)
        self.assertIn("-nolisten tcp", core_text)

        with open(os.path.join(REPO_ROOT, "usr", "share", "safebox", "safebox_gui.py"), encoding="utf-8") as fh:
            gui_text = fh.read()
        self.assertNotIn("subprocess.run(cmd, timeout=", gui_text)
        self.assertIn('resolve_bin("safebox-setup"), "--yes"', gui_text)


class TestSafeBoxCLIAndSeccomp(unittest.TestCase):
    def test_safebox_core_input_validation(self):
        core = os.path.join(REPO_ROOT, "usr", "bin", "safebox-core")
        with tempfile.TemporaryDirectory() as td:
            env = os.environ.copy()
            env["HOME"] = os.path.join(td, "home")
            env["XDG_RUNTIME_DIR"] = os.path.join(td, "xdg")
            os.makedirs(env["HOME"], exist_ok=True)
            os.makedirs(env["XDG_RUNTIME_DIR"], exist_ok=True)

            bad_cases = [
                ["abc", "2", "1366x768", "1", "1", "1", "1"],
                ["4", "0", "1366x768", "1", "1", "1", "1"],
                ["4", "2", "invalid_res", "1", "1", "1", "1"],
                ["4", "2", "1366x768", "2", "1", "1", "1"],
                ["4", "2", "1366x768", "1", "1", "1", "9"],
            ]
            for args in bad_cases:
                res = subprocess.run([core, *args], env=env, capture_output=True, text=True)
                self.assertEqual(res.returncode, 108, f"Expected 108 for {args}, got {res.returncode}")

            if not os.path.exists("/var/lib/safebox/rootfs/.safebox-rootfs-complete"):
                res = subprocess.run([core, "4", "2", "1366x768", "1", "1", "1", "1"], env=env, capture_output=True, text=True)
                self.assertEqual(res.returncode, 105)

            runtime_dir = os.path.join(env["XDG_RUNTIME_DIR"], "safebox")
            self.assertTrue(os.path.isdir(runtime_dir))

    def test_safebox_setup_flags_and_nonroot(self):
        setup = os.path.join(REPO_ROOT, "usr", "bin", "safebox-setup")
        help_res = subprocess.run([setup, "--help"], capture_output=True, text=True)
        self.assertEqual(help_res.returncode, 0)
        if os.geteuid() != 0:
            nonroot_res = subprocess.run([setup], capture_output=True, text=True)
            self.assertEqual(nonroot_res.returncode, 1)

    def test_guest_blocker(self):
        blocker = os.path.join(REPO_ROOT, "usr", "share", "safebox", "safebox-guest-blocker")
        res = subprocess.run([blocker], capture_output=True, text=True)
        self.assertEqual(res.returncode, 1)
        self.assertIn("İç içe sandbox", res.stdout)

    def test_seccomp_bpf_generation_modes(self):
        with tempfile.TemporaryDirectory() as td:
            fb_path = os.path.join(td, "fallback.bpf")
            mode = seccomp_filter.write_bpf_to_path(fb_path, force_fallback=True)
            self.assertEqual(mode, "fallback")
            with open(fb_path, "rb") as fh:
                fb_data = fh.read()
            self.assertGreater(len(fb_data), 0)
            self.assertEqual(len(fb_data) % 8, 0)

            try:
                ctypes.CDLL("libseccomp.so.2")
                has_libseccomp = True
            except OSError:
                has_libseccomp = False

            if has_libseccomp:
                lib_path = os.path.join(td, "libseccomp.bpf")
                mode2 = seccomp_filter.write_bpf_to_path(lib_path, force_fallback=False)
                self.assertEqual(mode2, "libseccomp")
                with open(lib_path, "rb") as fh:
                    lib_data = fh.read()
                self.assertGreater(len(lib_data), 0)
                self.assertEqual(len(lib_data) % 8, 0)

    def test_bwrap_seccomp_enforced_in_sandbox(self):
        if not shutil.which("bwrap"):
            self.skipTest("bwrap not installed")

        probe = subprocess.run(
            ["bwrap", "--unshare-user", "--ro-bind", "/", "/", "--dev", "/dev", "--proc", "/proc", "/bin/true"],
            capture_output=True,
            text=True,
        )
        if probe.returncode != 0:
            self.skipTest(f"bwrap user namespaces unavailable in this environment: {probe.stderr}")

        guest_code = """
import ctypes, errno
libc = ctypes.CDLL(None, use_errno=True)
status = {}
with open('/proc/self/status') as fh:
    for line in fh:
        if ':' in line:
            k, v = line.split(':', 1)
            status[k.strip()] = v.strip()
assert status.get('NoNewPrivs') == '1', status
assert status.get('Seccomp') == '2', status

table = {'x86_64': {'unshare': 272, 'bpf': 321, 'userfaultfd': 323, 'kexec_load': 246, 'keyctl': 250, 'io_uring_setup': 425, 'ptrace': 101},
         'aarch64': {'unshare': 97, 'bpf': 280, 'userfaultfd': 282, 'kexec_load': 104, 'keyctl': 219, 'io_uring_setup': 425, 'ptrace': 117}}
import platform
arch = platform.machine().lower()
for name, nr in table[arch].items():
    ctypes.set_errno(0)
    r = libc.syscall(nr, 0, 0, 0, 0, 0, 0)
    err = ctypes.get_errno()
    assert r == -1 and err == errno.EPERM, (name, r, err)
print('SECCOMP_VERIFIED')
"""
        for force_fb in (False, True):
            with tempfile.TemporaryDirectory() as td:
                bpf_path = os.path.join(td, "filter.bpf")
                seccomp_filter.write_bpf_to_path(bpf_path, force_fallback=force_fb)
                with open(bpf_path, "rb") as bpf_fh:
                    res = subprocess.run(
                        [
                            "bwrap",
                            "--unshare-user",
                            "--unshare-pid",
                            "--unshare-uts",
                            "--unshare-ipc",
                            "--unshare-net",
                            "--ro-bind",
                            "/",
                            "/",
                            "--dev",
                            "/dev",
                            "--proc",
                            "/proc",
                            "--seccomp",
                            str(bpf_fh.fileno()),
                            sys.executable,
                            "-c",
                            guest_code,
                        ],
                        pass_fds=(bpf_fh.fileno(),),
                        capture_output=True,
                        text=True,
                        timeout=15,
                    )
                self.assertEqual(res.returncode, 0, f"force_fb={force_fb} failed:\n{res.stdout}\n{res.stderr}")
                self.assertIn("SECCOMP_VERIFIED", res.stdout)

    def test_gui_module_helpers(self):
        try:
            import gi
            gi.require_version("Gtk", "3.0")
            from gi.repository import Gtk  # noqa: F401
        except Exception as exc:
            self.skipTest(f"GTK3 PyGObject unavailable: {exc}")

        import safebox_gui

        with tempfile.TemporaryDirectory() as td:
            old_xdg = os.environ.get("XDG_RUNTIME_DIR")
            os.environ["XDG_RUNTIME_DIR"] = td
            try:
                self.assertEqual(safebox_gui.get_runtime_dir(), os.path.join(td, "safebox"))
            finally:
                if old_xdg is None:
                    os.environ.pop("XDG_RUNTIME_DIR", None)
                else:
                    os.environ["XDG_RUNTIME_DIR"] = old_xdg

        self.assertTrue(safebox_gui.resolve_bin("safebox-core").endswith("/usr/bin/safebox-core"))
        self.assertTrue(safebox_gui.resolve_bin("safebox-setup").endswith("/usr/bin/safebox-setup"))


if __name__ == "__main__":
    unittest.main()
