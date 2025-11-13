# Network GPU Setup: Windows 11 → Ubuntu Linux

**Setup**: RTX 4090 on Windows 11 Pro → Ubuntu dev machine (same WiFi)
**Time**: 15-20 minutes
**Result**: Ubuntu can generate images via Windows GPU

---

## 🚀 Quick Start (Windows 11 Side)

### Step 1: Find Windows PC IP Address (1 min)

```powershell
# Open PowerShell and run:
ipconfig

# Look for "Wireless LAN adapter Wi-Fi" section:
# IPv4 Address. . . . . . . . . . . : 192.168.1.XXX
```

**Example output**:
```
Wireless LAN adapter Wi-Fi:
   IPv4 Address. . . . . . . . . . . : 192.168.1.105
```

📝 **Note this IP** - you'll use it on Ubuntu side

---

### Step 2: Install ComfyUI on Windows (5 min)

**Option A: Portable Version** (Recommended - easiest)

1. Download portable version:
   - Visit: https://github.com/comfyanonymous/ComfyUI/releases
   - Download: `ComfyUI_windows_portable_nvidia_cu121_or_cpu.7z`

2. Extract to `C:\` (creates `C:\ComfyUI_windows_portable\`)

3. Done! Includes Python + all dependencies

**Folder structure**:
```
C:\ComfyUI_windows_portable\
├── ComfyUI\              ← Main folder
│   ├── models\
│   │   └── checkpoints\  ← Models go here
│   ├── output\           ← Generated images
│   └── main.py
├── python_embeded\       ← Python installation
└── run_nvidia_gpu.bat    ← Startup script
```

**Option B: Manual Install**

```powershell
# Open PowerShell as Administrator

# Create directory
cd C:\
mkdir ComfyUI
cd ComfyUI

# Clone repository
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install PyTorch with CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install dependencies
pip install -r requirements.txt
```

---

### Step 3: Download Flux Schnell Model (10 min - 23.8GB)

**IMPORTANT**: This model requires Hugging Face authentication.

**Step 3.1: Setup Hugging Face Access** (2 min - first time only)

1. **Create account**: Go to https://huggingface.co/join
2. **Accept model terms**: Visit https://huggingface.co/black-forest-labs/FLUX.1-schnell and click "Agree and access repository"
3. **Create access token**:
   - Go to https://huggingface.co/settings/tokens
   - Click "New token"
   - Name: `comfyui-download`
   - Type: **Read**
   - Click "Generate a token"
   - **Copy the token** (starts with `hf_...`)

**Step 3.2: Download Model with Authentication**

```powershell
# Set your Hugging Face token (replace with YOUR token from above)
$env:HF_TOKEN = "hf_YOUR_TOKEN_HERE"

# Navigate to models directory
# For PORTABLE version:
cd C:\ComfyUI_windows_portable\ComfyUI\models\checkpoints

# For MANUAL install:
# cd C:\ComfyUI\ComfyUI\models\checkpoints

# Download with authentication
$headers = @{Authorization="Bearer $env:HF_TOKEN"}
Invoke-WebRequest -Uri "https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/flux1-schnell.safetensors" -OutFile "flux1-schnell.safetensors" -Headers $headers

# Verify download completed (should show ~23.8GB)
dir flux1-schnell.safetensors
```

**Alternative: Browser Download**
1. Visit: https://huggingface.co/black-forest-labs/FLUX.1-schnell/tree/main
2. Click on `flux1-schnell.safetensors`
3. Click "Download" button (must be logged in)
4. Move to: `C:\ComfyUI_windows_portable\ComfyUI\models\checkpoints\`

**Download time**: ~5-10 minutes depending on internet speed

---

### Step 4: Open Windows Firewall (2 min)

**CRITICAL**: Allow ComfyUI through Windows Firewall

```powershell
# Open PowerShell as Administrator

# Add firewall rule for ComfyUI
New-NetFirewallRule -DisplayName "ComfyUI API" -Direction Inbound -LocalPort 8188 -Protocol TCP -Action Allow

# Verify rule was created
Get-NetFirewallRule -DisplayName "ComfyUI API"
```

**Alternative: GUI Method**

1. Open Windows Defender Firewall
2. Click "Advanced settings"
3. Click "Inbound Rules" → "New Rule"
4. Choose "Port" → Next
5. Enter port `8188` → Next
6. Allow the connection → Next
7. Apply to all profiles → Next
8. Name: "ComfyUI API" → Finish

---

### Step 5: Start ComfyUI with Network Access (1 min)

```powershell
# For PORTABLE version:
cd C:\ComfyUI_windows_portable
.\run_nvidia_gpu.bat --listen 0.0.0.0 --port 8188

