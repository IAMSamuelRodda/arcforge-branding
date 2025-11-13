# Local GPU Setup Guide (RTX 4090)

**Purpose**: Configure your RTX 4090 PC to run ComfyUI API for free, fast image generation.

**Cost Savings**: ~$28 for 10,000 images (93% reduction vs Replicate)

---

## Prerequisites

- **Hardware**: NVIDIA RTX 4090 (24GB VRAM)
- **OS**: Windows or Linux
- **Python**: 3.10 or 3.11 (NOT 3.12+)
- **Disk Space**: ~50GB for ComfyUI + models
- **Network**: Same network as development machine

---

## Quick Start (10-15 minutes)

### Step 1: Install ComfyUI

**Windows:**
```powershell
# Create directory
cd C:\
mkdir ComfyUI
cd ComfyUI

# Download ComfyUI portable (includes Python + dependencies)
# Visit: https://github.com/comfyanonymous/ComfyUI/releases
# Download: ComfyUI_windows_portable_nvidia_cu121_or_cpu.7z
# Extract to C:\ComfyUI

# OR install manually with git
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
python -m venv venv
venv\Scripts\activate
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt
```

**Linux:**
```bash
# Install system dependencies
sudo apt update
sudo apt install -y python3.11 python3.11-venv git wget

# Clone ComfyUI
cd ~
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install PyTorch with CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install ComfyUI dependencies
pip install -r requirements.txt
```

### Step 2: Download Models

**Flux Schnell** (Recommended - fast, high quality, 23.8GB):
```bash
cd ComfyUI/models/checkpoints

# Using wget (Linux/WSL)
wget https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/flux1-schnell.safetensors

# OR using curl
curl -L -o flux1-schnell.safetensors https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/flux1-schnell.safetensors

# OR download manually from:
# https://huggingface.co/black-forest-labs/FLUX.1-schnell/tree/main
# Save to: ComfyUI/models/checkpoints/flux1-schnell.safetensors
```

**Optional: SD 3.5 Large** (Slower, alternative, 9.8GB):
```bash
cd ComfyUI/models/checkpoints

# Download from Stability AI (requires Hugging Face account)
wget --header="Authorization: Bearer YOUR_HF_TOKEN" \
  https://huggingface.co/stabilityai/stable-diffusion-3.5-large/resolve/main/sd3.5_large.safetensors
```

### Step 3: Start ComfyUI API Server

**Windows:**
```powershell
cd C:\ComfyUI
# If using portable version:
.\run_nvidia_gpu.bat --listen 0.0.0.0 --port 8188

# If manual install:
venv\Scripts\activate
python main.py --listen 0.0.0.0 --port 8188
```

**Linux:**
```bash
cd ~/ComfyUI
source venv/bin/activate
python main.py --listen 0.0.0.0 --port 8188
```

**Output (successful start):**
```
Total VRAM 24564 MB, total RAM 32768 MB
pytorch version: 2.1.2+cu121
Set vram state to: NORMAL_VRAM
Device: cuda:0 NVIDIA GeForce RTX 4090 : cudaMallocAsync
VAE dtype: torch.bfloat16

Starting server
To see the GUI go to: http://0.0.0.0:8188
```

**Keep this terminal open!** ComfyUI must run continuously.

### Step 4: Find Your 4090 PC's IP Address

**Windows:**
```powershell
ipconfig
# Look for "IPv4 Address" under your network adapter
# Example: 192.168.1.100
```

**Linux:**
```bash
ip addr show
# Look for inet under eth0 or wlan0
# Example: 192.168.1.100
```

### Step 5: Test Connection from Dev Machine

**From your development machine** (this device):
```bash
# Test connectivity (replace with your 4090 PC IP)
curl http://192.168.1.100:8188/system_stats

# Expected output:
# {"system":{"os":"Linux","python_version":"3.11.5", ...}}
```

