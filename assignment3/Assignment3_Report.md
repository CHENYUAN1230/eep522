# Camera setting
1. 檢查 GPU 記憶體配置 (Memory Split)
libcamera 需要足夠的連續記憶體空間。如果你的 /boot/firmware/config.txt 中沒有配置 cma，系統會無法開啟 DMA 裝置。

輸入 sudo nano /boot/firmware/config.txt（舊版系統路徑為 /boot/config.txt）。

確認是否有以下行（或將其調整為 256 或更高）：

Plaintext
dtoverlay=vc4-kms-v3d,cma-256
注意： 確保沒有 gpu_mem 的限制衝突。

2. 更新系統與核心
你的錯誤訊息中提到 libcamera 版本是 2026 年的版本，這表示你的軟體包非常新。請確保核心也是最新的，以匹配最新的 DMA 驅動：

Bash
sudo apt update
sudo apt full-upgrade
sudo reboot
3. 檢查使用者權限
如果你的帳號（yuanchen_eep522）不在正確的群組中，會因為無法讀取 /dev/dma_heap 而報錯。

執行以下指令將自己加入 video 和 render 群組：

Bash
sudo usermod -a -G video,render $USER
完成後必須登出再重新登入，或者直接重啟。

# use tailscale to transmit the video
tailscale file cp test.h264 thinkpadx1:

# make .h264 become .mp4
rpicam-vid -t 5000 --codec libav -o finals_test.mp4