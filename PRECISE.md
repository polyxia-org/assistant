Change this in `sudo vi /etc/asound.conf` file:

```
pcm.!default {
        type plug
        slave {
                pcm "plughw:2,0"
                channels 2
                rate 48000
        }
        hint.description "USB Headset"
}
```