**If connection fails:**
- Check firewall on 4090 PC (allow port 8188)
- Verify both devices on same network
- Try accessing from browser: `http://192.168.1.100:8188`

---

## Usage with DesignForge

### Configuration

**Option 1: Environment Variables** (Recommended)
```bash
# Add to ~/.bashrc or project .env
export LOCAL_GPU_URL="http://192.168.1.100:8188"
export LOCAL_GPU_MODEL="flux-schnell"
export REPLICATE_API_TOKEN="r8_..."  # Fallback
```

**Option 2: Direct in Code**
```python
from generation import MultiBackendClient

client = MultiBackendClient(
    local_gpu_enabled=True,
    local_gpu_url="http://192.168.1.100:8188",
    local_gpu_model="flux-schnell",
    replicate_token="r8_...",  # Fallback
    prefer_local=True,  # Try local GPU first
)
```

### Example Usage

```python
import asyncio
from generation import MultiBackendClient, GenerationRequest

async def main():
    async with MultiBackendClient(
        local_gpu_url="http://192.168.1.100:8188",
        replicate_token="r8_...",
        budget_limit=60.0
    ) as client:
        # Generate single image
        result = await client.generate("A minimalist logo design")

        if result.success:
            client.save_image(result, Path("output.png"))
            print(f"✓ Generated in {result.generation_time:.2f}s")
            print(f"  Cost: ${result.cost:.4f}")

        # Generate batch
        requests = [
            GenerationRequest(
                prompt_id=f"prompt_{i}",
                prompt_text=f"Design variation {i}"
            )
            for i in range(10)
        ]

        results, stats = await client.generate_batch(requests)

        print(f"\n📊 Results:")
        print(f"   Successful: {stats.successful}/{stats.total_requests}")
        print(f"   Total cost: ${stats.total_cost:.2f}")
        print(f"   Avg time: {stats.avg_generation_time:.2f}s")

asyncio.run(main())
```

**Expected output:**
```
Generating 10 images [local (✓), replicate (✓)]...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:15

📊 Backend Statistics:

   LOCAL:
   • Requests: 10/10 (100.0% success)
   • Total cost: $0.0020
   • Avg time: 1.5s

   REPLICATE:
   • Requests: 0/0 (0.0% success)
   • Total cost: $0.0000
   • Avg time: 0.0s
```

---

## Performance Benchmarks (RTX 4090)

### Flux Schnell
- **First generation**: 3-5s (model loading)
- **Subsequent**: 1-2s per image
- **Batch of 10**: ~15-20s total (parallel loading)
- **Quality**: High (comparable to Replicate)

### SD 3.5 Large
- **First generation**: 5-8s (model loading)
- **Subsequent**: 3-4s per image
- **Quality**: Excellent (state-of-the-art)

### Cost Comparison

| Volume | Local (4090) | Replicate Flux | Savings |
|--------|--------------|----------------|---------|
| 100 images | $0.02 | $0.30 | $0.28 (93%) |
| 1,000 images | $0.20 | $3.00 | $2.80 (93%) |
| 10,000 images | $2.00 | $30.00 | $28.00 (93%) |

*Local costs are electricity only (~$0.0002/image)*

---

## Troubleshooting

### Issue: "Connection refused" from dev machine

**Solutions:**
1. **Firewall**: Allow port 8188
   - Windows: `netsh advfirewall firewall add rule name="ComfyUI" dir=in action=allow protocol=TCP localport=8188`
   - Linux: `sudo ufw allow 8188`

2. **Verify ComfyUI is running**:
   ```bash
   # On 4090 PC
   curl http://localhost:8188/system_stats
   ```

3. **Check network**:
   ```bash
   # From dev machine
   ping 192.168.1.100
   ```

### Issue: "CUDA out of memory"

**Solutions:**
1. Reduce batch size in ComfyUI
2. Close other GPU applications
3. Restart ComfyUI to clear VRAM

### Issue: "Model not found"

