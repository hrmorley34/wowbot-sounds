# wowbot-sounds

Sounds for wowbot

## Normalise command

```bash
ffmpeg-normalize "source.ext" -o "dest.opus" -c:a libopus -f -nt peak -t -1
# or for multiple
EXT=wav
for f in *."$EXT"; do
    ffmpeg-normalize "$f" -o "audio/dest/${f%.${EXT}}.opus" -c:a libopus -f -nt peak -t -1
done
```