# For MANUAL install:
cd C:\ComfyUI\ComfyUI
.\venv\Scripts\activate
python main.py --listen 0.0.0.0 --port 8188
```

**Expected output**:
```
To see the GUI go to: http://0.0.0.0:8188
Starting server
To see the GUI go to: http://192.168.1.105:8188
```

📝 **Leave this PowerShell window open** - this keeps ComfyUI running

---

### Step 6: Test Local Access (1 min)

Open browser on Windows PC and visit:
```
http://localhost:8188
```

You should see the ComfyUI interface. If not:
- Check if server is still running in PowerShell
- Look for error messages in PowerShell output

---

## 🐧 Ubuntu Linux Side

### Step 7: Test Network Connection from Ubuntu (2 min)

```bash
# Replace 192.168.1.105 with YOUR Windows IP from Step 1
export GPU_IP="192.168.1.105"

# Test 1: Ping Windows PC
ping -c 3 $GPU_IP

# Test 2: Check if port 8188 is accessible
curl http://$GPU_IP:8188/system_stats

# Test 3: Check queue status
curl http://$GPU_IP:8188/queue
```

**Expected output for Test 2**:
```json
{
  "system": {
    "os": "nt",
    "python_version": "3.11.9",
    "embedded_python": true
  },
  "devices": [
    {
      "name": "NVIDIA GeForce RTX 4090",
      "type": "cuda",
      "index": 0,
      "vram_total": 25757220864,
      "vram_free": 25090842624,
      "torch_vram_total": 25757220864,
      "torch_vram_free": 24900812800
    }
  ]
}
```

✅ If you see JSON output with RTX 4090 info → **Connection successful!**

❌ If connection fails, see troubleshooting section below

---

### Step 8: Update DesignForge Config (2 min)

```bash
cd /home/samuel/repos/design-forge

# Edit config file
nano config/models.yaml
```

**Add local GPU configuration** (add at top of `models:` section):

```yaml
models:
  # Local GPU (Primary - FREE)
  local_gpu:
    enabled: true
    provider: "comfyui"
    api_url: "http://192.168.1.105:8188"  # YOUR WINDOWS IP HERE
    model: "flux-schnell"
    cost_per_generation: 0.0002  # Electricity only
    rate_limiting:
      concurrent_requests: 5  # RTX 4090 can handle ~5 parallel
      requests_per_minute: 100
    timeout_seconds: 60

  # Replicate (Emergency Fallback)
  flux:
    enabled: false  # DISABLED by default
    provider: "replicate"
    model_id: "black-forest-labs/flux-schnell"
    api_key: "${REPLICATE_API_KEY}"
    cost_per_generation: 0.003
```

**Update budget section**:

```yaml
budget:
  monthly_limit_usd: 1.00  # DOWN FROM $60
  alert_thresholds:
    - threshold: 0.50  # 50% = $0.50
      action: "log_warning"
    - threshold: 0.80  # 80% = $0.80
      action: "send_alert"
    - threshold: 1.00  # 100% = $1.00
      action: "disable_generation"
```

Save and exit (Ctrl+X, Y, Enter)

---

### Step 9: Test Generation from Ubuntu (2 min)

```bash
cd /home/samuel/repos/design-forge

# Create quick test script
cat > test_gpu.py << 'PYTHON'
import asyncio
import aiohttp
import json

async def test_generation():
    gpu_url = "http://192.168.1.105:8188"  # YOUR IP
    
    # Simple workflow for text-to-image
    workflow = {
        "prompt": {
            "1": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": "flux1-schnell.safetensors"}
            },
            "2": {
                "class_type": "CLIPTextEncode",
                "inputs": {"text": "a red cube on a blue sphere", "clip": ["1", 1]}
            },
            "3": {
                "class_type": "KSampler",
                "inputs": {
                    "seed": 42,
                    "steps": 4,
                    "cfg": 1.0,
                    "sampler_name": "euler",
                    "scheduler": "simple",
                    "denoise": 1.0,
                    "model": ["1", 0],
                    "positive": ["2", 0],
                    "negative": ["2", 0],
                    "latent_image": ["4", 0]
                }
            },
            "4": {
                "class_type": "EmptyLatentImage",
                "inputs": {"width": 512, "height": 512, "batch_size": 1}
            },
            "5": {
                "class_type": "VAEDecode",
                "inputs": {"samples": ["3", 0], "vae": ["1", 2]}
            },
            "6": {
                "class_type": "SaveImage",
                "inputs": {"filename_prefix": "test", "images": ["5", 0]}
            }
        }
    }
    
    async with aiohttp.ClientSession() as session:
        # Submit workflow
        async with session.post(f"{gpu_url}/prompt", json={"prompt": workflow}) as resp:
            result = await resp.json()
            print(f"✅ Generation started: {result}")
            return result.get("prompt_id")