**Solutions:**
1. Verify model file exists:
   ```bash
   ls -lh ComfyUI/models/checkpoints/
   ```

2. Check model name matches:
   - File: `flux1-schnell.safetensors`
   - Code: `local_gpu_model="flux-schnell"`

3. Re-download model if corrupted

### Issue: Slow generation (>10s)

**Possible causes:**
1. **First generation**: Models loading (normal)
2. **CPU fallback**: Check CUDA is working:
   ```python
   import torch
   print(torch.cuda.is_available())  # Should be True
   print(torch.cuda.get_device_name(0))  # Should be "NVIDIA GeForce RTX 4090"
   ```
3. **Wrong PyTorch**: Reinstall with CUDA support:
   ```bash
   pip uninstall torch torchvision torchaudio
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
   ```

### Issue: Backend keeps failing over to Replicate

**Debug:**
```python
from generation import LocalGPUBackend

backend = LocalGPUBackend(api_url="http://192.168.1.100:8188")

# Test availability
is_available = await backend.is_available()
print(f"Local GPU available: {is_available}")

# Test generation
try:
    image_bytes, time = await backend.generate("test prompt")
    print(f"✓ Generation successful in {time:.2f}s")
except Exception as e:
    print(f"✗ Generation failed: {e}")
```

---

## Production Recommendations

### 1. Run ComfyUI as a Service

**Windows (Task Scheduler):**
- Create task that runs `C:\ComfyUI\run_nvidia_gpu.bat --listen 0.0.0.0 --port 8188` on startup
- Run whether user is logged in or not

**Linux (systemd):**
```bash
sudo nano /etc/systemd/system/comfyui.service
```

```ini
[Unit]
Description=ComfyUI API Server
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/home/your_username/ComfyUI
ExecStart=/home/your_username/ComfyUI/venv/bin/python main.py --listen 0.0.0.0 --port 8188
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable comfyui
sudo systemctl start comfyui
sudo systemctl status comfyui
```

### 2. Static IP for 4090 PC

Configure router to assign static IP (e.g., 192.168.1.100) to prevent address changes.

### 3. Monitor GPU Usage

**Windows:**
```powershell
nvidia-smi -l 1  # Update every second
```

**Linux:**
```bash
watch -n 1 nvidia-smi
```

### 4. Optimize for 24/7 Operation

- Enable GPU temperature monitoring
- Set power limit if thermal throttling occurs:
  ```bash
  sudo nvidia-smi -pl 400  # Limit to 400W (default: 450W)
  ```
- Use UPS for power stability

---

## Advanced: Multiple Models

To support multiple models simultaneously, download additional checkpoints:

```bash
cd ComfyUI/models/checkpoints

# Flux Schnell (fast, 4 steps)
wget https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/flux1-schnell.safetensors

# Flux Dev (higher quality, 20-50 steps)
wget https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/flux1-dev.safetensors

# SD 3.5 Large (alternative)
wget --header="Authorization: Bearer YOUR_HF_TOKEN" \
  https://huggingface.co/stabilityai/stable-diffusion-3.5-large/resolve/main/sd3.5_large.safetensors
```

Then switch models in code:
```python
client = MultiBackendClient(
    local_gpu_model="flux-dev",  # or "sd35"
    ...
)
```

---

## Next Steps

1. **Test local generation**: Run example above
2. **Benchmark performance**: Compare with Replicate
3. **Configure auto-start**: Set up systemd/Task Scheduler
4. **Monitor costs**: Track electricity usage
5. **Optimize workflows**: Batch overnight generations

---

## Support

- **ComfyUI Documentation**: https://github.com/comfyanonymous/ComfyUI
- **Model Downloads**: https://huggingface.co/black-forest-labs
- **CUDA Toolkit**: https://developer.nvidia.com/cuda-downloads

**Estimated Setup Time**: 15-30 minutes (plus model download time)

**First Generation**: May take 3-5 seconds (model loading)

**Subsequent Generations**: 1-2 seconds each 🚀
