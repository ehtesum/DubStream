"""
Voice cloning environment detector and setup script for DubStream v2.0.

Detects Python version, PyTorch CUDA capability, F5-TTS / XTTS v2 package availability,
and reports MODEL_AVAILABLE or MODEL_UNAVAILABLE without auto-downloading large weights during boot.
"""
import sys
import platform
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def inspect_voice_cloning_environment() -> dict:
    py_ver = platform.python_version()
    os_info = f"{platform.system()} {platform.release()}"

    torch_installed = False
    cuda_available = False
    gpu_name = "None"
    vram_gb = 0.0

    try:
        import torch
        torch_installed = True
        cuda_available = torch.cuda.is_available()
        if cuda_available:
            gpu_name = torch.cuda.get_device_name(0)
            vram_gb = round(torch.cuda.get_device_properties(0).total_memory / (1024 ** 3), 2)
    except ImportError:
        pass

    f5_installed = False
    try:
        import f5_tts  # type: ignore
        f5_installed = True
    except ImportError:
        pass

    xtts_installed = False
    try:
        from TTS.api import TTS  # type: ignore
        xtts_installed = True
    except ImportError:
        pass

    model_available = f5_installed or xtts_installed

    env_report = {
        "python_version": py_ver,
        "os_platform": os_info,
        "pytorch_installed": torch_installed,
        "cuda_available": cuda_available,
        "gpu_name": gpu_name,
        "vram_gb": vram_gb,
        "f5_tts_installed": f5_installed,
        "xtts_v2_installed": xtts_installed,
        "model_status": "MODEL_AVAILABLE" if model_available else "MODEL_UNAVAILABLE",
        "active_engine": "F5-TTS" if f5_installed else ("XTTS_v2" if xtts_installed else "EdgeTTS Fallback"),
    }

    return env_report


if __name__ == "__main__":
    report = inspect_voice_cloning_environment()
    print("[Voice Cloning Setup Inspector]")
    for k, v in report.items():
        print(f"  {k}: {v}")
