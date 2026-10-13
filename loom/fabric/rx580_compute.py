"""
AMD Radeon RX 580 (Ellesmere) Hardware Compute Engine (`loom/fabric/rx580_compute.py`).

Direct native hardware compute using OpenCL on Platform 1 (Advanced Micro Devices, Inc. - Ellesmere 2048SP).
Executes high-density dynamical Kuramoto phase synchronization and topological invariant sweeps
directly across the 2,048 stream processors of the RX 580.
"""

from __future__ import annotations

import ctypes
import logging
from typing import Dict, Optional, Tuple
import numpy as np

logger = logging.getLogger("rx580_compute")

# OpenCL API Constants
CL_DEVICE_TYPE_ALL = 0xFFFFFFFF
CL_PLATFORM_NAME = 0x0903
CL_DEVICE_NAME = 0x102B
CL_MEM_READ_WRITE = (1 << 0)
CL_MEM_COPY_HOST_PTR = (1 << 5)


class RX580HardwareEngine:
    """Native OpenCL hardware compute pipeline bound specifically to the AMD Radeon RX 580 (Ellesmere)."""

    def __init__(self, n_oscillators: int = 65536):
        self.n_oscillators = n_oscillators
        self._initialized = False
        self._ctx = None
        self._queue = None
        self._kernel = None
        self._buf_theta = None
        self._buf_omega = None
        self.device_name = "Unknown"

        try:
            self._init_opencl()
            self._initialized = True
            logger.info(f"⚡ RX580HardwareEngine online: Bound to AMD Hardware ({self.device_name}), N={n_oscillators:,}")
        except Exception as e:
            logger.warning(f"Failed to initialize RX 580 OpenCL hardware pipeline: {e}. Falling back to vectorized CPU path.")

    def _init_opencl(self) -> None:
        self.cl = ctypes.cdll.LoadLibrary("OpenCL.dll")

        # Function signatures
        self.cl.clGetPlatformIDs.argtypes = [ctypes.c_uint32, ctypes.c_void_p, ctypes.c_void_p]
        self.cl.clGetPlatformInfo.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_void_p]
        self.cl.clGetDeviceIDs.argtypes = [ctypes.c_void_p, ctypes.c_uint64, ctypes.c_uint32, ctypes.c_void_p, ctypes.c_void_p]
        self.cl.clGetDeviceInfo.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_void_p]
        self.cl.clCreateContext.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
        self.cl.clCreateContext.restype = ctypes.c_void_p
        self.cl.clCreateCommandQueue.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint64, ctypes.c_void_p]
        self.cl.clCreateCommandQueue.restype = ctypes.c_void_p
        self.cl.clCreateProgramWithSource.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
        self.cl.clCreateProgramWithSource.restype = ctypes.c_void_p
        self.cl.clBuildProgram.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_void_p, ctypes.c_char_p, ctypes.c_void_p, ctypes.c_void_p]
        self.cl.clCreateKernel.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_void_p]
        self.cl.clCreateKernel.restype = ctypes.c_void_p
        self.cl.clCreateBuffer.argtypes = [ctypes.c_void_p, ctypes.c_uint64, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_void_p]
        self.cl.clCreateBuffer.restype = ctypes.c_void_p
        self.cl.clSetKernelArg.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_size_t, ctypes.c_void_p]
        self.cl.clEnqueueNDRangeKernel.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32, ctypes.c_void_p, ctypes.c_void_p]
        self.cl.clEnqueueReadBuffer.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32, ctypes.c_size_t, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_uint32, ctypes.c_void_p, ctypes.c_void_p]
        self.cl.clFinish.argtypes = [ctypes.c_void_p]

        # Enumerate platforms to locate AMD
        num_p = ctypes.c_uint32()
        self.cl.clGetPlatformIDs(0, None, ctypes.byref(num_p))
        platforms = (ctypes.c_void_p * num_p.value)()
        self.cl.clGetPlatformIDs(num_p.value, platforms, None)

        amd_p = None
        for p in platforms:
            pname = ctypes.create_string_buffer(256)
            self.cl.clGetPlatformInfo(p, CL_PLATFORM_NAME, 256, pname, None)
            if b"Advanced Micro Devices" in pname.value:
                amd_p = p
                break

        if amd_p is None:
            raise RuntimeError("AMD OpenCL platform not found")

        # Get device
        dev = ctypes.c_void_p()
        self.cl.clGetDeviceIDs(amd_p, CL_DEVICE_TYPE_ALL, 1, ctypes.byref(dev), None)
        dname = ctypes.create_string_buffer(256)
        self.cl.clGetDeviceInfo(dev, CL_DEVICE_NAME, 256, dname, None)
        self.device_name = dname.value.decode("utf-8", errors="ignore")

        # Context and Queue
        err = ctypes.c_int32()
        self._ctx = self.cl.clCreateContext(None, 1, ctypes.byref(dev), None, None, ctypes.byref(err))
        if err.value != 0:
            raise RuntimeError(f"clCreateContext failed with code {err.value}")

        self._queue = self.cl.clCreateCommandQueue(self._ctx, dev, 0, ctypes.byref(err))
        if err.value != 0:
            raise RuntimeError(f"clCreateCommandQueue failed with code {err.value}")

        # Compile Kernel
        kernel_src = b"""
        __kernel void kuramoto_sweep(__global float* theta, __global const float* omega, const float k_order, const float psi, const float dt, const int n) {
            int gid = get_global_id(0);
            if (gid < n) {
                float d = omega[gid] + k_order * sin(psi - theta[gid]);
                theta[gid] += d * dt;
            }
        }
        """
        src_p = ctypes.c_char_p(kernel_src)
        src_len = ctypes.c_size_t(len(kernel_src))
        prog = self.cl.clCreateProgramWithSource(self._ctx, 1, ctypes.byref(src_p), ctypes.byref(src_len), ctypes.byref(err))
        self.cl.clBuildProgram(prog, 1, ctypes.byref(dev), None, None, None)
        self._kernel = self.cl.clCreateKernel(prog, b"kuramoto_sweep", ctypes.byref(err))

        # Initialize Device Memory Buffers
        n = self.n_oscillators
        theta_init = np.random.uniform(0.0, 2.0 * np.pi, size=n).astype(np.float32)
        omega_init = np.random.normal(0.0, 1.0, size=n).astype(np.float32)
        n_bytes = n * 4

        self._buf_theta = self.cl.clCreateBuffer(
            self._ctx,
            CL_MEM_READ_WRITE | CL_MEM_COPY_HOST_PTR,
            n_bytes,
            theta_init.ctypes.data_as(ctypes.c_void_p),
            ctypes.byref(err),
        )
        self._buf_omega = self.cl.clCreateBuffer(
            self._ctx,
            CL_MEM_READ_WRITE | CL_MEM_COPY_HOST_PTR,
            n_bytes,
            omega_init.ctypes.data_as(ctypes.c_void_p),
            ctypes.byref(err),
        )

        self.theta_cache = theta_init

    def step_sweep(self, steps: int = 500, k_coupling: float = 2.8, dt: float = 0.015) -> Dict[str, object]:
        """Dispatches an iterative batch of dynamical updates directly to the RX 580 stream processors."""
        if not self._initialized:
            # Fallback to CPU NumPy if OpenCL unavailable
            return self._cpu_fallback_step(steps, k_coupling, dt)

        n = self.n_oscillators
        n_c = ctypes.c_int32(n)
        dt_c = ctypes.c_float(dt)
        k_c = ctypes.c_float(k_coupling)

        global_work_size = (ctypes.c_size_t * 1)(n)

        # Execute iterative steps on the GPU
        for _ in range(steps):
            # Compute order parameter on host sample for coupling angle
            comp = np.mean(np.exp(1j * self.theta_cache[:4096]))
            r_order = float(np.abs(comp))
            psi_angle = float(np.angle(comp))

            r_c = ctypes.c_float(r_order * k_coupling)
            psi_c = ctypes.c_float(psi_angle)

            # Set kernel arguments
            buf_t = ctypes.c_void_p(self._buf_theta)
            buf_o = ctypes.c_void_p(self._buf_omega)
            self.cl.clSetKernelArg(self._kernel, 0, ctypes.sizeof(ctypes.c_void_p), ctypes.byref(buf_t))
            self.cl.clSetKernelArg(self._kernel, 1, ctypes.sizeof(ctypes.c_void_p), ctypes.byref(buf_o))
            self.cl.clSetKernelArg(self._kernel, 2, ctypes.sizeof(ctypes.c_float), ctypes.byref(r_c))
            self.cl.clSetKernelArg(self._kernel, 3, ctypes.sizeof(ctypes.c_float), ctypes.byref(psi_c))
            self.cl.clSetKernelArg(self._kernel, 4, ctypes.sizeof(ctypes.c_float), ctypes.byref(dt_c))
            self.cl.clSetKernelArg(self._kernel, 5, ctypes.sizeof(ctypes.c_int32), ctypes.byref(n_c))

            # Dispatch ND-Range Kernel to the RX 580 Stream Processors
            self.cl.clEnqueueNDRangeKernel(self._queue, self._kernel, 1, None, global_work_size, None, 0, None, None)

        # Read back a portion of the state to update cache and compute final order
        read_n = min(n, 8192)
        read_bytes = read_n * 4
        self.cl.clEnqueueReadBuffer(
            self._queue,
            self._buf_theta,
            1,  # blocking read
            0,
            read_bytes,
            self.theta_cache.ctypes.data_as(ctypes.c_void_p),
            0,
            None,
            None,
        )
        self.cl.clFinish(self._queue)

        final_order = float(np.abs(np.mean(np.exp(1j * self.theta_cache[:read_n]))))

        return {
            "device": f"AMD RX 580 ({self.device_name})",
            "backend": "OpenCL Hardware Accelerated",
            "oscillators": n,
            "steps": steps,
            "coherence_r": round(final_order, 4),
            "conserved": final_order > 0.45,
        }

    def _cpu_fallback_step(self, steps: int, k_coupling: float, dt: float) -> Dict[str, object]:
        n = 4096
        theta = np.random.uniform(0.0, 2.0 * np.pi, size=n).astype(np.float32)
        omega = np.random.normal(0.0, 1.0, size=n).astype(np.float32)
        for _ in range(steps):
            comp = np.mean(np.exp(1j * theta))
            d = omega + (k_coupling * np.abs(comp) * np.sin(np.angle(comp) - theta))
            theta += d * dt
        r = float(np.abs(np.mean(np.exp(1j * theta))))
        return {
            "device": "Host CPU Fallback",
            "backend": "NumPy Vectorized",
            "oscillators": n,
            "steps": steps,
            "coherence_r": round(r, 4),
            "conserved": r > 0.45,
        }