if __name__ == "__main__":
    asyncio.run(test_generation())
PYTHON

# Run test
python test_gpu.py
```

**Expected output**:
```
✅ Generation started: {'prompt_id': '12345-abcd-6789-efgh', 'number': 1}
```

**Image will be saved on Windows PC** at:
```
# For PORTABLE version:
C:\ComfyUI_windows_portable\ComfyUI\output\test_00001_.png

# For MANUAL install:
C:\ComfyUI\ComfyUI\output\test_00001_.png
```

---

## ✅ Verification Checklist

After setup, verify:

- [ ] Windows IP address noted (e.g., 192.168.1.105)
- [ ] ComfyUI installed (portable: `C:\ComfyUI_windows_portable\` or manual: `C:\ComfyUI\`)
- [ ] Hugging Face account created and model terms accepted
- [ ] Flux Schnell model downloaded (23.8GB in `ComfyUI\models\checkpoints\`)
- [ ] Windows Firewall rule added for port 8188
- [ ] ComfyUI running with `--listen 0.0.0.0 --port 8188`
- [ ] Ubuntu can ping Windows PC
- [ ] Ubuntu can curl `http://[WINDOWS_IP]:8188/system_stats`
- [ ] `config/models.yaml` updated with Windows IP
- [ ] Test generation succeeds from Ubuntu

---

## 🔧 Troubleshooting

### Problem 1: Connection Refused from Ubuntu

**Symptoms**: `curl: (7) Failed to connect to 192.168.1.105 port 8188: Connection refused`

**Solutions**:

1. **Check ComfyUI is running on Windows**
   ```powershell
   # On Windows: Check if ComfyUI process is running
   Get-Process | Where-Object {$_.ProcessName -like "*python*"}
   ```

2. **Verify Windows Firewall rule**
   ```powershell
   # On Windows: Check firewall rule exists
   Get-NetFirewallRule -DisplayName "ComfyUI API"
   
   # If not found, create it:
   New-NetFirewallRule -DisplayName "ComfyUI API" -Direction Inbound -LocalPort 8188 -Protocol TCP -Action Allow
   ```

3. **Test local access on Windows first**
   - Open browser on Windows: `http://localhost:8188`
   - If this works but network doesn't, it's a firewall issue

4. **Check correct IP address**
   ```powershell
   # On Windows: Verify IP hasn't changed
   ipconfig | findstr "IPv4"
   ```

### Problem 2: "Model not found" Error

**Symptoms**: Error about missing `flux1-schnell.safetensors`

**Solution**:
```powershell
# On Windows: Verify model file exists
# For PORTABLE version:
dir C:\ComfyUI_windows_portable\ComfyUI\models\checkpoints\flux1-schnell.safetensors

# For MANUAL install:
# dir C:\ComfyUI\ComfyUI\models\checkpoints\flux1-schnell.safetensors

# Should show file size: ~23.8 GB
# If missing, re-download from Step 3 (requires Hugging Face authentication)
```

### Problem 3: Out of Memory Error

**Symptoms**: CUDA out of memory during generation

**Solution**:
```powershell
# On Windows: Close other GPU-heavy applications
# - Close games, video editing software, etc.
# - Restart ComfyUI
```

### Problem 4: Slow Generation Speed

**Symptoms**: Takes >10 seconds per image

**Solutions**:

1. **First generation is always slow** (model loading)
   - Cold start: 15-20 seconds
   - Subsequent: 1-2 seconds
   
2. **Check GPU is being used**
   ```powershell
   # On Windows: Monitor GPU usage
   nvidia-smi
   # Should show ~20GB VRAM usage during generation
   ```

3. **Reduce concurrent requests**
   - Edit `config/models.yaml`: `concurrent_requests: 1`
   - RTX 4090 can handle 3-5 concurrent, but start with 1

