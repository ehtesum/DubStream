"""
Voice cloning environment detector and setup script for DubStream v2.0.

Detects Python version, PyTorch CUDA capability, F5-TTS / XTTS v2 package availability,
model initialization status, and reports exact setup status without auto-downloading large weights during boot.
"""
import sys
import platform
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

    # Status classification: MODEL_NOT_INSTALLED, MODEL_INSTALLED, MODEL_INITIALIZATION_FAILED, MODEL_READY
    if not (f5_installed or xtts_installed):
        status = "MODEL_NOT_INSTALLED"
    else:
        # Check if initialization works
        try:
            from voices.cloning import NeuralVoiceCloningEngine
            engine = NeuralVoiceCloningEngine()
            if engine.f5.model or engine.xtts.model:
                status = "MODEL_READY"
            else:
                status = "MODEL_INSTALLED"
        except Exception:
            status = "MODEL_INITIALIZATION_FAILED"

    env_report = {
        "python_version": py_ver,
        "os_platform": os_info,
        "pytorch_installed": torch_installed,
        "cuda_available": cuda_available,
        "gpu_name": gpu_name,
        "vram_gb": vram_gb,
        "f5_tts_installed": f5_installed,
        "xtts_v2_installed": xtts_installed,
        "model_status": status,
        "active_engine": "F5-TTS" if f5_installed else ("XTTS_v2" if xtts_installed else "EdgeTTS Fallback"),
    }

    return env_report


if __name__ == "__main__":
    report = inspect_voice_cloning_environment()
    print("[Voice Cloning Setup Inspector]")
    for k, v in report.items():
        print(f"  {k}: {v}")