### Problem 5: Windows IP Address Changes

**Symptoms**: Connection works, then stops working later

**Solution**: Set static IP on Windows

```powershell
# On Windows: Set static IP (example)
# 1. Open Settings → Network & Internet → WiFi
# 2. Click your WiFi network properties
# 3. Click "Edit" next to IP assignment
# 4. Change from "Automatic (DHCP)" to "Manual"
# 5. Enable IPv4
# 6. Set:
#    IP address:     192.168.1.105 (your current IP)
#    Subnet mask:    255.255.255.0 (FULL format - NOT "24")
#    Gateway:        192.168.1.1 (your router)
#    Preferred DNS:  8.8.8.8 (Google DNS)
#    Alternate DNS:  8.8.4.4 (Google DNS backup)
#
# IMPORTANT: Use full subnet mask 255.255.255.0 (NOT prefix "24")
#            Windows 11 will show "Invalid entry" if you use prefix format
```

---

## 🔄 Auto-Start ComfyUI on Windows Boot (Optional)

To avoid manually starting ComfyUI each time:

### Method 1: Task Scheduler (Recommended)

1. Open Task Scheduler on Windows
2. Create Basic Task → Name: "ComfyUI AutoStart"
3. Trigger: "When I log on"
4. Action: "Start a program"
5. **For PORTABLE**:
   - Program: `C:\ComfyUI_windows_portable\run_nvidia_gpu.bat`
   - Arguments: `--listen 0.0.0.0 --port 8188`
6. **For MANUAL**:
   - Program: `C:\ComfyUI\ComfyUI\venv\Scripts\python.exe`
   - Arguments: `main.py --listen 0.0.0.0 --port 8188`
   - Start in: `C:\ComfyUI\ComfyUI`
7. Finish

### Method 2: Startup Folder

```powershell
# For PORTABLE version:
$script = @"
cd C:\ComfyUI_windows_portable
.\run_nvidia_gpu.bat --listen 0.0.0.0 --port 8188
"@

# For MANUAL install:
# $script = @"
# cd C:\ComfyUI\ComfyUI
# .\venv\Scripts\activate
# python main.py --listen 0.0.0.0 --port 8188
# "@

$script | Out-File -FilePath "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\start_comfyui.bat"
```

---

## 📊 Network Performance Expectations

| Metric | Over WiFi | Over Ethernet | Notes |
|--------|-----------|---------------|-------|
| **Latency** | 5-10ms | 1-2ms | Minimal impact on generation |
| **Transfer (512x512)** | 50-100ms | 10-20ms | Image download from Windows |
| **Transfer (1024x1024)** | 200-400ms | 50-100ms | Larger images take longer |
| **Total per image** | 1.5-2.5s | 1.2-1.5s | Includes generation + transfer |

**Recommendation**: WiFi is fine for development. Ethernet only needed if generating 100+ images/minute.

---

## 🎯 Next Steps After Setup

Once setup is complete:

1. **Keep Windows PC powered on** during development
2. **Update `.env` file** (if needed):
   ```bash
   echo "LOCAL_GPU_URL=http://192.168.1.105:8188" >> .env
   ```

3. **Test with MultiBackendClient**:
   ```python
   from src.generation.multi_backend_client import MultiBackendClient
   
   client = MultiBackendClient(
       local_gpu_enabled=True,
       local_gpu_url="http://192.168.1.105:8188"
   )
   
   result = await client.generate("a test logo")
   print(f"Generated in {result.generation_time}s for ${result.cost}")
   ```

4. **Monitor costs**:
   ```bash
   cat results/cost-tracking.json
   ```

---

## 💰 Cost Verification

After generating 10 test images:

```bash
# Check cost tracking
cat results/cost-tracking.json

# Should show:
# {
#   "total_generations": 10,
#   "total_cost": 0.002,  # $0.0002 × 10
#   "backend_stats": {
#     "local_gpu": {"count": 10, "cost": 0.002}
#   }
# }
```

**Verify**: 10 images = $0.002 (not $0.03 which would be Replicate)

---

## ✅ Setup Complete!

You now have:
- ✅ RTX 4090 running ComfyUI on Windows 11
- ✅ Network access from Ubuntu over WiFi
- ✅ Cost tracking showing $0.0002/image
- ✅ Can generate 4,900 images/month for <$1

**Monthly cost**: $0.25 for Epic #11 (1,250 images) vs $3.75 with Replicate

**Ready to continue Feature #2.3!**
